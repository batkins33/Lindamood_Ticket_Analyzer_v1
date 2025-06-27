import logging
import os

import cv2
import easyocr
import numpy as np
import onnxruntime as ort
from PIL import Image
from PIL import ImageDraw
from paddleocr import PaddleOCR

from modular_analyzer.image_utils import inches_to_pixels, sanitize_box

ocr_readers = {}


def get_onnx_model_path(model_name: str = "handwriting_ocr.onnx") -> str:
    """
    Return the full filesystem path to the specified ONNX model.
    Ensure the file exists under modular_analyzer/models/.
    """
    path = os.path.join(os.path.dirname(__file__), "models", model_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"ONNX model not found at {path}. "
                                "Please place your model file there or update the path.")
    return path


def initialize_reader(backend: str = "paddleocr"):
    """
    Initialize an OCR/ICR reader based on the specified backend.
    Supported backends:
      - "paddleocr": printed/text via PaddleOCR
      - "onnxruntime": handwriting ICR via ONNXRuntime (>=1.9)
      - "torch": EasyOCR via PyTorch
    """
    backend = backend.lower()

    if backend == "paddleocr":
        reader = PaddleOCR(use_angle_cls=True, lang='en')
    elif backend == "onnxruntime":
        model_path = get_onnx_model_path("handwriting_ocr.onnx")
        providers = ort.get_available_providers()
        reader = ort.InferenceSession(model_path, providers=providers)
    elif backend == "torch":
        reader = easyocr.Reader(["en"], gpu=False)
    else:
        raise ValueError(
            f"Unsupported backend: '{backend}'. Choose 'paddleocr', 'onnxruntime', or 'torch'."
        )

    ocr_readers[backend] = reader
    return reader


def add_box_to_fields(fields_conf):
    """
    Add pixel box coordinates to each field configuration based on position and size in inches.
    Applies a defensive check to ensure config structure is valid.
    """
    for section_key, section in fields_conf.items():
        if isinstance(section, str):
            fields_conf[section_key] = {"raw_text": {"value": section}}
            logging.warning(f"🛑 Converted flat string field '{section_key}' to dict with 'raw_text' field")
            continue

        if not isinstance(section, dict):
            logging.warning(f"⚠️ Expected dict in section '{section_key}', but got {type(section).__name__}: {section}")
            continue

        for field_key, field in section.items():
            if (
                    isinstance(field, dict)
                    and "position_inches" in field
                    and "size_inches" in field
            ):
                field["box"] = inches_to_pixels(field["position_inches"], field["size_inches"])


def draw_boxes_on_image(img: Image.Image, fields: dict) -> Image.Image:
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size

    for key, meta in fields.items():
        if "position_inches" in meta and "size_inches" in meta:
            box = inches_to_pixels(meta["position_inches"], meta["size_inches"])
            sanitized = sanitize_box(box, img_width, img_height)
            if sanitized is None:
                logging.error(f"❌ Invalid sanitized box for {key}: {box}")
                continue
            meta["box"] = sanitized
        elif "box" in meta:
            sanitized = sanitize_box(meta["box"], img_width, img_height)
            if sanitized is None:
                logging.error(f"❌ Invalid sanitized box for {key}: {meta['box']}")
                continue
        else:
            logging.warning(f"⚠️ No box or dimensions found for {key}")
            continue

        color = meta.get("color", "red")
        line_width = meta.get("line_width", 3)
        draw.rectangle(sanitized, outline=color, width=line_width)

    return img


def ensure_region_array(region, field_name, page_num, entry):
    try:
        region_array = np.array(region)
        if region_array is None or region_array.size == 0:
            logging.error(f"❌ region_array is None or empty for {field_name} on page {page_num}")
            entry[field_name] = "REGION_ARRAY_INVALID"
            return None
        return region_array
    except Exception as e:
        logging.exception(f"❌ Failed to convert region to array for {field_name} on page {page_num}: {e}")
        entry[field_name] = "REGION_ARRAY_ERROR"
        return None


def read_text(image, backend="paddleocr"):
    if image is None:
        raise ValueError("read_text received None image array")
    if not isinstance(image, np.ndarray):
        raise TypeError(f"read_text expected np.ndarray, got {type(image)}")
    if image.ndim not in (2, 3):
        raise ValueError(f"read_text received invalid image dimensions: {image.shape}")

    backend = backend.lower()
    reader = ocr_readers.setdefault(backend, initialize_reader(backend))

    if backend == "paddleocr":
        return reader.ocr(image, cls=True)

    elif backend == "onnxruntime":
        from modular_analyzer.image_preprocessing import preprocess_for_onnx
        img = preprocess_for_onnx(image)

        input_name = reader.get_inputs()[0].name
        pred = reader.run(None, {input_name: img})[0]

        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        text = "".join([chars[i] for i in np.argmax(pred, axis=2)[0] if i < len(chars)])
        return [(None, [(None, text, 0.99)])]

    elif backend == "torch":
        return reader.readtext(image)

    raise ValueError(f"Unsupported backend: {backend}")


def detect_handwriting(img):
    if isinstance(img, Image.Image):
        img = np.array(img.convert("L"))
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 150)
    edge_density = np.sum(edges > 0) / edges.size
    stddev = np.std(img)
    return edge_density > 0.02 or stddev > 50


def is_handwriting_deep(img: Image.Image) -> bool:
    """
    Use a trained ONNX classifier to detect handwritten vs printed.
    Returns True if handwriting.
    """
    from modular_analyzer.image_preprocessing import preprocess_for_handwriting_classification

    model_path = get_onnx_model_path("handwriting_classifier.onnx")
    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    img_arr = preprocess_for_handwriting_classification(np.array(img))
    if img_arr is None:
        logging.error("❌ Image preprocessing failed: preprocess_for_handwriting_classification returned None")
        return False  # fallback to non-handwriting

    try:
        preds = session.run([output_name], {input_name: img_arr})[0]
        return bool(preds[0][0] > 0.5)
    except Exception as e:
        logging.exception(f"❌ ONNX handwriting classifier failed: {e}")
        return False


def template_match(img_region, template_path, threshold=0.7):
    template = cv2.imread(template_path, 0)
    if template is None:
        raise FileNotFoundError(f"Template image not found: {template_path}")
    img_np = np.array(img_region.convert("L"))
    res = cv2.matchTemplate(img_np, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return (max_val >= threshold), max_loc


def extract_text_fields(img: Image.Image, reader, backend: str = "paddleocr") -> list:
    """
    Extract text fields from an image using OCR.
    Returns a list of tuples with (bbox, text, confidence).
    """
    region_array = np.array(img.convert("RGB"))
    return read_text(reader, region_array, backend=backend)

import logging
import os

from modular_analyzer.file_utils import load_yaml

import cv2
import numpy as np
from modular_analyzer.file_utils import find_file_case_insensitive
from modular_analyzer.image_utils import save_crop_and_thumbnail, save_field, sanitize_box
from modular_analyzer.ocr_utils import (
    initialize_reader,
    read_text,
    detect_handwriting,
    is_handwriting_deep,
    template_match,
    ensure_region_array
)
from modular_analyzer.types import PageTask

# Load OCR configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "configs", "ocr_config.yaml")
OCR_CONFIG = load_yaml(CONFIG_PATH) if os.path.exists(CONFIG_PATH) else {}
USE_ONNX_FALLBACK = OCR_CONFIG.get("use_onnx_fallback", True)

logger = logging.getLogger(__name__)

def simplify_field_name(field_name: str) -> str:
    return field_name.split(".")[-1]


def process_page(task: PageTask):
    import time

    page_idx = task.page_idx
    img = task.img
    fields = task.fields
    output_dir = task.output_dir

    reader_std = initialize_reader("doctr")
    reader_hand = initialize_reader("onnxruntime") if USE_ONNX_FALLBACK else None

    page_num = page_idx + 1
    crops_dir = os.path.join(output_dir, "crops")
    thumbnails_dir = os.path.join(output_dir, "thumbnails")
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(crops_dir, exist_ok=True)
    os.makedirs(thumbnails_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    entry = {"Page": page_num}
    ticket_issue = ""
    thumbnail_log = []
    issue_log = []

    def log_issue(issue_type: str, field: str):
        issue_log.append({
            "Page": page_num,
            "IssueType": issue_type,
            "FieldName": field,
        })

    logging.info(f"📄 Processing page {page_num}")
    start_time = time.time()

    for field_name, field_conf in fields.items():
        short_name = simplify_field_name(field_name)

        if "box" not in field_conf:
            logging.warning(f"⚠️ Field '{field_name}' missing 'box', skipping.")
            log_issue("MISSING_BOX", field_name)
            continue

        box = sanitize_box(field_conf["box"], *img.size)
        if box is None:
            logging.error(f"❌ Invalid sanitized box for {field_name} on page {page_num}: {field_conf['box']}")
            entry[field_name] = "BOX_INVALID"
            log_issue("BOX_INVALID", field_name)
            continue

        region = img.crop(box)
        if region is None:
            logging.error(f"❌ Cropped region is None for {field_name} on page {page_num}")
            entry[field_name] = "REGION_NONE"
            log_issue("REGION_NONE", field_name)
            continue

        region_array = ensure_region_array(region, field_name, page_num, entry)
        if region_array is None:
            log_issue("REGION_ARRAY_NONE", field_name)
            continue
        if not isinstance(region_array, np.ndarray):
            logging.error(f"❌ region_array is not ndarray for {field_name} on page {page_num}")
            entry[field_name] = "INVALID_ARRAY_TYPE"
            log_issue("INVALID_ARRAY_TYPE", field_name)
            continue
        if region_array.size == 0:
            logging.error(f"❌ region_array is empty for {field_name} on page {page_num}")
            entry[field_name] = "EMPTY_ARRAY"
            log_issue("EMPTY_ARRAY", field_name)
            continue

        if "ticket_number" in field_name:
            try:
                region_bgr = cv2.cvtColor(region_array, cv2.COLOR_RGB2BGR)
            except Exception as e:
                logging.error(f"❌ cvtColor failed for {field_name} on page {page_num}: {e}")
                entry[field_name] = "CVTCOLOR_FAIL"
                continue

            if region_bgr is None or not isinstance(region_bgr, np.ndarray):
                logging.error(f"❌ region_bgr is None or invalid for {field_name} on page {page_num}")
                entry[field_name] = "BGR_INVALID"
                continue

            texts = read_text(region_bgr, backend="doctr")
            if texts:
                entry[field_name] = texts[0][1]
                logging.info(f"✅ Found ticket number: {texts[0][1]} on page {page_num}")
            else:
                logging.warning(f"❌ Ticket number missing on page {page_num}, trying template match.")
                template_path = find_file_case_insensitive("ticket_template.jpg", "modular_analyzer/templates")
                if template_path:
                    matched, _ = template_match(region, template_path)
                    if matched:
                        entry[field_name] = "TemplateMatch"
                        logging.info(f"🔍 Template match succeeded for page {page_num}")
                    else:
                        entry[field_name] = "MISSING"
                        ticket_issue = "MISSING"
                        logging.error(f"❌ Ticket number not found by OCR or template match on page {page_num}")
                        log_issue("TICKET_MISSING", field_name)
                else:
                    entry[field_name] = "MISSING"
                    ticket_issue = "MISSING"
                    logging.error("🛑 Template file 'ticket_template.jpg' not found.")
                    log_issue("TEMPLATE_NOT_FOUND", field_name)

            save_crop_and_thumbnail(region, crops_dir, f"{short_name}_{page_num}", thumbnails_dir, thumbnail_log)
            continue

        try:
            is_handwritten = False
            if USE_ONNX_FALLBACK:
                is_handwritten = detect_handwriting(region) or is_handwriting_deep(region)
            text_value = None

            if is_handwritten and reader_hand is not None:
                from modular_analyzer.image_preprocessing import preprocess_for_onnx, decode_onnx_output

                region_for_onnx = region_array
                if region_for_onnx.ndim == 2 or region_for_onnx.shape[2] != 3:
                    region_for_onnx = cv2.cvtColor(region_for_onnx, cv2.COLOR_GRAY2BGR)
                    logging.warning(f"⚠️ Converted grayscale to BGR for {field_name} on page {page_num}")

                try:
                    preprocessed = preprocess_for_onnx(region_for_onnx)
                    preds = reader_hand.run(None, {reader_hand.get_inputs()[0].name: preprocessed})[0]
                    decoded = decode_onnx_output(preds)
                    if decoded:
                        text_value = decoded
                        logging.info(f"✍️ Handwritten field '{field_name}': {decoded}")
                    else:
                        logging.warning(f"⚠️ Handwriting OCR unreadable for: {field_name}")
                        log_issue("HANDWRITING_UNREADABLE", field_name)
                except Exception as e:
                    logging.error(f"❌ ONNX handwriting OCR failed for {field_name} on page {page_num}: {e}")
                    log_issue("HANDWRITING_ERROR", field_name)

            if text_value is None:
                try:
                    region_bgr = cv2.cvtColor(region_array, cv2.COLOR_RGB2BGR) if region_array.ndim == 3 else cv2.cvtColor(region_array, cv2.COLOR_GRAY2BGR)
                    texts = read_text(region_bgr, backend="doctr")
                    if texts:
                        text_value = texts[0][1]
                        logging.info(f"📝 Printed field '{field_name}': {text_value}")
                    else:
                        text_value = "TEXT_NOT_FOUND"
                        logging.warning(f"⚠️ Printed OCR failed for: {field_name}")
                except Exception as e:
                    text_value = "OCR_ERROR"
                    logging.error(f"❌ Printed OCR failed for {field_name} on page {page_num}: {e}")
                    entry[field_name] = "HANDWRITING_ERROR"
                    logging.error(f"❌ Exception while processing handwriting for {field_name} on page {page_num}: {e}")
                    log_issue("HANDWRITING_ERROR", field_name)

            entry[field_name] = text_value
            if is_handwritten:
                save_field(region, crops_dir, f"{short_name}_{page_num}")
                save_crop_and_thumbnail(region, crops_dir, f"{short_name}_{page_num}", thumbnails_dir, thumbnail_log)
            if USE_ONNX_FALLBACK and reader_hand is not None:
                logging.debug(f"🧪 Calling preprocess_for_onnx on shape={region_array.shape}, dtype={region_array.dtype}")
                try:
                    if not isinstance(region_array, np.ndarray) or region_array.ndim != 3:
                        raise ValueError(f"Invalid image shape: {getattr(region_array, 'shape', None)}")

                    if region_array.shape[2] != 3:
                        region_array = cv2.cvtColor(region_array, cv2.COLOR_GRAY2BGR)
                        logging.warning(f"⚠️ Converted grayscale to BGR for {field_name} on page {page_num}")

                    from modular_analyzer.image_preprocessing import preprocess_for_onnx, decode_onnx_output

                    preprocessed = preprocess_for_onnx(region_array)
                    preds = reader_hand.run(None, {reader_hand.get_inputs()[0].name: preprocessed})[0]
                    decoded = decode_onnx_output(preds)

                    if decoded:
                        entry[field_name] = decoded
                        logging.info(f"✍️ Handwritten field '{field_name}': {decoded}")
                    else:
                        entry[field_name] = "HANDWRITING_UNREADABLE"
                        logging.warning(f"⚠️ Handwriting OCR unreadable for: {field_name}")
                        log_issue("HANDWRITING_UNREADABLE", field_name)
                except Exception as e:
                    entry[field_name] = "HANDWRITING_ERROR"
                    logging.error(f"❌ Exception while processing handwriting for {field_name} on page {page_num}: {e}")
                    log_issue("HANDWRITING_ERROR", field_name)
            else:
                texts = read_text(region_array, backend="doctr")
                if texts:
                    entry[field_name] = texts[0][1]
                    logging.info(f"📝 Printed field '{field_name}': {texts[0][1]}")
                else:
                    entry[field_name] = "TEXT_NOT_FOUND"
                    logging.warning(f"⚠️ Printed OCR failed for: {field_name}")
                    log_issue("TEXT_NOT_FOUND", field_name)
                save_crop_and_thumbnail(region, crops_dir, f"{short_name}_{page_num}", thumbnails_dir, thumbnail_log)

        except Exception as e:
            entry[field_name] = "GENERAL_ERROR"
            logging.exception(f"❌ Exception while processing field {field_name} on page {page_num}: {e}")
            log_issue("GENERAL_ERROR", field_name)

    duration = round(time.time() - start_time, 2)
    logging.info(f"✅ Finished page {page_num} in {duration}s")

    return {
        "entry": entry,
        "ticket_issue": ticket_issue,
        "thumbnails": thumbnail_log,
        "timing": {"Page": page_num, "DurationSeconds": duration},
        "issue_log": issue_log,
    }

import logging
import os

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
    reader_hand = initialize_reader("onnxruntime")

    page_num = page_idx + 1
    crops_dir = os.path.join(output_dir, "crops")
    thumbnails_dir = os.path.join(output_dir, "thumbnails")
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(crops_dir, exist_ok=True)
    os.makedirs(thumbnails_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    entry = {"Page": page_num}
    ticket_issue = ""
    issue_log = []
    thumbnail_log = []

    logging.info(f"📄 Processing page {page_num}")
    start_time = time.time()

    for field_name, field_conf in fields.items():
        short_name = simplify_field_name(field_name)

        if "box" not in field_conf:
            logging.warning(f"⚠️ Field '{field_name}' missing 'box', skipping.")
            continue

        box = sanitize_box(field_conf["box"], *img.size)
        if box is None:
            logging.error(f"❌ Invalid sanitized box for {field_name} on page {page_num}: {field_conf['box']}")
            entry[field_name] = "BOX_INVALID"
            continue

        region = img.crop(box)
        if region is None:
            logging.error(f"❌ Cropped region is None for {field_name} on page {page_num}")
            entry[field_name] = "REGION_NONE"
            continue

        region_array = ensure_region_array(region, field_name, page_num, entry)
        if region_array is None:
            continue
        if not isinstance(region_array, np.ndarray):
            logging.error(f"❌ region_array is not ndarray for {field_name} on page {page_num}")
            entry[field_name] = "INVALID_ARRAY_TYPE"
            continue
        if region_array.size == 0:
            logging.error(f"❌ region_array is empty for {field_name} on page {page_num}")
            entry[field_name] = "EMPTY_ARRAY"
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
                else:
                    entry[field_name] = "MISSING"
                    ticket_issue = "MISSING"
                    logging.error("🛑 Template file 'ticket_template.jpg' not found.")

            save_crop_and_thumbnail(region, crops_dir, f"{short_name}_{page_num}", thumbnails_dir, thumbnail_log)
            continue

        try:
            if detect_handwriting(region) or is_handwriting_deep(region):
                from modular_analyzer.image_preprocessing import preprocess_for_onnx, decode_onnx_output

                # Validate region_array before preprocessing
                if not isinstance(region_array, np.ndarray):
                    logging.error(
                        f"❌ Invalid region_array type for {field_name} on page {page_num}: "
                        f"{type(region_array)}"
                    )
                    entry[field_name] = "INVALID_REGION_ARRAY"
                    continue
                if region_array.ndim not in (2, 3):
                    logging.error(
                        f"❌ region_array has invalid ndim={region_array.ndim} "
                        f"for {field_name} on page {page_num}"
                    )
                    entry[field_name] = "INVALID_DIMS"
                    continue
                if region_array.size == 0:
                    logging.error(f"❌ Empty region_array for {field_name} on page {page_num}")
                    entry[field_name] = "EMPTY_REGION_ARRAY"
                    continue

                if region_array.ndim == 2 or region_array.shape[2] != 3:
                    region_array = cv2.cvtColor(region_array, cv2.COLOR_GRAY2BGR)
                    logging.warning(f"⚠️ Converted grayscale to BGR for {field_name} on page {page_num}")

                try:
                    preprocessed = preprocess_for_onnx(region_array)
                    preds = reader_hand.run(None, {reader_hand.get_inputs()[0].name: preprocessed})[0]
                    decoded = decode_onnx_output(preds)
                    if decoded:
                        entry[field_name] = decoded
                        logging.info(f"✍️ Handwritten field '{field_name}': {decoded}")
                    else:
                        entry[field_name] = "HANDWRITING_UNREADABLE"
                        logging.warning(f"⚠️ Handwriting OCR unreadable for: {field_name}")
                except Exception as e:
                    entry[field_name] = "HANDWRITING_ERROR"
                    logging.error(f"❌ ONNX handwriting OCR failed for {field_name} on page {page_num}: {e}")

                save_field(region, crops_dir, f"{short_name}_{page_num}")
                save_crop_and_thumbnail(region, crops_dir, f"{short_name}_{page_num}", thumbnails_dir, thumbnail_log)

            else:
                entry[field_name] = "SKIPPED_NONHANDWRITING"
                logging.debug(f"Field '{field_name}' did not appear handwritten — skipped.")
            if detect_handwriting(region) or is_handwriting_deep(region):
                try:
                    if not isinstance(region_array, np.ndarray) or region_array.ndim != 3:
                        raise ValueError(f"Invalid image shape: {getattr(region_array, 'shape', None)}")

                    if region_array.shape[2] != 3:
                        region_array = cv2.cvtColor(region_array, cv2.COLOR_GRAY2BGR)
                        logging.warning(f"⚠️ Converted grayscale to BGR for {field_name} on page {page_num}")

                    from modular_analyzer.image_preprocessing import preprocess_for_onnx, decode_onnx_output

                    # Validate region_array before preprocessing
                    if region_array is None or not isinstance(region_array, np.ndarray):
                        logging.error(
                            f"❌ Invalid region_array for {field_name} on page {page_num}: {type(region_array)}")
                        entry[field_name] = "INVALID_REGION_ARRAY"
                        continue
                    if region_array.size == 0:
                        logging.error(f"❌ Empty region_array for {field_name} on page {page_num}")
                        entry[field_name] = "EMPTY_REGION_ARRAY"
                        continue

                    preprocessed = preprocess_for_onnx(region_array)
                    preds = reader_hand.run(None, {reader_hand.get_inputs()[0].name: preprocessed})[0]
                    decoded = decode_onnx_output(preds)

                    if decoded:
                        entry[field_name] = decoded
                        logging.info(f"✍️ Handwritten field '{field_name}': {decoded}")
                    else:
                        entry[field_name] = "HANDWRITING_UNREADABLE"
                        logging.warning(f"⚠️ Handwriting OCR unreadable for: {field_name}")

                except Exception as e:
                    entry[field_name] = "HANDWRITING_ERROR"
                    logging.error(f"❌ Exception while processing handwriting for {field_name} on page {page_num}: {e}")

                save_field(region, crops_dir, f"{short_name}_{page_num}")
                save_crop_and_thumbnail(region, crops_dir, f"{short_name}_{page_num}", thumbnails_dir, thumbnail_log)

            logging.debug(f"🧪 Calling preprocess_for_onnx on shape={region_array.shape}, dtype={region_array.dtype}")
            try:
                if not isinstance(region_array, np.ndarray) or region_array.ndim != 3:
                    raise ValueError(f"Invalid image shape: {getattr(region_array, 'shape', None)}")

                if region_array.shape[2] != 3:
                    region_array = cv2.cvtColor(region_array, cv2.COLOR_GRAY2BGR)
                    logging.warning(f"⚠️ Converted grayscale to BGR for {field_name} on page {page_num}")

                from modular_analyzer.image_preprocessing import preprocess_for_onnx, decode_onnx_output

                logging.debug(
                    f"🧪 Calling preprocess_for_onnx on shape={region_array.shape}, dtype={region_array.dtype}")

                preprocessed = preprocess_for_onnx(region_array)
                preds = reader_hand.run(None, {reader_hand.get_inputs()[0].name: preprocessed})[0]
                decoded = decode_onnx_output(preds)

                if decoded:
                    entry[field_name] = decoded
                    logging.info(f"✍️ Handwritten field '{field_name}': {decoded}")
                else:
                    entry[field_name] = "HANDWRITING_UNREADABLE"
                    logging.warning(f"⚠️ Handwriting OCR unreadable for: {field_name}")

            except Exception as e:
                entry[field_name] = "HANDWRITING_ERROR"
                logging.error(f"❌ Exception while processing handwriting for {field_name} on page {page_num}: {e}")

            else:
                texts = read_text(region_array, backend="doctr")
                if texts:
                    entry[field_name] = texts[0][1]
                    logging.info(f"📝 Printed field '{field_name}': {texts[0][1]}")
                else:
                    entry[field_name] = "TEXT_NOT_FOUND"
                    logging.warning(f"⚠️ Printed OCR failed for: {field_name}")

                save_crop_and_thumbnail(region, crops_dir, f"{short_name}_{page_num}", thumbnails_dir, thumbnail_log)

        except Exception as e:
            entry[field_name] = "GENERAL_ERROR"
            logging.exception(f"❌ Exception while processing field {field_name} on page {page_num}: {e}")

    duration = round(time.time() - start_time, 2)
    logging.info(f"✅ Finished page {page_num} in {duration}s")

    return {
        "entry": entry,
        "ticket_issue": ticket_issue,
        "issues": issue_log,
        "thumbnails": thumbnail_log,
        "timing": {"Page": page_num, "DurationSeconds": duration},
    }

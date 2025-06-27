# --- modular_analyzer/pdf_utils.py ---

import fitz
from PIL import Image


def convert_pdf_to_images(pdf_path):
    """
    Convert each page of the given PDF to a PIL Image.
    :param pdf_path: Path to the PDF file.
    :return: List of PIL Image objects, one per page.
    """
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        images.append(img)
    return images


# === IMPROVEMENT: pdf_utils.py > process_pages_concurrently ===
from multiprocessing import Pool


def process_pages_concurrently(args_list, processor):
    with Pool() as pool:
        results = pool.map(processor, args_list)

    # Filter out None results
    return [r for r in results if r is not None]


# === TEST HARNESS FOR KNOWN-INVALID INPUT ===
def test_read_text_with_invalid_image():
    import numpy as np
    from modular_analyzer.ocr_utils import read_text, initialize_reader

    reader = initialize_reader("paddleocr")
    try:
        result = read_text(reader, None)  # force failure
    except ValueError as e:
        print("✅ Caught expected ValueError:", e)

    try:
        bad_array = np.array([[]])
        result = read_text(reader, bad_array)
    except ValueError as e:
        print("✅ Caught expected ValueError on bad shape:", e)

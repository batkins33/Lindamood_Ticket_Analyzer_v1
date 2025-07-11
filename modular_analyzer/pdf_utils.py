# --- modular_analyzer/pdf_utils.py ---

import fitz
from PIL import Image


def convert_pdf_to_images(pdf_path):
    """
    Convert each page of the given PDF to a PIL Image.
    :param pdf_path: Path to the PDF file.
    :return: List of PIL Image objects, one per page.
    """
    images = []
    with fitz.open(pdf_path) as doc:
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



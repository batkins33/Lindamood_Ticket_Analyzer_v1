import pytest

modules_to_test = [
    "cv2",
    "paddleocr",
    "onnxruntime",
    "easyocr",
    "pytesseract",
    "numpy",
    "torch",
    "torchvision",
    "pandas",
    "sklearn",
    "skimage",
    "fitz",
]

@pytest.mark.parametrize("module", modules_to_test)
def test_module_available(module):
    pytest.importorskip(module)

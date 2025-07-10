import importlib
import sys

import sklearn
import skimage
modules_to_test = [
    "cv2",  # OpenCV (used for image processing)
    "paddleocr",  # OCR engine
    "onnxruntime",  # For running ONNX models
    "easyocr",  # Another OCR engine
    "pytesseract",  # Wrapper for Tesseract OCR
    "doctr",  # DocTR OCR engine
    "numpy",  # Numerical computation
    "torch", "torchvision",  # PyTorch and vision utilities
    "pandas",  # Tabular data manipulation
    "sklearn",  # Machine learning utilities
    "skimage",  # scikit-image for image processing
    "fitz",  # For handling PDF files
]

print("\n🔍 ENVIRONMENT MODULE CHECK\n" + "=" * 30)

for mod in modules_to_test:
    try:
        module = importlib.import_module(mod)
        version = getattr(module, '__version__', None)
        if not version and hasattr(module, 'VERSION'):
            version = module.VERSION
        print(f"✅ {mod}: {version or 'Loaded successfully'}")
    except Exception as e:
        print(f"❌ {mod}: FAILED TO LOAD\n    {type(e).__name__}: {e}")

print("\n🔁 sys.executable:", sys.executable)
print("📁 sys.path[0]:", sys.path[0])

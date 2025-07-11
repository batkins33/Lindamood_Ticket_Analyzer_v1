import os
import sys
import types
import pytest

# Stub heavy optional dependencies before importing ocr_utils
for name in [
    "cv2", "onnxruntime", "doctr", "doctr.io", "doctr.models", "pytesseract", "PIL", "PIL.Image", "PIL.ImageDraw"
]:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

fake_pil = sys.modules.get("PIL")
pil_image_mod = types.ModuleType("PIL.Image")
class DummyImage:
    pass
pil_image_mod.Image = DummyImage
sys.modules["PIL.Image"] = pil_image_mod
fake_pil.Image = pil_image_mod
doctr_io = sys.modules.get("doctr.io")
doctr_io.DocumentFile = type("DocumentFile", (), {})
doctr_models = sys.modules.get("doctr.models")
doctr_models.ocr_predictor = lambda *a, **k: object()

np = pytest.importorskip("numpy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

ocr_utils = __import__('modular_analyzer.ocr_utils', fromlist=['correct_image_orientation'])
correct_image_orientation = ocr_utils.correct_image_orientation

Image = pytest.importorskip('PIL').Image


def test_orientation_none():
    if Image is None:
        return
    img = Image.new('RGB', (10, 10))
    result = correct_image_orientation(img, method='none')
    assert result is img


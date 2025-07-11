import os
import sys
import types

# Stub heavy optional dependencies before importing page_processor
for name in [
    "pandas", "cv2", "onnxruntime", "openpyxl", "openpyxl.styles",
    "PIL", "doctr", "doctr.io", "doctr.models", "yaml"
]:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

# Provide minimal attributes required by file_utils and ocr_utils
sys.modules["openpyxl"].load_workbook = lambda *a, **k: None
sys.modules["openpyxl.styles"].PatternFill = lambda *a, **k: None

fake_pil = sys.modules.get("PIL")
pil_image_mod = types.ModuleType("PIL.Image")
class DummyImage:
    pass
pil_image_mod.Image = DummyImage
sys.modules["PIL.Image"] = pil_image_mod
fake_pil.Image = pil_image_mod
image_draw_mod = types.ModuleType("PIL.ImageDraw")
sys.modules["PIL.ImageDraw"] = image_draw_mod
fake_pil.ImageDraw = image_draw_mod

doctr_io = sys.modules.get("doctr.io")
doctr_io.DocumentFile = type("DocumentFile", (), {})
doctr_models = sys.modules.get("doctr.models")
doctr_models.ocr_predictor = lambda *a, **k: object()
yaml_mod = sys.modules.get("yaml")
yaml_mod.safe_load = lambda *a, **k: {}

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modular_analyzer.types import PageTask
def test_process_page_runs(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "numpy", types.ModuleType("numpy"))
    import modular_analyzer.page_processor as pp
    monkeypatch.setattr(pp, "initialize_reader", lambda backend="doctr": object())

    task = PageTask(page_idx=0, img=object(), fields={}, output_dir=str(tmp_path), vendor="v", date="d")
    result = pp.process_page(task)
    assert result["issue_log"] == []

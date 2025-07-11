import pytest

ocr_utils = pytest.importorskip('modular_analyzer.ocr_utils')
np = pytest.importorskip('numpy')

class DummyImage:
    def convert(self, mode):
        assert mode == "RGB"
        return np.zeros((1, 1, 3), dtype=np.uint8)

def test_extract_text_fields_uses_read_text(monkeypatch):
    called = {}
    def fake_read_text(image, backend="doctr"):
        called['image_type'] = type(image)
        called['backend'] = backend
        return [("box", "text", 1.0)]

    monkeypatch.setattr(ocr_utils, 'read_text', fake_read_text)
    img = DummyImage()
    result = ocr_utils.extract_text_fields(img, reader=object(), backend="onnxruntime")
    assert result == [("box", "text", 1.0)]
    assert called['backend'] == "onnxruntime"
    assert issubclass(called['image_type'], np.ndarray)

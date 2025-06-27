import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import numpy as np
except Exception:  # numpy might not be installed in minimal test env
    np = None

ocr_utils = pytest.importorskip('modular_analyzer.ocr_utils')
read_text = ocr_utils.read_text

@pytest.mark.skipif(np is None, reason="numpy is required for this test")
def test_read_text_with_none():
    with pytest.raises(ValueError):
        read_text(None)

@pytest.mark.skipif(np is None, reason="numpy is required for this test")
def test_read_text_with_empty_array():
    with pytest.raises(ValueError):
        read_text(np.array([[]]))

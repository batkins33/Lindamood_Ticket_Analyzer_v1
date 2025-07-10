import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

def test_cv2_resize():
    img = np.random.randint(0, 255, (100, 200), dtype=np.uint8)
    resized = cv2.resize(img, (96, 32), interpolation=cv2.INTER_LINEAR)
    assert resized.shape == (32, 96)

import os
import pytest

fitz = pytest.importorskip("fitz")

from modular_analyzer.pdf_utils import convert_pdf_to_images


def _open_targets():
    targets = []
    for fd in os.listdir("/proc/self/fd"):
        try:
            targets.append(os.readlink(f"/proc/self/fd/{fd}"))
        except OSError:
            continue
    return targets


def test_convert_pdf_to_images_closes_file(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()

    convert_pdf_to_images(str(pdf_path))

    assert str(pdf_path) not in _open_targets()

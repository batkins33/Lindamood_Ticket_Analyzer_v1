import os
import sys
import pytest

pytest.importorskip('pandas')
openpyxl = pytest.importorskip('openpyxl')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modular_analyzer.file_utils import save_entries_to_excel, color_code_excel


def test_color_code_excel_round_trip(tmp_path):
    entries = [
        {"Page": 1, "Ticket": "missing data"},
        {"Page": 2, "Ticket": "valid"},
    ]

    save_entries_to_excel(entries, tmp_path, "sample")
    csv_path = tmp_path / "sample_ticket_numbers.csv"

    assert csv_path.exists()

    color_code_excel(str(csv_path))

    xlsx_path = tmp_path / "sample_ticket_numbers.xlsx"
    assert xlsx_path.exists()

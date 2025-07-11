import sys
import types

# Stub pandas so reporting_utils can be imported without the real dependency.
sys.modules.setdefault("pandas", types.ModuleType("pandas"))

from modular_analyzer.reporting_utils import export_logs_to_html, auto_export_logs

def test_export_logs_to_html(tmp_path):
    log_file = tmp_path / "sample.log"
    html_file = tmp_path / "report.html"
    log_file.write_text(
        "[2024-01-01 12:34:56,789] [ERROR] test.py:10 - Something went wrong\n"
        "[2024-01-01 12:35:00,123] [WARNING] test.py:20 - Something suspicious\n"
        "[2024-01-01 12:35:01,000] [INFO] test.py:30 - Info message\n"
        "Unstructured line\n"
    )

    export_logs_to_html(str(log_file), str(html_file))

    html = html_file.read_text()
    assert "Error Log Report" in html
    assert "Something went wrong" in html
    assert "Something suspicious" in html
    assert "Unstructured line" in html
    assert "Info message" not in html


def test_auto_export_logs_no_file(tmp_path, monkeypatch):
    """auto_export_logs should not raise if error.log is missing."""
    monkeypatch.chdir(tmp_path)
    # Ensure no error.log exists
    assert not (tmp_path / "error.log").exists()
    auto_export_logs()  # should run without exceptions

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from processor.filename_utils import add_suffix


def test_add_suffix():
    assert add_suffix("data.csv", "_sorted") == "data_sorted.csv"
    assert add_suffix("/tmp/sample.csv", "_done").endswith("sample_done.csv")

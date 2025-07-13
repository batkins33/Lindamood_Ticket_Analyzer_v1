import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from processor.file_handler import sort_tickets


def test_sort_tickets_priority():
    tickets = [
        {"id": "1", "priority": "high"},
        {"id": "2", "priority": "low"},
        {"id": "3", "priority": "medium"},
    ]
    sorted_t = sort_tickets(tickets)
    ids = [t["id"] for t in sorted_t]
    assert ids == ["2", "3", "1"]

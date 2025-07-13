from pathlib import Path
from typing import List, Dict
import csv

from utils.loader import load_csv

PRIORITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def read_tickets(path: str | Path) -> List[Dict[str, str]]:
    """Load ticket data from a CSV file."""
    return load_csv(path)


def sort_tickets(tickets: List[Dict[str, str]], by: str = "priority") -> List[Dict[str, str]]:
    """Return tickets sorted by a given key."""
    if by == "priority":
        return sorted(tickets, key=lambda t: PRIORITY_ORDER.get(t.get("priority", ""), -1))
    return sorted(tickets, key=lambda t: t.get(by, ""))


def save_tickets(tickets: List[Dict[str, str]], path: str | Path) -> None:
    """Write ticket data to a CSV file."""
    if not tickets:
        return
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tickets[0].keys())
        writer.writeheader()
        writer.writerows(tickets)

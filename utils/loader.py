import csv
from pathlib import Path
from typing import List, Dict


def load_csv(path: str | Path) -> List[Dict[str, str]]:
    """Read a CSV file and return a list of rows as dictionaries."""
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

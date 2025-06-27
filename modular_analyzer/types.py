from dataclasses import dataclass
from typing import Any

from PIL import Image


@dataclass
class PageTask:
    page_idx: int
    img: Image.Image
    fields: dict
    output_dir: str
    vendor: str
    date: str
    issues_log: Any  # can be List or None

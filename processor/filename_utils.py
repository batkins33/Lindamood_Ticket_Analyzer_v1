from pathlib import Path


def add_suffix(path: str | Path, suffix: str) -> str:
    """Return the filename with the given suffix inserted before the extension."""
    p = Path(path)
    return str(p.with_name(p.stem + suffix + p.suffix))

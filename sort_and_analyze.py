"""Utility script to sort a CSV and then launch the PDF analyzer."""
import sys
from processor import run as sorter
from modular_analyzer.main import main as analyze_main


def main(argv: list[str] | None = None) -> None:
    """Run the sorter followed by the analyzer."""
    sorter.main(argv)
    analyze_main()


if __name__ == "__main__":
    main(sys.argv[1:])

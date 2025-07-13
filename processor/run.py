import argparse
from pathlib import Path
from .file_handler import read_tickets, sort_tickets, save_tickets
from .filename_utils import add_suffix


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Sort ticket CSV files")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("output", nargs="?", help="Output CSV file")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else Path(add_suffix(input_path, "_sorted"))

    tickets = read_tickets(input_path)
    sorted_tickets = sort_tickets(tickets)
    save_tickets(sorted_tickets, output_path)
    print(f"Saved sorted tickets to {output_path}")

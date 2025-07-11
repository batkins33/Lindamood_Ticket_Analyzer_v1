import logging
import os
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from modular_analyzer.file_utils import (
    list_yaml_configs, load_yaml, save_csv,
    color_code_excel, zip_folder,
    validate_required_files, is_dir_writable,
    find_file_case_insensitive, save_entries_to_excel
)
from modular_analyzer.logger_utils import setup_logger
from modular_analyzer.ocr_utils import (
    add_box_to_fields
)
from modular_analyzer.page_processor import process_page
from modular_analyzer.pdf_utils import convert_pdf_to_images, process_pages_concurrently
from modular_analyzer.reporting_utils import collect_summary_report, log_yaml_fields
from modular_analyzer.types import PageTask

CONFIGS_DIR = "modular_analyzer/configs"
OUTPUT_DIR = "output"

setup_logger()

import sys
import traceback


def custom_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception",
                     exc_info=(exc_type, exc_value, exc_traceback))
    with open("error.log", "w") as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)


sys.excepthook = custom_exception_handler


def flatten_fields(conf):
    flat = {}
    for section_name, section in conf.items():
        if isinstance(section, dict):
            for field_name, field_conf in section.items():
                flat[f"{section_name}.{field_name}"] = field_conf
    return flat


def main():
    logging.info("Welcome to Modular Analyzer!")
    Tk().withdraw()
    pdf_path = askopenfilename(title="Select PDF to Analyze", filetypes=[("PDF Files", "*.pdf")])
    if not pdf_path:
        logging.error("No PDF selected. Exiting.")
        return

    structured_name = Path(pdf_path).stem
    yaml_files = list_yaml_configs(CONFIGS_DIR)
    yaml_files = [f for f in yaml_files if f.lower() != "ocr_config.yaml"]
    vendor_names = [os.path.splitext(f)[0] for f in yaml_files]

    print("Available Vendors:")
    for idx, vendor in enumerate(vendor_names, start=1):
        print(f"{idx}. {vendor}")

    vendor_match = None
    for yaml_file in yaml_files:
        base = os.path.splitext(yaml_file)[0]
        if base.lower() in structured_name.lower():
            vendor_match = base
            break

    if not vendor_match:
        print(f"No YAML config matches the PDF name: {structured_name}")
        print(f"Available configs: {vendor_names}")
        return

    confirmed = input(f"Auto-matched '{vendor_match}'. Use this config? [Y/n]: ").strip().lower()
    if confirmed not in ["", "y", "yes"]:
        print("Aborting by user.")
        return

    yaml_path = find_file_case_insensitive(f"{vendor_match}.yaml", CONFIGS_DIR)
    fields_conf = load_yaml(yaml_path)

    if not is_dir_writable(OUTPUT_DIR):
        logging.error(f"Output directory not writable: {OUTPUT_DIR}")
        return

    ok, missing = validate_required_files(
        vendor_match, CONFIGS_DIR, ["ticket_template.jpg"], "modular_analyzer/templates"
    )
    if not ok:
        logging.error("Missing required files:\n" + "\n".join(missing))
        return

    add_box_to_fields(fields_conf)
    log_yaml_fields(fields_conf, yaml_path)

    output_dir = os.path.join(OUTPUT_DIR, vendor_match, structured_name)
    os.makedirs(output_dir, exist_ok=True)

    images = convert_pdf_to_images(pdf_path)
    logging.info(f"Converted {len(images)} pages from PDF.")

    flat_fields = flatten_fields(fields_conf)
    args_list = [
        PageTask(
            page_idx=idx,
            img=img,
            fields=flat_fields,
            output_dir=output_dir,
            vendor=vendor_match,
            date="20250101"
        )
        for idx, img in enumerate(images)
    ]
    results = process_pages_concurrently(args_list, process_page)

    entries = [r["entry"] for r in results]
    ticket_issues = [(r["entry"].get("Page"), r["ticket_issue"]) for r in results if r["ticket_issue"]]
    thumbnails = [thumb for r in results for thumb in r["thumbnails"]]
    timings = [r["timing"] for r in results]

    save_entries_to_excel(entries, output_dir, structured_name)
    csv_path = os.path.join(output_dir, f"{structured_name}_ticket_numbers.csv")
    save_csv(ticket_issues, columns=["Page", "Issue"],
             filepath=os.path.join(output_dir, "ticket_issues.csv"))
    save_csv(thumbnails, columns=["Page", "Field", "ThumbnailPath"],
             filepath=os.path.join(output_dir, "thumbnail_index.csv"))
    save_csv(timings, columns=["Page", "DurationSeconds"],
             filepath=os.path.join(output_dir, "process_analysis.csv"))

    collect_summary_report(output_dir, entries)
    color_code_excel(csv_path)
    zip_folder(os.path.join(output_dir, "valid"), os.path.join(output_dir, "valid_pages.zip"))

    logging.info("Processing complete. Output saved.")


if __name__ == "__main__":
    main()

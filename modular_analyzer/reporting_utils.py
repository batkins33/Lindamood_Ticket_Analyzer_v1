# --- modular_analyzer/reporting_utils.py ---

import atexit
import logging
import os

import pandas as pd


def collect_summary_report(output_dir, entries):
    valid = sum(1 for e in entries if "MISSING" not in str(e.values()))
    missing = sum(1 for e in entries if "MISSING" in str(e.values()))
    template = sum(1 for e in entries if "TemplateMatch" in str(e.values()))
    summary = [{"TotalPages": len(entries), "Valid": valid, "Missing": missing, "TemplateMatched": template}]
    path = os.path.join(output_dir, "summary_report.csv")
    df = pd.DataFrame(summary)
    df.to_csv(path, index=False)
    logging.info(f"Summary report saved: {path}")


def collect_thumbnail_index(output_dir, thumbnail_log):
    if thumbnail_log:
        path = os.path.join(output_dir, "thumbnail_index.csv")
        df = pd.DataFrame(thumbnail_log)
        df.to_csv(path, index=False)
        logging.info(f"Thumbnail index saved: {path}")


def collect_issue_log(output_dir, issue_log):
    if issue_log:
        path = os.path.join(output_dir, "issues_log.csv")
        df = pd.DataFrame(issue_log)
        df.to_csv(path, index=False)
        logging.info(f"Issues log saved: {path}")


def collect_process_timings(output_dir, timing_log):
    if timing_log:
        path = os.path.join(output_dir, "process_analysis.csv")
        df = pd.DataFrame(timing_log)
        df.to_csv(path, index=False)
        logging.info(f"Page processing timings saved: {path}")


def log_yaml_fields(fields_conf, yaml_path):
    logging.info(f"📄 Loaded YAML config: {yaml_path}")
    for section_name, section in fields_conf.items():
        if not isinstance(section, dict):
            continue
        for field_name, field_data in section.items():
            if isinstance(field_data, dict):
                has_pos = "position_inches" in field_data
                has_size = "size_inches" in field_data
                has_box = "box" in field_data
                logging.info(
                    f"🧾 Field '{section_name}.{field_name}': "
                    f"pos={has_pos}, size={has_size}, box={has_box}"
                )


# === HTML LOG EXPORT ===


def export_logs_to_csv(log_file_path, output_csv_path):
    import re
    import csv

    pattern = re.compile(
        r"\[(?P<datetime>.*?)\]\s+"  # [timestamp]
        r"\[\s*(?P<level>.*?)\]\s+"  # [ log level ]
        r"(?P<file>.*?):(?P<line>\d+)\s+-\s+"  # file:line -
        r"(?P<message>.*)"  # message
    )
    rows = []
    unmatched = []

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                rows.append(match.groupdict())
            else:
                unmatched.append({
                    "datetime": "",
                    "level": "UNMATCHED",
                    "file": "",
                    "line": "",
                    "message": line.strip()
                })

    rows.extend(unmatched)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["datetime", "level", "file", "line", "message"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Logs exported to {output_csv_path}")


# === HTML LOG EXPORT ===
def export_logs_to_html(log_file_path, output_html_path):
    import re

    pattern = re.compile(
        r"(?P<datetime>\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+\])\s+"
        r"\[\s*(?P<level>[A-Z]+)\]\s+"
        r"(?P<file>[^:]+):(?P<line>\d+)\s+-\s+"
        r"(?P<message>.+)"
    )
    grouped = {}
    allowed_levels = {"ERROR", "WARNING"}

    unmatched_lines = []

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                level = match.group("level")
                if level in allowed_levels:
                    grouped.setdefault(level, []).append(match.groupdict())
            else:
                unmatched_lines.append(line.strip())

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write("<html><head><style>details{margin-bottom:1em;}summary{font-weight:bold;}</style></head><body>")
        f.write("<h1>Error Log Report</h1>")

        for level, entries in grouped.items():
            f.write(f"<details><summary>{level} ({len(entries)} entries)</summary><ul>")
            for entry in entries:
                f.write("<li>" + " | ".join(f"{k}: {v}" for k, v in entry.items()) + "</li>")
            f.write("</ul></details>")

        if unmatched_lines:
            f.write("<details><summary>⚠️ Unmatched Log Lines</summary><ul>")
            for line in unmatched_lines:
                f.write(f"<li>{line}</li>")
            f.write("</ul></details>")

        f.write("</body></html>")
    print(f"✅ Logs exported to {output_html_path}")


def auto_export_logs():
    try:
        log_file = "error.log"
        export_logs_to_csv(log_file, "log_report.csv")
        export_logs_to_html(log_file, "log_report.html")
    except Exception as e:
        print(f"[auto_export_logs] Export failed: {e}")


atexit.register(auto_export_logs)

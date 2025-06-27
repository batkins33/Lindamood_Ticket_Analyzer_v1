# modular_analyzer/logger_utils.py

import logging
import os


def setup_logger(log_path="modular_analyzer/analyzer.log"):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        filename=log_path,
        filemode='a',
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )
    logging.getLogger().addHandler(logging.StreamHandler())  # Also print to console

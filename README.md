
# Lindamood Ticket Analyzer

This repository contains a PDF ticket analysis tool built around
`modular_analyzer`. It converts PDF pages to images and extracts fields such
as ticket numbers using a combination of **DocTR** for printed text,
Tesseract and optional ONNX‑based handwriting models. Results are saved to
CSV/Excel for further review.

## Main dependencies
- Python 3.10
- DocTR for OCR
- PaddleOCR / PaddlePaddle
- OpenCV
- PyMuPDF & pdf2image
- Tesseract via `pytesseract`
- EasyOCR / PyTorch
- ONNX Runtime
- pandas, numpy, scikit-learn

See [`docs/doctr_env.yaml`](docs/doctr_env.yaml) for the Conda environment
definition. Windows users can also use [`analyzer_env.yaml`](analyzer_env.yaml)
for a preconfigured setup. Both create an environment named `doctr_env`.

## Features
The analyzer provides:

- PDF to image conversion using `pdf2image`
- Printed-text OCR via DocTR
- ONNX-based handwriting recognition
- Optional template matching for ticket numbers
- Concurrent processing of pages using Python's multiprocessing

DocTR is the default OCR engine. `modular_analyzer/ocr_utils.py` also
supports PaddleOCR, EasyOCR and ONNX Runtime. You can switch engines by
calling `initialize_reader("paddleocr")` or passing `backend` to `read_text`.

## Usage
1. Create and activate the Conda environment:
   ```bash
   conda env create -f docs/doctr_env.yaml
   conda activate doctr_env
   ```
   (On Windows you can use `analyzer_env.yaml`.)
2. Run the analyzer and choose a PDF when prompted:
   ```bash
   python launch_analyzer.py
   ```
   Output files will be written under the `output/` directory.

## Environment check
Before running the analyzer you can verify all dependencies are installed:

```bash
python test_env_integrity.py
```
Any missing modules will be listed in `env_check.log` when using
`new_launch.bat` on Windows.

## Running tests
Unit tests live under the `tests/` directory and can be executed with:

```bash
pytest
```

## Additional documentation
A more in-depth guide is provided in
[docs/DETAILED_README.md](docs/DETAILED_README.md).

## License
This project is released under the [MIT License](LICENSE).

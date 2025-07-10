
# Lindamood Ticket Analyzer

This repository contains a PDF ticket analysis tool built around
`modular_analyzer`. It converts PDF pages to images and extracts fields such
as ticket numbers using a combination of PaddleOCR, Tesseract and ONNX-based
handwriting models. Results are saved to CSV/Excel for further review.

## Main dependencies
- Python 3.10
- PaddleOCR / PaddlePaddle
- OpenCV
- PyMuPDF & pdf2image
- Tesseract via `pytesseract`
- EasyOCR / PyTorch
- ONNX Runtime
- pandas, numpy, scikit-learn

See [`environment.yml`](environment.yml) or the Windows variant
[`analyzer_env.yaml`](analyzer_env.yaml) for the full list of required packages
and environment setup instructions.

## Features
The analyzer provides:

- PDF to image conversion using `pdf2image`
- Printed-text OCR via PaddleOCR (or EasyOCR if configured)
- ONNX-based handwriting recognition
- Optional template matching for ticket numbers
- Concurrent processing of pages using Python's multiprocessing

## Usage
1. Create and activate the Conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate analyzer_env
   ```
   (On Windows you can use `analyzer_env.yaml`.)
2. Run the analyzer and choose a PDF when prompted:
   ```bash
   python launch_analyzer.py
   ```
   Output files will be written under the `output/` directory.

## Environment check
The test suite includes a simple import check for optional dependencies. You
can run it with `pytest -k env_integrity` to see which modules are available.

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

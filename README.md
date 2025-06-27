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

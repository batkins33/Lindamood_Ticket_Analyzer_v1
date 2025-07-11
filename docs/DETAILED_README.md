# Ticket Analyzer

A Python-based tool for extracting and analyzing truck ticket data from PDF scans. This application uses multiple
OCR/ICR engines to read printed text and handwriting, and includes template matching and classification workflows.

---

## Features

* **PDF to Image Conversion**: Converts each page of a PDF into PIL images.
* **Printed Text OCR**: Uses DocTR for high-accuracy printed-text recognition.
* **Handwriting Recognition (ICR)**: Integrates an ONNXRuntime-based model for handwriting extraction.
* **Handwriting Detection**: Heuristic and deep-learning based methods to detect handwritten regions.
* **Template Matching**: Locates known form elements using OpenCV template matching.
* **Concurrent Processing**: Leverages Python’s `multiprocessing` for fast, parallel page processing.
* **Vendor Configuration**: Built-in support for multiple ticket vendors with custom XML mappings.

---

## Directory Structure

```
Ticket_Analyzer/
├── launch_analyzer.py           # Entry point script
├── environment.yml              # Conda environment definition
├── README.md                    # Project documentation
└── modular_analyzer/
    ├── main.py                  # Core orchestration logic
    ├── ocr_utils.py             # OCR/ICR helper functions
    ├── pdf_utils.py             # PDF-to-image conversion & concurrency
    ├── image_preprocessing.py   # Preprocessing pipelines for ONNX models
    ├── xml/                     # Vendor-specific XML mapping files
    └── models/
        ├── handwriting_ocr.onnx             # ONNX handwriting recognition model
        └── handwriting_classifier.onnx      # ONNX handwriting vs. printed classifier
```

---

## Installation

1. **Set up a Conda environment** (recommended on Windows):

   ```bash
   conda create -n ocr_env python=3.10 pip
   conda activate ocr_env
   ```

2. **Install core frameworks via Conda**:

   ```bash
   conda install -c pytorch pytorch cpuonly
   ```

3. **Install all dependencies**:

   ```bash
   conda env update -f environment.yml
   ```

4. **Tesseract OCR** (for `pytesseract`):

    * Download and install from the [UB-Mannheim Windows installer](https://github.com/UB-Mannheim/tesseract).

---

## Configuration

* Place your ONNX models under `modular_analyzer/models/`:

    * `handwriting_ocr.onnx`
    * `handwriting_classifier.onnx`

* Vendor XML mappings live in `modular_analyzer/xml/`. Add or update files for new vendors.

* Adjust `launch_analyzer.py` arguments or modify `main.py` defaults as needed (e.g., output directory, logging).

---

## Usage

1. **Activate environment**:

   ```bash
   conda activate ocr_env
   ```

2. **Run the analyzer**:

   ```bash
   python launch_analyzer.py
   ```

3. **Follow the on-screen prompts** to select the vendor and PDF file.

4. **Results** will be output to the `./output/` folder, including:

    * Cropped images and text snippets
    * CSV/Excel logs of extracted fields
    * Debug logs under `log_output/`

---

## Troubleshooting

* **ONNX Runtime errors**:

    * Ensure ONNX models exist in the `models/` directory.
    * If you see a `providers` error, verify you’re using `onnxruntime>=1.9` and the code
      passes `providers=["CPUExecutionProvider"]`.

* **NumPy compatibility**:

    * Use `numpy==1.24.3` to avoid binary mismatches with compiled modules.

* **OpenCV issues**:

    * Only install `opencv-python` (no headless) at version `4.6.0.66` for full G-API support.

* **Shapely DLL errors**:

    * If you get `WinError 126`, reinstall with a prebuilt wheel: `pip install shapely`.

---

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to your branch (`git push origin feature/my-feature`).
5. Open a pull request.

---

## License

MIT License. See `LICENSE` file for details.

# --- modular_analyzer/utils/image_preprocessing.py ---

import logging

import cv2
import numpy as np


def preprocess_for_handwriting_classification(img_array):
    try:
        if img_array is None:
            logging.error("🛑 preprocess: input img_array is None")
            return None
        if not isinstance(img_array, np.ndarray):
            logging.error(f"🛑 preprocess: expected np.ndarray, got {type(img_array)}")
            return None
        if img_array.ndim not in (2, 3):
            logging.error(f"🛑 preprocess: invalid dimensions {img_array.ndim}")
            return None

        if img_array.ndim == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        resized = cv2.resize(gray, (96, 32), interpolation=cv2.INTER_LINEAR)
        normalized = resized.astype(np.float32) / 255.0
        normalized = normalized[np.newaxis, np.newaxis, :, :]  # shape: (1, 1, 32, 96)
        return normalized

    except Exception as e:
        logging.exception(f"❌ Exception in preprocess_for_handwriting_classification: {e}")
        return None


def preprocess_for_onnx(region_array):
    """
    Prepare an image for ONNX handwriting OCR inference.
    Converts to grayscale, resizes, normalizes, and reshapes.
    """
    if region_array is None:
        raise ValueError("❌ preprocess_for_onnx received NoneType image")
    if not isinstance(region_array, np.ndarray):
        raise ValueError(f"❌ preprocess_for_onnx received invalid type: {type(region_array)}")
    if region_array.size == 0:
        raise ValueError("❌ preprocess_for_onnx received empty image array")

    try:
        if region_array.ndim == 3 and region_array.shape[2] != 3:
            raise ValueError(f"❌ preprocess_for_onnx expected 3-channel image, got shape: {region_array.shape}")
        if region_array.ndim == 2:
            img = region_array
        else:
            img = cv2.cvtColor(region_array, cv2.COLOR_RGB2GRAY)

        img = cv2.resize(img, (128, 32))
        img = img.astype(np.float32) / 255.0
        img = img.reshape(1, 1, 32, 128)
        return img
    except Exception as e:
        raise ValueError(f"❌ Image preprocessing failed: {e}")


def decode_onnx_output(preds):
    # Simple greedy decoder assuming softmax outputs over character logits
    import string
    alphabet = string.ascii_uppercase + string.digits + "-"
    blank_token = len(alphabet)

    best_path = np.argmax(preds[0], axis=1)
    collapsed = []
    prev = blank_token
    for p in best_path:
        if p != prev and p != blank_token:
            collapsed.append(p)
        prev = p

    chars = [alphabet[c] for c in collapsed if c < len(alphabet)]
    return "".join(chars)

import numpy as np
import onnxruntime as ort

# Load model
session = ort.InferenceSession("handwriting_ocr.onnx")

# Prepare dummy input
input_name = session.get_inputs()[0].name
dummy_input = np.random.rand(1, 3, 1000, 600).astype(np.float32)

# Run inference
output = session.run(None, {input_name: dummy_input})

# Print output info
print(f"Output type: {type(output)}")
print(f"Number of outputs: {len(output)}")
print(f"First output shape: {np.array(output[0]).shape}")

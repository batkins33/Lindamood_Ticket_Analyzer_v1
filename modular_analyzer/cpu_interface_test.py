# torch + onnxruntime CPU-only inference test with benchmarking

import time

import numpy as np
import onnxruntime as ort
import torch
import torch.nn as nn


# Define simple linear model
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(4, 2)

    def forward(self, x):
        return self.fc(x)


# Instantiate and export model
def export_to_onnx():
    model = SimpleModel()
    dummy_input = torch.randn(1, 4)
    torch.onnx.export(
        model, dummy_input, "simple_model.onnx",
        input_names=["input"], output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        opset_version=12
    )


# Load and run ONNX model with CPU (benchmark version)
def run_onnx_inference_benchmark(num_runs=100):
    ort_session = ort.InferenceSession("simple_model.onnx", providers=["CPUExecutionProvider"])
    input_data = np.random.randn(1, 4).astype(np.float32)

    # Warm-up
    ort_session.run(None, {"input": input_data})

    # Benchmark loop
    start_time = time.time()
    for _ in range(num_runs):
        ort_session.run(None, {"input": input_data})
    end_time = time.time()

    avg_time_ms = (end_time - start_time) / num_runs * 1000
    print(f"Average inference time over {num_runs} runs: {avg_time_ms:.3f} ms")


if __name__ == "__main__":
    export_to_onnx()
    run_onnx_inference_benchmark()

import cv2
import numpy as np

img = np.random.randint(0, 255, (100, 200), dtype=np.uint8)

resized = cv2.resize(img, (96, 32), interpolation=cv2.INTER_LINEAR)

print("✅ Resize succeeded. New shape:", resized.shape)

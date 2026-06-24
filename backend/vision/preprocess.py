from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


def load_image(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        rgb = ImageOps.exif_transpose(image).convert("RGB")
    return cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)


def enhance_page(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        gray = image
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    background = cv2.GaussianBlur(contrast, (0, 0), sigmaX=15, sigmaY=15)
    normalized = cv2.addWeighted(contrast, 1.5, background, -0.5, 0)
    blur = cv2.GaussianBlur(normalized, (0, 0), sigmaX=3)
    sharpened = cv2.addWeighted(normalized, 1.5, blur, -0.5, 0)
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)


def save_image(path: str | Path, image: np.ndarray) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    extension = ".jpg" if suffix in {".jpg", ".jpeg"} else ".png"
    success, encoded = cv2.imencode(extension, image)
    if not success:
        raise ValueError(f"Cannot encode image for {output_path}")
    output_path.write_bytes(encoded.tobytes())
    return output_path


def preprocess_page(input_path: str | Path, output_path: str | Path) -> Path:
    image = load_image(input_path)
    enhanced = enhance_page(image)
    return save_image(output_path, enhanced)

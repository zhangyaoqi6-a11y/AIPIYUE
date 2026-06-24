from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class PaddleOcrEngine:
    def __init__(self, lang: str = "ch") -> None:
        os.environ.setdefault("PADDLE_DEVICE", "cpu")
        from paddleocr import PaddleOCR

        self._ocr = PaddleOCR(lang=lang)

    def recognize(self, image_path: str | Path) -> Any:
        path = str(image_path)
        if hasattr(self._ocr, "predict"):
            return self._ocr.predict(path)
        return self._ocr.ocr(path, cls=True)

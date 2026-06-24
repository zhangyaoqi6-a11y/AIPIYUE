import sys
import tempfile
import types
import unittest
from pathlib import Path

from backend.ocr.paddle_engine import PaddleOcrEngine


class PaddleEngineTests(unittest.TestCase):
    def test_recognize_uses_predict_when_available(self):
        class FakePaddleOCR:
            def __init__(self, lang):
                self.lang = lang
                self.seen_path = None

            def predict(self, path):
                self.seen_path = path
                return [{"rec_texts": ["答案"], "rec_scores": [0.9], "dt_polys": []}]

        fake_module = types.SimpleNamespace(PaddleOCR=FakePaddleOCR)
        previous_module = sys.modules.get("paddleocr")
        sys.modules["paddleocr"] = fake_module
        try:
            engine = PaddleOcrEngine(lang="ch")
        finally:
            if previous_module is None:
                sys.modules.pop("paddleocr", None)
            else:
                sys.modules["paddleocr"] = previous_module

        result = engine.recognize(Path("sample.png"))

        self.assertEqual(engine._ocr.lang, "ch")
        self.assertEqual(engine._ocr.seen_path, "sample.png")
        self.assertEqual(result[0]["rec_texts"], ["答案"])

    def test_recognize_uses_ocr_fallback_when_predict_is_missing(self):
        class FakePaddleOCR:
            def __init__(self, lang):
                self.lang = lang
                self.calls = []

            def ocr(self, path, cls):
                self.calls.append((path, cls))
                return [[[[0, 0], [1, 0], [1, 1], [0, 1]], ("A", 0.8)]]

        fake_module = types.SimpleNamespace(PaddleOCR=FakePaddleOCR)
        previous_module = sys.modules.get("paddleocr")
        sys.modules["paddleocr"] = fake_module
        try:
            engine = PaddleOcrEngine(lang="ch")
        finally:
            if previous_module is None:
                sys.modules.pop("paddleocr", None)
            else:
                sys.modules["paddleocr"] = previous_module

        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "样本.png"
            result = engine.recognize(image_path)

        self.assertEqual(engine._ocr.calls, [(str(image_path), True)])
        self.assertEqual(result[0][1], ("A", 0.8))


if __name__ == "__main__":
    unittest.main()

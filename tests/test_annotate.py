import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

from backend.ocr.schema import OcrTextBox
from backend.vision.annotate import draw_ocr_boxes


class AnnotateTests(unittest.TestCase):
    def test_draw_ocr_boxes_writes_changed_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "预处理.png"
            output_path = Path(tmp) / "结果" / "boxed.png"
            Image.new("RGB", (100, 80), "white").save(image_path)
            boxes = [
                OcrTextBox(
                    text="答案",
                    confidence=0.95,
                    points=[[10.0, 10.0], [60.0, 10.0], [60.0, 30.0], [10.0, 30.0]],
                )
            ]

            result = draw_ocr_boxes(image_path, boxes, output_path)

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())
            original = Image.open(image_path).convert("RGB")
            annotated = Image.open(output_path).convert("RGB")
            self.assertIsNotNone(ImageChops.difference(original, annotated).getbbox())


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from backend.vision.preprocess import enhance_page, load_image, preprocess_page, save_image


class PreprocessTests(unittest.TestCase):
    def test_load_image_handles_chinese_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "试卷样本.jpg"
            Image.new("RGB", (120, 80), "white").save(image_path)

            image = load_image(image_path)

            self.assertEqual(image.shape, (80, 120, 3))
            self.assertEqual(image.dtype, np.uint8)

    def test_enhance_page_keeps_shape_and_type(self):
        image = np.full((80, 120, 3), 180, dtype=np.uint8)
        cv2.putText(image, "A", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (40, 40, 40), 2)

        enhanced = enhance_page(image)

        self.assertEqual(enhanced.shape, image.shape)
        self.assertEqual(enhanced.dtype, np.uint8)
        self.assertGreater(int(enhanced.max()), int(enhanced.min()))

    def test_preprocess_page_writes_output_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "微信图片_测试.jpg"
            output_path = Path(tmp) / "输出" / "preprocessed.png"
            Image.new("RGB", (120, 80), "white").save(input_path)

            result = preprocess_page(input_path, output_path)

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())
            written = cv2.imdecode(np.frombuffer(output_path.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
            self.assertEqual(written.shape, (80, 120, 3))

    def test_save_image_handles_chinese_output_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "结果" / "预处理.png"
            image = np.full((10, 12, 3), 255, dtype=np.uint8)

            result = save_image(output_path, image)

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from backend.pipeline.minimal_ocr import discover_input_images, run_one_image


class MinimalOcrPipelineTests(unittest.TestCase):
    def test_discover_input_images_returns_supported_files_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "b.png"
            second = root / "a.jpg"
            ignored = root / "note.txt"
            Image.new("RGB", (20, 20), "white").save(first)
            Image.new("RGB", (20, 20), "white").save(second)
            ignored.write_text("not image", encoding="utf-8")

            result = discover_input_images(root)

            self.assertEqual(result, [second, first])

    def test_run_one_image_writes_json_and_debug_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "试卷.jpg"
            output_dir = root / "outputs"
            Image.new("RGB", (100, 80), "white").save(input_path)

            def fake_ocr_runner(image_path: Path):
                self.assertTrue(image_path.exists())
                return [
                    [
                        [[[10, 10], [40, 10], [40, 30], [10, 30]], ("答案A", 0.96)]
                    ]
                ]

            result = run_one_image(input_path, output_dir, fake_ocr_runner)

            self.assertTrue(result.preprocessed_image.exists())
            self.assertTrue(result.debug_image.exists())
            self.assertTrue(result.ocr_json.exists())
            payload = json.loads(result.ocr_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["source_image"], str(input_path))
            self.assertEqual(payload["ocr_box_count"], 1)
            self.assertEqual(payload["boxes"][0]["text"], "答案A")
            self.assertEqual(payload["image_size"], {"height": 80, "width": 100})


if __name__ == "__main__":
    unittest.main()

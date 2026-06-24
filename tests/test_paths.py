import json
import tempfile
import unittest
from pathlib import Path

from backend.common.paths import ensure_directory, read_binary, write_json


class PathHelperTests(unittest.TestCase):
    def test_ensure_directory_creates_nested_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "输出" / "嵌套"

            result = ensure_directory(target)

            self.assertEqual(result, target)
            self.assertTrue(target.is_dir())

    def test_read_binary_handles_chinese_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "微信图片_测试.jpg"
            file_path.write_bytes(b"abc")

            self.assertEqual(read_binary(file_path), b"abc")

    def test_write_json_writes_utf8_and_sorted_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "结果" / "ocr.json"

            result = write_json(output_path, {"text": "答案", "score": 1})

            self.assertEqual(result, output_path)
            loaded = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded, {"score": 1, "text": "答案"})


if __name__ == "__main__":
    unittest.main()

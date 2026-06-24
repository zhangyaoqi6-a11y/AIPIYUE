import json
import tempfile
import unittest
from pathlib import Path

from backend.tools.write_stage_record import build_stage_record, load_ocr_records, write_stage_record


class StageRecordTests(unittest.TestCase):
    def test_build_stage_record_contains_sample_summary(self):
        records = [
            {
                "source_image": "参考资料/样本1.jpg",
                "ocr_box_count": 2,
                "preprocessed_image": "data/outputs/minimal-ocr/样本1.preprocessed.png",
                "debug_image": "data/outputs/minimal-ocr/样本1.ocr-boxes.png",
            }
        ]

        markdown = build_stage_record(records)

        self.assertIn("# 第一阶段识别验证记录", markdown)
        self.assertIn("| 参考资料/样本1.jpg | 2 |", markdown)
        self.assertIn("data/outputs/minimal-ocr/样本1.ocr-boxes.png", markdown)

    def test_load_ocr_records_reads_sorted_json_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            second = output_dir / "b.ocr.json"
            first = output_dir / "a.ocr.json"
            second.write_text(json.dumps({"source_image": "b.jpg", "ocr_box_count": 1}), encoding="utf-8")
            first.write_text(json.dumps({"source_image": "a.jpg", "ocr_box_count": 3}), encoding="utf-8")

            records = load_ocr_records(output_dir)

            self.assertEqual([record["source_image"] for record in records], ["a.jpg", "b.jpg"])

    def test_write_stage_record_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "docs" / "阶段记录" / "第一阶段识别验证记录.md"

            result = write_stage_record(output_path, [{"source_image": "a.jpg", "ocr_box_count": 1}])

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())
            self.assertIn("a.jpg", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

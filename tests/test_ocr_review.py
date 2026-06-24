import json
import tempfile
import unittest
from pathlib import Path

from backend.review.ocr_review import (
    ReviewStore,
    build_question_candidates,
    build_review_samples,
    load_ocr_payload,
)


class OcrReviewTests(unittest.TestCase):
    def test_load_ocr_payload_reads_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.ocr.json"
            path.write_text(json.dumps({"ocr_box_count": 1, "boxes": []}), encoding="utf-8")

            payload = load_ocr_payload(path)

            self.assertEqual(payload["ocr_box_count"], 1)

    def test_build_question_candidates_extracts_numbered_items(self):
        boxes = [
            {
                "text": "1. The passage tells us about sports.",
                "confidence": 0.91,
                "points": [[10, 10], [200, 10], [200, 30], [10, 30]],
            },
            {
                "text": "A. running",
                "confidence": 0.88,
                "points": [[20, 40], [100, 40], [100, 60], [20, 60]],
            },
            {
                "text": "二、阅读理解",
                "confidence": 0.94,
                "points": [[5, 80], [120, 80], [120, 100], [5, 100]],
            },
        ]

        candidates = build_question_candidates("sample-a", boxes)

        self.assertEqual([candidate["label"] for candidate in candidates], ["1", "二"])
        self.assertEqual(candidates[0]["text"], "1. The passage tells us about sports.")
        self.assertEqual(candidates[0]["status"], "pending")
        self.assertEqual(candidates[0]["bounds"], {"x": 10.0, "y": 10.0, "width": 190.0, "height": 20.0})

    def test_build_review_samples_uses_existing_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            payload = {
                "source_image": "参考资料/样本.jpg",
                "preprocessed_image": str(output_dir / "样本.preprocessed.png"),
                "debug_image": str(output_dir / "样本.ocr-boxes.png"),
                "image_size": {"width": 100, "height": 80},
                "ocr_box_count": 1,
                "boxes": [
                    {
                        "text": "1. Test question",
                        "confidence": 0.8,
                        "points": [[1, 2], [40, 2], [40, 12], [1, 12]],
                    }
                ],
            }
            (output_dir / "样本.ocr.json").write_text(json.dumps(payload), encoding="utf-8")

            samples = build_review_samples(output_dir, ReviewStore(Path(tmp) / "reviews.json"))

            self.assertEqual(len(samples), 1)
            self.assertEqual(samples[0]["id"], "样本")
            self.assertEqual(samples[0]["ocr_box_count"], 1)
            self.assertEqual(samples[0]["question_candidates"][0]["label"], "1")

    def test_review_store_persists_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ReviewStore(Path(tmp) / "reviews.json")

            store.set_status("sample-a", "sample-a-q-1", "correct")
            reloaded = ReviewStore(Path(tmp) / "reviews.json")

            self.assertEqual(reloaded.get_status("sample-a", "sample-a-q-1"), "correct")
            self.assertEqual(reloaded.get_status("sample-a", "missing"), "pending")


if __name__ == "__main__":
    unittest.main()

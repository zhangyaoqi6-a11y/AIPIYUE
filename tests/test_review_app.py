import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.web.review_app import create_app


class ReviewAppTests(unittest.TestCase):
    def test_api_samples_returns_review_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "outputs"
            review_path = root / "reviews.json"
            output_dir.mkdir()
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

            client = TestClient(create_app(output_dir=output_dir, review_path=review_path, project_root=root))
            response = client.get("/api/samples")

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["samples"][0]["id"], "样本")
            self.assertEqual(data["samples"][0]["question_candidates"][0]["label"], "1")

    def test_api_reviews_persists_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "outputs"
            review_path = root / "reviews.json"
            output_dir.mkdir()
            client = TestClient(create_app(output_dir=output_dir, review_path=review_path, project_root=root))

            response = client.post(
                "/api/reviews",
                json={"sample_id": "sample-a", "candidate_id": "sample-a-q-1", "status": "incorrect"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "incorrect"})
            saved = json.loads(review_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["sample-a"]["sample-a-q-1"], "incorrect")

    def test_file_route_blocks_paths_outside_allowed_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "outputs"
            output_dir.mkdir()
            client = TestClient(create_app(output_dir=output_dir, review_path=root / "reviews.json", project_root=root))

            response = client.get("/files/..%2Fsecret.txt")

            self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

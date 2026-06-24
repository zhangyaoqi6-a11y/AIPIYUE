import unittest

from backend.ocr.normalize import normalize_paddle_result
from backend.ocr.schema import OcrTextBox


class OcrNormalizeTests(unittest.TestCase):
    def test_normalize_v2_style_result(self):
        raw = [
            [
                [[[0, 0], [50, 0], [50, 20], [0, 20]], ("姓名", 0.98)],
                [[[0, 30], [60, 30], [60, 50], [0, 50]], ("答案A", 0.87)],
            ]
        ]

        boxes = normalize_paddle_result(raw)

        self.assertEqual(
            boxes,
            [
                OcrTextBox(
                    text="姓名",
                    confidence=0.98,
                    points=[[0.0, 0.0], [50.0, 0.0], [50.0, 20.0], [0.0, 20.0]],
                ),
                OcrTextBox(
                    text="答案A",
                    confidence=0.87,
                    points=[[0.0, 30.0], [60.0, 30.0], [60.0, 50.0], [0.0, 50.0]],
                ),
            ],
        )

    def test_normalize_v3_style_dict_result(self):
        raw = [
            {
                "rec_texts": ["一、选择题", "B"],
                "rec_scores": [0.91, 0.76],
                "dt_polys": [
                    [[1, 2], [80, 2], [80, 22], [1, 22]],
                    [[10, 40], [28, 40], [28, 58], [10, 58]],
                ],
            }
        ]

        boxes = normalize_paddle_result(raw)

        self.assertEqual(len(boxes), 2)
        self.assertEqual(boxes[0].text, "一、选择题")
        self.assertEqual(boxes[0].confidence, 0.91)
        self.assertEqual(boxes[1].points, [[10.0, 40.0], [28.0, 40.0], [28.0, 58.0], [10.0, 58.0]])

    def test_normalize_empty_result(self):
        self.assertEqual(normalize_paddle_result(None), [])
        self.assertEqual(normalize_paddle_result([]), [])

    def test_to_dict_uses_stable_keys(self):
        box = OcrTextBox(text="题号1", confidence=0.8, points=[[0.0, 0.0], [1.0, 0.0]])

        self.assertEqual(
            box.to_dict(),
            {"confidence": 0.8, "points": [[0.0, 0.0], [1.0, 0.0]], "text": "题号1"},
        )


if __name__ == "__main__":
    unittest.main()

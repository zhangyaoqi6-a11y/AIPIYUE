from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

VALID_REVIEW_STATUSES = {"pending", "correct", "incorrect"}
QUESTION_PATTERNS = [
    re.compile(r"^\s*(\d{1,2})[.．、]\s*"),
    re.compile(r"^\s*([一二三四五六七八九十]+)[、.．]\s*"),
    re.compile(r"^\s*([①②③④⑤⑥⑦⑧⑨⑩])\s*"),
]


class ReviewStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._data = self._load()

    def get_status(self, sample_id: str, candidate_id: str) -> str:
        return self._data.get(sample_id, {}).get(candidate_id, "pending")

    def set_status(self, sample_id: str, candidate_id: str, status: str) -> None:
        if status not in VALID_REVIEW_STATUSES:
            raise ValueError(f"Invalid review status: {status}")
        sample = self._data.setdefault(sample_id, {})
        sample[candidate_id] = status
        self._save()

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {}
        return {
            str(sample_id): {str(candidate_id): str(status) for candidate_id, status in statuses.items()}
            for sample_id, statuses in raw.items()
            if isinstance(statuses, dict)
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )


def load_ocr_payload(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_review_samples(output_dir: str | Path, review_store: ReviewStore) -> list[dict[str, Any]]:
    root = Path(output_dir)
    samples: list[dict[str, Any]] = []
    for json_path in sorted(root.glob("*.ocr.json")):
        payload = load_ocr_payload(json_path)
        sample_id = json_path.name.removesuffix(".ocr.json")
        boxes = payload.get("boxes", [])
        candidates = build_question_candidates(sample_id, boxes, review_store)
        samples.append(
            {
                "id": sample_id,
                "source_image": payload.get("source_image", ""),
                "preprocessed_image": payload.get("preprocessed_image", ""),
                "debug_image": payload.get("debug_image", ""),
                "image_size": payload.get("image_size", {"width": 0, "height": 0}),
                "ocr_box_count": payload.get("ocr_box_count", len(boxes)),
                "boxes": boxes,
                "question_candidates": candidates,
            }
        )
    return samples


def build_question_candidates(
    sample_id: str,
    boxes: list[dict[str, Any]],
    review_store: ReviewStore | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for index, box in enumerate(boxes):
        text = str(box.get("text", "")).strip()
        label = _question_label(text)
        if label is None:
            continue
        candidate_id = f"{sample_id}-q-{len(candidates) + 1}"
        confidence = float(box.get("confidence", 0.0) or 0.0)
        candidates.append(
            {
                "id": candidate_id,
                "box_index": index,
                "label": label,
                "text": text,
                "confidence": confidence,
                "bounds": _bounds_from_points(box.get("points", [])),
                "status": review_store.get_status(sample_id, candidate_id) if review_store else "pending",
            }
        )
    return candidates


def _question_label(text: str) -> str | None:
    for pattern in QUESTION_PATTERNS:
        match = pattern.match(text)
        if match:
            return match.group(1)
    return None


def _bounds_from_points(points: Any) -> dict[str, float]:
    if not points:
        return {"x": 0.0, "y": 0.0, "width": 0.0, "height": 0.0}
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    min_x = min(xs)
    min_y = min(ys)
    return {
        "x": min_x,
        "y": min_y,
        "width": max(xs) - min_x,
        "height": max(ys) - min_y,
    }

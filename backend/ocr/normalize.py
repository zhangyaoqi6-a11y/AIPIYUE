from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from backend.ocr.schema import OcrTextBox


def normalize_paddle_result(raw: Any) -> list[OcrTextBox]:
    boxes: list[OcrTextBox] = []
    for item in _iter_result_items(raw):
        if isinstance(item, dict):
            boxes.extend(_from_dict_result(item))
        elif _is_v2_box(item):
            boxes.append(_from_v2_box(item))
    return boxes


def _iter_result_items(raw: Any) -> Iterable[Any]:
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [raw]
    if not isinstance(raw, list):
        return []
    if len(raw) == 1 and isinstance(raw[0], list) and not _is_v2_box(raw[0]):
        return raw[0]
    return raw


def _from_dict_result(result: dict[str, Any]) -> list[OcrTextBox]:
    texts = result.get("rec_texts") or result.get("texts") or []
    scores = result.get("rec_scores") or result.get("scores") or []
    polys = result.get("dt_polys") or result.get("rec_polys") or result.get("boxes") or []
    boxes: list[OcrTextBox] = []
    for index, text in enumerate(texts):
        points = _points_to_list(polys[index]) if index < len(polys) else []
        confidence = float(scores[index]) if index < len(scores) else 0.0
        boxes.append(OcrTextBox(text=str(text), confidence=confidence, points=points))
    return boxes


def _from_v2_box(item: Any) -> OcrTextBox:
    points = _points_to_list(item[0])
    text_data = item[1]
    text = str(text_data[0])
    confidence = float(text_data[1])
    return OcrTextBox(text=text, confidence=confidence, points=points)


def _is_v2_box(item: Any) -> bool:
    if not isinstance(item, (list, tuple)) or len(item) < 2:
        return False
    text_data = item[1]
    if not _looks_like_points(item[0]) or not isinstance(text_data, (list, tuple)) or len(text_data) < 2:
        return False
    return isinstance(text_data[0], str) and isinstance(text_data[1], (float, int))


def _looks_like_points(value: Any) -> bool:
    if hasattr(value, "tolist"):
        value = value.tolist()
    return isinstance(value, (list, tuple)) and len(value) >= 2 and isinstance(value[0], (list, tuple))


def _points_to_list(value: Any) -> list[list[float]]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    return [[float(point[0]), float(point[1])] for point in value]

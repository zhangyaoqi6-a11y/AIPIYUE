from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OcrTextBox:
    text: str
    confidence: float
    points: list[list[float]]

    def to_dict(self) -> dict[str, object]:
        return {
            "confidence": self.confidence,
            "points": self.points,
            "text": self.text,
        }

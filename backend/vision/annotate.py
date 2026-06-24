from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from backend.ocr.schema import OcrTextBox


def draw_ocr_boxes(image_path: str | Path, boxes: list[OcrTextBox], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as source:
        image = source.convert("RGB")

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for index, box in enumerate(boxes, start=1):
        points = [(float(point[0]), float(point[1])) for point in box.points]
        if len(points) >= 2:
            draw.line(points + [points[0]], fill=(255, 0, 0), width=3)
            label_x, label_y = points[0]
        else:
            label_x, label_y = 0.0, 0.0

        draw.text(
            (label_x, max(0.0, label_y - 14.0)),
            f"{index}:{box.confidence:.2f}",
            fill=(0, 0, 255),
            font=font,
        )

    image.save(output)
    return output

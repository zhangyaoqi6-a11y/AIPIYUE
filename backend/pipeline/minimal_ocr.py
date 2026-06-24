from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from backend.common.paths import ensure_directory, write_json
from backend.ocr.normalize import normalize_paddle_result
from backend.vision.annotate import draw_ocr_boxes
from backend.vision.preprocess import preprocess_page

SUPPORTED_IMAGE_SUFFIXES = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff"}
OcrRunner = Callable[[Path], Any]


@dataclass(frozen=True)
class PageOutput:
    source_image: Path
    preprocessed_image: Path
    ocr_json: Path
    debug_image: Path


def discover_input_images(input_path: str | Path) -> list[Path]:
    path = Path(input_path)
    if path.is_file():
        return [path] if path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES else []
    if not path.exists():
        raise FileNotFoundError(f"Input path does not exist: {path}")
    return sorted(
        file_path
        for file_path in path.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
    )


def run_one_image(image_path: str | Path, output_dir: str | Path, ocr_runner: OcrRunner) -> PageOutput:
    source = Path(image_path)
    target_dir = ensure_directory(output_dir)
    stem = source.stem
    preprocessed_path = target_dir / f"{stem}.preprocessed.png"
    ocr_json_path = target_dir / f"{stem}.ocr.json"
    debug_image_path = target_dir / f"{stem}.ocr-boxes.png"

    preprocess_page(source, preprocessed_path)
    raw_result = ocr_runner(preprocessed_path)
    boxes = normalize_paddle_result(raw_result)
    draw_ocr_boxes(preprocessed_path, boxes, debug_image_path)

    with Image.open(preprocessed_path) as image:
        width, height = image.size

    payload = {
        "boxes": [box.to_dict() for box in boxes],
        "debug_image": str(debug_image_path),
        "image_size": {"height": height, "width": width},
        "ocr_box_count": len(boxes),
        "preprocessed_image": str(preprocessed_path),
        "source_image": str(source),
    }
    write_json(ocr_json_path, payload)
    return PageOutput(
        source_image=source,
        preprocessed_image=preprocessed_path,
        ocr_json=ocr_json_path,
        debug_image=debug_image_path,
    )


def run_batch(input_path: str | Path, output_dir: str | Path, ocr_runner: OcrRunner) -> list[PageOutput]:
    images = discover_input_images(input_path)
    return [run_one_image(image_path, output_dir, ocr_runner) for image_path in images]

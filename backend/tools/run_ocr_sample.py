from __future__ import annotations

import argparse
from pathlib import Path

from backend.ocr.paddle_engine import PaddleOcrEngine
from backend.pipeline.minimal_ocr import run_batch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run minimal paper OCR verification.")
    parser.add_argument("--input", required=True, type=Path, help="Image file or directory.")
    parser.add_argument("--output-dir", default=Path("data/outputs/minimal-ocr"), type=Path)
    parser.add_argument("--lang", default="ch")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    engine = PaddleOcrEngine(lang=args.lang)
    outputs = run_batch(args.input, args.output_dir, engine.recognize)
    for output in outputs:
        print(f"source={output.source_image}")
        print(f"json={output.ocr_json}")
        print(f"debug_image={output.debug_image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

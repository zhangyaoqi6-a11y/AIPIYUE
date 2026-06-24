from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from backend.web.review_app import create_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local OCR review web UI.")
    parser.add_argument("--output-dir", default=Path("data/outputs/minimal-ocr"), type=Path)
    parser.add_argument("--review-path", default=Path("data/reviews/ocr-review.json"), type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8001, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    app = create_app(output_dir=args.output_dir, review_path=args.review_path, project_root=Path.cwd())
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from backend.review.ocr_review import ReviewStore, build_review_samples


class ReviewUpdate(BaseModel):
    sample_id: str
    candidate_id: str
    status: Literal["pending", "correct", "incorrect"]


def create_app(
    output_dir: str | Path = Path("data/outputs/minimal-ocr"),
    review_path: str | Path = Path("data/reviews/ocr-review.json"),
    project_root: str | Path = Path("."),
) -> FastAPI:
    root = Path(project_root).resolve()
    output_root = Path(output_dir).resolve()
    reviews = ReviewStore(review_path)
    static_dir = Path(__file__).parent / "static"

    app = FastAPI(title="AI 智能批阅机 OCR 验收")

    @app.get("/", response_class=HTMLResponse)
    def index() -> FileResponse:
        return FileResponse(static_dir / "review.html")

    @app.get("/static/{filename}")
    def static_file(filename: str) -> FileResponse:
        path = (static_dir / filename).resolve()
        if path.parent != static_dir.resolve() or not path.exists():
            raise HTTPException(status_code=404)
        return FileResponse(path)

    @app.get("/api/samples")
    def samples() -> dict[str, object]:
        return {"samples": build_review_samples(output_root, reviews)}

    @app.post("/api/reviews")
    def update_review(payload: ReviewUpdate) -> dict[str, str]:
        reviews.set_status(payload.sample_id, payload.candidate_id, payload.status)
        return {"status": payload.status}

    @app.get("/files/{relative_path:path}")
    def local_file(relative_path: str) -> FileResponse:
        path = (root / relative_path).resolve()
        if not _is_allowed_file(path, root, output_root):
            raise HTTPException(status_code=404)
        return FileResponse(path)

    return app


def _is_allowed_file(path: Path, project_root: Path, output_root: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    allowed_roots = [project_root / "参考资料", output_root, project_root / "data" / "outputs"]
    return any(_is_relative_to(path, root.resolve()) for root in allowed_roots)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True

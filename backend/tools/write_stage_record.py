from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_ocr_records(output_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(output_dir)
    records: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.ocr.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def build_stage_record(records: list[dict[str, Any]]) -> str:
    lines = [
        "# 第一阶段识别验证记录",
        "",
        "日期：2026-06-24",
        "",
        "## 1. 本次验证目标",
        "",
        "本次只验证最小试卷识别链路：真实图片导入、基础预处理、整页 OCR、JSON 输出、识别框调试图输出。",
        "",
        "## 2. 输出文件汇总",
        "",
        "| 样本 | 识别框数量 | 预处理图 | 调试框图 |",
        "| --- | ---: | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| {source} | {count} | {preprocessed} | {debug} |".format(
                source=record.get("source_image", ""),
                count=record.get("ocr_box_count", 0),
                preprocessed=record.get("preprocessed_image", ""),
                debug=record.get("debug_image", ""),
            )
        )
    lines.extend(
        [
            "",
            "## 3. 人工观察结论",
            "",
            "运行后需要打开调试框图，记录题号、印刷文字、手写答案、阴影、歪斜、裁切边缘对识别效果的具体影响。",
            "",
            "## 4. 下一步工程方向",
            "",
            "下一步不直接用整页 OCR 判分，而是进入模板对齐、题区裁剪、小区域 OCR、规则判分和人工复核流程。",
            "",
        ]
    )
    return "\n".join(lines)


def write_stage_record(output_path: str | Path, records: list[dict[str, Any]]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_stage_record(records), encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write minimal OCR stage record.")
    parser.add_argument("--output-dir", default=Path("data/outputs/minimal-ocr"), type=Path)
    parser.add_argument("--record", default=Path("docs/阶段记录/第一阶段识别验证记录.md"), type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    records = load_ocr_records(args.output_dir)
    record_path = write_stage_record(args.record, records)
    print(f"record={record_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

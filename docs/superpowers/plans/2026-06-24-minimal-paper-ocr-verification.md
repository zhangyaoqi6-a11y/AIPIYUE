# 最小试卷识别验证 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 做出一个最小试卷识别验证版本，能读取 `参考资料` 中的真实试卷图片，完成基础预处理、PaddleOCR 识别、JSON 输出、带识别框调试图输出，并生成阶段记录。

**Architecture:** 先做 Python 脚本流水线，不先做桌面界面和 FastAPI 服务。代码按 `backend/common`、`backend/vision`、`backend/ocr`、`backend/pipeline`、`backend/tools` 拆分，确保后续可以平滑接入 FastAPI 和 Electron。

**Tech Stack:** Python 3.11, OpenCV, Pillow, PaddleOCR, unittest, JSON, Markdown.

---

## 当前基线

- 工作目录：`F:\智能批阅机`
- Git 分支：`main`
- Git 状态：干净，当前 shell 需使用 `C:\Program Files\Git\cmd\git.exe`
- 环境验证命令：`powershell -ExecutionPolicy Bypass -File scripts\verify-env.ps1`
- 环境验证结果：`paddle 3.3.1`、`paddleocr import ok`、`cv2 4.10.0`、`pymupdf 1.27.2.3`、`fastapi import ok`
- 真实样本：
  - `参考资料/微信图片_20260616093037_3804_37.jpg`
  - `参考资料/微信图片_20260616093039_3805_37.jpg`
- `.gitignore` 已忽略：`.env`、`参考资料/`、`data/outputs/`、`data/cache/`

## 方案取舍

推荐方案是脚本优先：先把真实图片的预处理、OCR、JSON 和框图输出跑通，再设计模板对齐和题区裁剪。这个方案最快暴露 PaddleOCR 在真实样本上的问题。

备选方案一是 FastAPI 优先：先搭服务接口，再把 OCR 接进去。这个方案适合产品化，但现在会让接口结构早于样本验证，容易多写无用代码。

备选方案二是桌面界面优先：先做上传和预览界面。这个方案对演示友好，但当前阶段最需要的是识别效果证据，不是界面。

## File Structure

- Create: `backend/__init__.py`
- Create: `backend/common/__init__.py`
- Create: `backend/common/paths.py`
- Create: `backend/vision/__init__.py`
- Create: `backend/vision/preprocess.py`
- Create: `backend/ocr/__init__.py`
- Create: `backend/ocr/schema.py`
- Create: `backend/ocr/normalize.py`
- Create: `backend/ocr/paddle_engine.py`
- Create: `backend/vision/annotate.py`
- Create: `backend/pipeline/__init__.py`
- Create: `backend/pipeline/minimal_ocr.py`
- Create: `backend/tools/__init__.py`
- Create: `backend/tools/run_ocr_sample.py`
- Create: `backend/tools/write_stage_record.py`
- Create: `tests/test_paths.py`
- Create: `tests/test_preprocess.py`
- Create: `tests/test_ocr_normalize.py`
- Create: `tests/test_annotate.py`
- Create: `tests/test_paddle_engine.py`
- Create: `tests/test_minimal_ocr_pipeline.py`
- Create: `tests/test_stage_record.py`
- Create after real run: `docs/阶段记录/第一阶段识别验证记录.md`

---

### Task 1: 公共路径和 JSON 写入工具

**Files:**
- Create: `backend/__init__.py`
- Create: `backend/common/__init__.py`
- Create: `backend/common/paths.py`
- Create: `tests/test_paths.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_paths.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from backend.common.paths import ensure_directory, read_binary, write_json


class PathHelperTests(unittest.TestCase):
    def test_ensure_directory_creates_nested_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "输出" / "嵌套"

            result = ensure_directory(target)

            self.assertEqual(result, target)
            self.assertTrue(target.is_dir())

    def test_read_binary_handles_chinese_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "微信图片_测试.jpg"
            file_path.write_bytes(b"abc")

            self.assertEqual(read_binary(file_path), b"abc")

    def test_write_json_writes_utf8_and_sorted_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "结果" / "ocr.json"

            result = write_json(output_path, {"text": "答案", "score": 1})

            self.assertEqual(result, output_path)
            loaded = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded, {"score": 1, "text": "答案"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_paths -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'backend'`.

- [ ] **Step 3: Write minimal implementation**

Create empty package files:

```python
# backend/__init__.py
```

```python
# backend/common/__init__.py
```

Create `backend/common/paths.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_binary(path: str | Path) -> bytes:
    return Path(path).read_bytes()


def write_json(path: str | Path, payload: dict[str, Any] | list[Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_paths -v
```

Expected: PASS, `Ran 3 tests`.

- [ ] **Step 5: Commit**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add backend tests\test_paths.py
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: add backend path helpers"
```

---

### Task 2: 图片加载、增强和预处理输出

**Files:**
- Create: `backend/vision/__init__.py`
- Create: `backend/vision/preprocess.py`
- Create: `tests/test_preprocess.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_preprocess.py`:

```python
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from backend.vision.preprocess import enhance_page, load_image, preprocess_page, save_image


class PreprocessTests(unittest.TestCase):
    def test_load_image_handles_chinese_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "试卷样本.jpg"
            Image.new("RGB", (120, 80), "white").save(image_path)

            image = load_image(image_path)

            self.assertEqual(image.shape, (80, 120, 3))
            self.assertEqual(image.dtype, np.uint8)

    def test_enhance_page_keeps_shape_and_type(self):
        image = np.full((80, 120, 3), 180, dtype=np.uint8)
        cv2.putText(image, "A", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (40, 40, 40), 2)

        enhanced = enhance_page(image)

        self.assertEqual(enhanced.shape, image.shape)
        self.assertEqual(enhanced.dtype, np.uint8)
        self.assertGreater(int(enhanced.max()), int(enhanced.min()))

    def test_preprocess_page_writes_output_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "微信图片_测试.jpg"
            output_path = Path(tmp) / "输出" / "preprocessed.png"
            Image.new("RGB", (120, 80), "white").save(input_path)

            result = preprocess_page(input_path, output_path)

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())
            written = cv2.imdecode(np.frombuffer(output_path.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
            self.assertEqual(written.shape, (80, 120, 3))

    def test_save_image_handles_chinese_output_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "结果" / "预处理.png"
            image = np.full((10, 12, 3), 255, dtype=np.uint8)

            result = save_image(output_path, image)

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_preprocess -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'backend.vision'`.

- [ ] **Step 3: Write minimal implementation**

Create empty package file:

```python
# backend/vision/__init__.py
```

Create `backend/vision/preprocess.py`:

```python
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


def load_image(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        rgb = ImageOps.exif_transpose(image).convert("RGB")
    return cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)


def enhance_page(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        gray = image
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    background = cv2.GaussianBlur(contrast, (0, 0), sigmaX=15, sigmaY=15)
    normalized = cv2.addWeighted(contrast, 1.5, background, -0.5, 0)
    blur = cv2.GaussianBlur(normalized, (0, 0), sigmaX=3)
    sharpened = cv2.addWeighted(normalized, 1.5, blur, -0.5, 0)
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)


def save_image(path: str | Path, image: np.ndarray) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    extension = ".jpg" if suffix in {".jpg", ".jpeg"} else ".png"
    success, encoded = cv2.imencode(extension, image)
    if not success:
        raise ValueError(f"Cannot encode image for {output_path}")
    output_path.write_bytes(encoded.tobytes())
    return output_path


def preprocess_page(input_path: str | Path, output_path: str | Path) -> Path:
    image = load_image(input_path)
    enhanced = enhance_page(image)
    return save_image(output_path, enhanced)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_preprocess -v
```

Expected: PASS, `Ran 4 tests`.

- [ ] **Step 5: Commit**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add backend\vision tests\test_preprocess.py
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: add page preprocessing"
```

---

### Task 3: 统一 OCR 结果结构和 PaddleOCR 输出转换

**Files:**
- Create: `backend/ocr/__init__.py`
- Create: `backend/ocr/schema.py`
- Create: `backend/ocr/normalize.py`
- Create: `tests/test_ocr_normalize.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_ocr_normalize.py`:

```python
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
                OcrTextBox(text="姓名", confidence=0.98, points=[[0.0, 0.0], [50.0, 0.0], [50.0, 20.0], [0.0, 20.0]]),
                OcrTextBox(text="答案A", confidence=0.87, points=[[0.0, 30.0], [60.0, 30.0], [60.0, 50.0], [0.0, 50.0]]),
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_ocr_normalize -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'backend.ocr'`.

- [ ] **Step 3: Write minimal implementation**

Create empty package file:

```python
# backend/ocr/__init__.py
```

Create `backend/ocr/schema.py`:

```python
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
```

Create `backend/ocr/normalize.py`:

```python
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
    return _looks_like_points(item[0]) and isinstance(text_data, (list, tuple)) and len(text_data) >= 2


def _looks_like_points(value: Any) -> bool:
    if hasattr(value, "tolist"):
        value = value.tolist()
    return isinstance(value, (list, tuple)) and len(value) >= 2 and isinstance(value[0], (list, tuple))


def _points_to_list(value: Any) -> list[list[float]]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    return [[float(point[0]), float(point[1])] for point in value]
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_ocr_normalize -v
```

Expected: PASS, `Ran 4 tests`.

- [ ] **Step 5: Commit**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add backend\ocr tests\test_ocr_normalize.py
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: normalize paddle ocr results"
```

---

### Task 4: PaddleOCR 引擎封装和调试框图绘制

**Files:**
- Create: `backend/ocr/paddle_engine.py`
- Create: `backend/vision/annotate.py`
- Create: `tests/test_annotate.py`
- Create: `tests/test_paddle_engine.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_annotate.py`:

```python
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

from backend.ocr.schema import OcrTextBox
from backend.vision.annotate import draw_ocr_boxes


class AnnotateTests(unittest.TestCase):
    def test_draw_ocr_boxes_writes_changed_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "预处理.png"
            output_path = Path(tmp) / "结果" / "boxed.png"
            Image.new("RGB", (100, 80), "white").save(image_path)
            boxes = [
                OcrTextBox(
                    text="答案",
                    confidence=0.95,
                    points=[[10.0, 10.0], [60.0, 10.0], [60.0, 30.0], [10.0, 30.0]],
                )
            ]

            result = draw_ocr_boxes(image_path, boxes, output_path)

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())
            original = Image.open(image_path).convert("RGB")
            annotated = Image.open(output_path).convert("RGB")
            self.assertIsNotNone(ImageChops.difference(original, annotated).getbbox())


if __name__ == "__main__":
    unittest.main()
```

Create `tests/test_paddle_engine.py`:

```python
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.ocr.paddle_engine import PaddleOcrEngine


class PaddleEngineTests(unittest.TestCase):
    def test_recognize_uses_predict_when_available(self):
        class FakePaddleOCR:
            def __init__(self, lang):
                self.lang = lang
                self.seen_path = None

            def predict(self, path):
                self.seen_path = path
                return [{"rec_texts": ["答案"], "rec_scores": [0.9], "dt_polys": []}]

        with patch("paddleocr.PaddleOCR", FakePaddleOCR):
            engine = PaddleOcrEngine(lang="ch")

        result = engine.recognize(Path("sample.png"))

        self.assertEqual(engine._ocr.lang, "ch")
        self.assertEqual(engine._ocr.seen_path, "sample.png")
        self.assertEqual(result[0]["rec_texts"], ["答案"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_annotate -v
.\.venv\Scripts\python.exe -m unittest tests.test_paddle_engine -v
```

Expected: first command FAILS with `ModuleNotFoundError: No module named 'backend.vision.annotate'`; second command FAILS with `ModuleNotFoundError: No module named 'backend.ocr.paddle_engine'`.

- [ ] **Step 3: Write minimal implementation**

Create `backend/vision/annotate.py`:

```python
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
```

Create `backend/ocr/paddle_engine.py`:

```python
from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class PaddleOcrEngine:
    def __init__(self, lang: str = "ch") -> None:
        os.environ.setdefault("PADDLE_DEVICE", "cpu")
        from paddleocr import PaddleOCR

        self._ocr = PaddleOCR(lang=lang)

    def recognize(self, image_path: str | Path) -> Any:
        path = str(image_path)
        if hasattr(self._ocr, "predict"):
            return self._ocr.predict(path)
        return self._ocr.ocr(path, cls=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_annotate -v
.\.venv\Scripts\python.exe -m unittest tests.test_paddle_engine -v
```

Expected: PASS, `Ran 1 test` for each command.

- [ ] **Step 5: Commit**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add backend\ocr\paddle_engine.py backend\vision\annotate.py tests\test_annotate.py tests\test_paddle_engine.py
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: add ocr debug annotation"
```

---

### Task 5: 最小 OCR 流水线和命令行入口

**Files:**
- Create: `backend/pipeline/__init__.py`
- Create: `backend/pipeline/minimal_ocr.py`
- Create: `backend/tools/__init__.py`
- Create: `backend/tools/run_ocr_sample.py`
- Create: `tests/test_minimal_ocr_pipeline.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_minimal_ocr_pipeline.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from backend.pipeline.minimal_ocr import discover_input_images, run_one_image


class MinimalOcrPipelineTests(unittest.TestCase):
    def test_discover_input_images_returns_supported_files_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "b.png"
            second = root / "a.jpg"
            ignored = root / "note.txt"
            Image.new("RGB", (20, 20), "white").save(first)
            Image.new("RGB", (20, 20), "white").save(second)
            ignored.write_text("not image", encoding="utf-8")

            result = discover_input_images(root)

            self.assertEqual(result, [second, first])

    def test_run_one_image_writes_json_and_debug_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "试卷.jpg"
            output_dir = root / "outputs"
            Image.new("RGB", (100, 80), "white").save(input_path)

            def fake_ocr_runner(image_path: Path):
                self.assertTrue(image_path.exists())
                return [
                    [
                        [[[10, 10], [40, 10], [40, 30], [10, 30]], ("答案A", 0.96)]
                    ]
                ]

            result = run_one_image(input_path, output_dir, fake_ocr_runner)

            self.assertTrue(result.preprocessed_image.exists())
            self.assertTrue(result.debug_image.exists())
            self.assertTrue(result.ocr_json.exists())
            payload = json.loads(result.ocr_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["source_image"], str(input_path))
            self.assertEqual(payload["ocr_box_count"], 1)
            self.assertEqual(payload["boxes"][0]["text"], "答案A")
            self.assertEqual(payload["image_size"], {"height": 80, "width": 100})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_minimal_ocr_pipeline -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'backend.pipeline'`.

- [ ] **Step 3: Write minimal implementation**

Create empty package files:

```python
# backend/pipeline/__init__.py
```

```python
# backend/tools/__init__.py
```

Create `backend/pipeline/minimal_ocr.py`:

```python
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
```

Create `backend/tools/run_ocr_sample.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_minimal_ocr_pipeline -v
```

Expected: PASS, `Ran 2 tests`.

- [ ] **Step 5: Run all unit tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: PASS, `Ran 16 tests`.

- [ ] **Step 6: Commit**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add backend\pipeline backend\tools tests\test_minimal_ocr_pipeline.py
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: add minimal ocr pipeline"
```

---

### Task 6: 阶段记录生成工具

**Files:**
- Create: `backend/tools/write_stage_record.py`
- Create: `tests/test_stage_record.py`
- Create after real run: `docs/阶段记录/第一阶段识别验证记录.md`

- [ ] **Step 1: Write the failing test**

Create `tests/test_stage_record.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from backend.tools.write_stage_record import build_stage_record, load_ocr_records, write_stage_record


class StageRecordTests(unittest.TestCase):
    def test_build_stage_record_contains_sample_summary(self):
        records = [
            {
                "source_image": "参考资料/样本1.jpg",
                "ocr_box_count": 2,
                "preprocessed_image": "data/outputs/minimal-ocr/样本1.preprocessed.png",
                "debug_image": "data/outputs/minimal-ocr/样本1.ocr-boxes.png",
            }
        ]

        markdown = build_stage_record(records)

        self.assertIn("# 第一阶段识别验证记录", markdown)
        self.assertIn("| 参考资料/样本1.jpg | 2 |", markdown)
        self.assertIn("data/outputs/minimal-ocr/样本1.ocr-boxes.png", markdown)

    def test_load_ocr_records_reads_sorted_json_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            second = output_dir / "b.ocr.json"
            first = output_dir / "a.ocr.json"
            second.write_text(json.dumps({"source_image": "b.jpg", "ocr_box_count": 1}), encoding="utf-8")
            first.write_text(json.dumps({"source_image": "a.jpg", "ocr_box_count": 3}), encoding="utf-8")

            records = load_ocr_records(output_dir)

            self.assertEqual([record["source_image"] for record in records], ["a.jpg", "b.jpg"])

    def test_write_stage_record_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "docs" / "阶段记录" / "第一阶段识别验证记录.md"

            result = write_stage_record(output_path, [{"source_image": "a.jpg", "ocr_box_count": 1}])

            self.assertEqual(result, output_path)
            self.assertTrue(output_path.exists())
            self.assertIn("a.jpg", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_stage_record -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'backend.tools.write_stage_record'`.

- [ ] **Step 3: Write minimal implementation**

Create `backend/tools/write_stage_record.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_stage_record -v
```

Expected: PASS, `Ran 3 tests`.

- [ ] **Step 5: Run all unit tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: PASS, `Ran 20 tests`.

- [ ] **Step 6: Commit**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add backend\tools\write_stage_record.py tests\test_stage_record.py
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: add ocr stage record writer"
```

---

### Task 7: 在真实样本上运行最小识别验证

**Files:**
- Modify: `docs/阶段记录/第一阶段识别验证记录.md`
- Generated but ignored by Git: `data/outputs/minimal-ocr/*.preprocessed.png`
- Generated but ignored by Git: `data/outputs/minimal-ocr/*.ocr.json`
- Generated but ignored by Git: `data/outputs/minimal-ocr/*.ocr-boxes.png`

- [ ] **Step 1: Run the real OCR pipeline**

Run:

```powershell
.\.venv\Scripts\python.exe -m backend.tools.run_ocr_sample --input .\参考资料 --output-dir .\data\outputs\minimal-ocr
```

Expected: command exits with code 0 and prints one `json=` path and one `debug_image=` path for each real sample image.

- [ ] **Step 2: Generate the stage record**

Run:

```powershell
.\.venv\Scripts\python.exe -m backend.tools.write_stage_record --output-dir .\data\outputs\minimal-ocr --record .\docs\阶段记录\第一阶段识别验证记录.md
```

Expected: command exits with code 0 and prints `record=docs\阶段记录\第一阶段识别验证记录.md`.

- [ ] **Step 3: Inspect generated JSON**

Run:

```powershell
Get-ChildItem -LiteralPath .\data\outputs\minimal-ocr -Filter *.ocr.json | ForEach-Object { $_.Name; Get-Content -LiteralPath $_.FullName -Encoding UTF8 -TotalCount 40 }
```

Expected: each JSON file contains `source_image`, `preprocessed_image`, `debug_image`, `image_size`, `ocr_box_count`, and `boxes`.

- [ ] **Step 4: Inspect generated debug images**

Open these local files in the Codex app or Windows image viewer:

```text
F:\智能批阅机\data\outputs\minimal-ocr\微信图片_20260616093037_3804_37.ocr-boxes.png
F:\智能批阅机\data\outputs\minimal-ocr\微信图片_20260616093039_3805_37.ocr-boxes.png
```

Record concrete observations in `docs/阶段记录/第一阶段识别验证记录.md` under `## 3. 人工观察结论`:

```markdown
- 样本 `微信图片_20260616093037_3804_37.jpg`：记录 OCR 框是否覆盖题号、答案、干扰文字、手写内容，以及明显漏检或错检位置。
- 样本 `微信图片_20260616093039_3805_37.jpg`：记录 OCR 框是否覆盖题号、答案、干扰文字、手写内容，以及明显漏检或错检位置。
```

- [ ] **Step 5: Run all unit tests again**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: PASS, `Ran 20 tests`.

- [ ] **Step 6: Verify Git status**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' status --short
```

Expected: generated `data/outputs/` and `参考资料/` files do not appear. Only code, tests, and `docs/阶段记录/第一阶段识别验证记录.md` appear if they are not committed yet.

- [ ] **Step 7: Commit**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add backend tests docs\阶段记录\第一阶段识别验证记录.md
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: run minimal paper ocr verification"
```

---

## Final Verification

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify-env.ps1
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m backend.tools.run_ocr_sample --input .\参考资料 --output-dir .\data\outputs\minimal-ocr
.\.venv\Scripts\python.exe -m backend.tools.write_stage_record --output-dir .\data\outputs\minimal-ocr --record .\docs\阶段记录\第一阶段识别验证记录.md
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
```

Expected:

- Environment imports still pass.
- Unit tests pass with `Ran 20 tests`.
- Real OCR command writes JSON and debug images for both reference images.
- Stage record exists at `docs/阶段记录/第一阶段识别验证记录.md`.
- `参考资料/` and `data/outputs/` remain ignored.

## Self-Review

- Spec coverage: covers real image loading, preprocessing, PaddleOCR call, JSON output, boxed debug image output, sample effect review, and next-step template alignment direction.
- Scope control: does not build Electron, FastAPI routes, student roster, parent app, mini program, or final grading logic.
- Type consistency: OCR result shape is normalized into `OcrTextBox` and serialized through `to_dict()`.
- Test strategy: no production module is created without a failing unittest step first.

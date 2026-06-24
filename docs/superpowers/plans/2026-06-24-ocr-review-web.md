# OCR Review Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个本地 FastAPI 验收网页，直观看到真实试卷 OCR 框、题目候选、识别文本和人工正确性标注。

**Architecture:** Python 后端读取现有 OCR JSON 和图片文件，生成网页所需数据；FastAPI 提供页面、API 和本地图片访问；前端用无构建 HTML/CSS/JS，避免过早引入 Electron 或 React。

**Tech Stack:** Python 3.11, FastAPI, unittest, HTML, CSS, JavaScript.

---

## File Structure

- Create: `backend/review/__init__.py`
- Create: `backend/review/ocr_review.py`
- Create: `backend/web/__init__.py`
- Create: `backend/web/review_app.py`
- Create: `backend/web/static/review.html`
- Create: `backend/web/static/review.css`
- Create: `backend/web/static/review.js`
- Create: `backend/tools/run_review_web.py`
- Create: `tests/test_ocr_review.py`
- Create: `tests/test_review_app.py`
- Modify: `docs/项目交接说明.md`

## Tasks

### Task 1: Review 数据解析

- [ ] 写 `tests/test_ocr_review.py`，覆盖 OCR JSON 加载、题目候选抽取、人工状态保存。
- [ ] 运行测试，确认因 `backend.review` 缺失而失败。
- [ ] 实现 `backend/review/ocr_review.py`。
- [ ] 运行测试，确认通过。

### Task 2: FastAPI 验收服务

- [ ] 写 `tests/test_review_app.py`，覆盖 `/api/samples`、`/api/reviews`、图片路径安全。
- [ ] 运行测试，确认因 `backend.web.review_app` 缺失而失败。
- [ ] 实现 `backend/web/review_app.py` 和 `backend/tools/run_review_web.py`。
- [ ] 运行测试，确认通过。

### Task 3: 网页界面

- [ ] 创建 `review.html`、`review.css`、`review.js`。
- [ ] 页面展示样本列表、真实图 OCR 框、题目候选、状态按钮。
- [ ] 运行本地服务，用真实样本检查页面。

### Task 4: 验证和交接

- [ ] 运行全部单元测试。
- [ ] 启动网页并截图检查。
- [ ] 更新 `docs/项目交接说明.md`。
- [ ] 提交并推送。

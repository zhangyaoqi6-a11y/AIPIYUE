$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "setup-env.ps1")

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

& $PythonExe -c "import paddle; print('paddle', paddle.__version__)"
& $PythonExe -c "import paddleocr; print('paddleocr import ok')"
& $PythonExe -c "import cv2; print('cv2', cv2.__version__)"
& $PythonExe -c "import fitz; print('pymupdf', fitz.version[0])"
& $PythonExe -c "import fastapi; print('fastapi import ok')"

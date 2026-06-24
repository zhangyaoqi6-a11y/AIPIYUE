$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $ProjectRoot "data"
$CacheDir = Join-Path $DataDir "cache"

New-Item -ItemType Directory -Force (Join-Path $DataDir "uploads") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $DataDir "outputs") | Out-Null
New-Item -ItemType Directory -Force $CacheDir | Out-Null
New-Item -ItemType Directory -Force (Join-Path $CacheDir "paddle") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $CacheDir "paddlex") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $CacheDir "huggingface") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $CacheDir "modelscope") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $DataDir "home") | Out-Null

$env:APP_ENV = "development"
$env:APP_HOST = "127.0.0.1"
$env:APP_PORT = "8000"
$env:DATA_DIR = Join-Path $ProjectRoot "data"
$env:UPLOAD_DIR = Join-Path $DataDir "uploads"
$env:OUTPUT_DIR = Join-Path $DataDir "outputs"
$env:OCR_ENGINE = "paddleocr"
$env:OCR_LANG = "ch"
$env:PADDLE_DEVICE = "cpu"
$env:HOME = Join-Path $DataDir "home"
$env:USERPROFILE = Join-Path $DataDir "home"
$env:XDG_CACHE_HOME = $CacheDir
$env:PADDLE_HOME = Join-Path $CacheDir "paddle"
$env:PADDLE_PDX_CACHE_HOME = Join-Path $CacheDir "paddlex"
$env:HF_HOME = Join-Path $CacheDir "huggingface"
$env:MODELSCOPE_CACHE = Join-Path $CacheDir "modelscope"

Write-Host "Project environment variables loaded for this PowerShell session."

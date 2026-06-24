$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $ProjectRoot "data"

function Test-AsciiPath {
    param([string]$Path)
    return $Path -cmatch '^[\x00-\x7F]+$'
}

if (Test-AsciiPath $ProjectRoot) {
    $CacheDir = Join-Path $DataDir "cache"
    $HomeDir = Join-Path $DataDir "home"
} else {
    $DriveRoot = [System.IO.Path]::GetPathRoot($ProjectRoot)
    $CacheDir = Join-Path $DriveRoot "aipiyue_cache"
    $HomeDir = Join-Path $DriveRoot "aipiyue_home"
}

New-Item -ItemType Directory -Force (Join-Path $DataDir "uploads") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $DataDir "outputs") | Out-Null
New-Item -ItemType Directory -Force $CacheDir | Out-Null
New-Item -ItemType Directory -Force (Join-Path $CacheDir "paddle") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $CacheDir "paddlex") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $CacheDir "huggingface") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $CacheDir "modelscope") | Out-Null
New-Item -ItemType Directory -Force $HomeDir | Out-Null

$env:APP_ENV = "development"
$env:APP_HOST = "127.0.0.1"
$env:APP_PORT = "8000"
$env:DATA_DIR = Join-Path $ProjectRoot "data"
$env:UPLOAD_DIR = Join-Path $DataDir "uploads"
$env:OUTPUT_DIR = Join-Path $DataDir "outputs"
$env:OCR_ENGINE = "paddleocr"
$env:OCR_LANG = "ch"
$env:PADDLE_DEVICE = "cpu"
$env:HOME = $HomeDir
$env:USERPROFILE = $HomeDir
$env:XDG_CACHE_HOME = $CacheDir
$env:PADDLE_HOME = Join-Path $CacheDir "paddle"
$env:PADDLE_PDX_CACHE_HOME = Join-Path $CacheDir "paddlex"
$env:HF_HOME = Join-Path $CacheDir "huggingface"
$env:MODELSCOPE_CACHE = Join-Path $CacheDir "modelscope"
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"

Write-Host "Project environment variables loaded for this PowerShell session."
Write-Host "Model cache root: $CacheDir"

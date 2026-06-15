# Exness Trading Backend 安装和启动脚本 (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Exness Trading Backend 安装和启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
Set-Location $PSScriptRoot

# 检查Python
Write-Host "[1/4] 检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [错误] 未找到 Python,请先安装 Python 3.9+" -ForegroundColor Red
    pause
    exit 1
}

# 升级pip
Write-Host ""
Write-Host "[2/4] 升级 pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# 安装依赖
Write-Host ""
Write-Host "[3/4] 安装依赖包 (这可能需要几分钟)..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "  [错误] 依赖安装失败" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "  依赖安装成功!" -ForegroundColor Green

# 创建日志目录
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "  [警告] 未找到 .env 文件,正在创建..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  [提示] 请编辑 .env 文件配置环境变量" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] 启动 FastAPI 服务..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服务即将启动..." -ForegroundColor Green
Write-Host "API文档地址: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "健康检查: http://localhost:8000/health" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 启动服务
python main.py

pause

# Exness Trading Backend 启动脚本 (PowerShell版本)
# 使用方法: 右键此文件 -> "使用PowerShell运行"

# 设置编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 切换到脚本所在目录
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Exness Trading Backend - 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步骤1: 检查Python
Write-Host "[步骤 1/4] 检查 Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [错误] 未找到 Python!" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装 Python 3.9+:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}

# 步骤2: 检查pip
Write-Host ""
Write-Host "[步骤 2/4] 检查 pip..." -ForegroundColor Yellow
try {
    $pipVersion = & python -m pip --version 2>&1
    Write-Host "  $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "  [错误] 未找到 pip!" -ForegroundColor Red
    pause
    exit 1
}

# 步骤3: 检查并安装依赖
Write-Host ""
Write-Host "[步骤 3/4] 检查依赖包..." -ForegroundColor Yellow
try {
    & python -c "import fastapi" 2>&1 | Out-Null
    Write-Host "  [成功] 依赖包已安装" -ForegroundColor Green
} catch {
    Write-Host "  [警告] 依赖包未安装,正在安装..." -ForegroundColor Yellow
    Write-Host ""
    & python -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  [错误] 依赖安装失败!" -ForegroundColor Red
        Write-Host "  请尝试手动运行: pip install -r requirements.txt" -ForegroundColor Yellow
        pause
        exit 1
    }
    Write-Host ""
    Write-Host "  [成功] 依赖安装完成" -ForegroundColor Green
}

# 创建日志目录
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# 步骤4: 启动服务
Write-Host ""
Write-Host "[步骤 4/4] 启动 FastAPI 服务..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服务启动中..." -ForegroundColor Green
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "健康检查: http://localhost:8000/health" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 使用uvicorn启动服务
& python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Write-Host ""
Write-Host "服务已停止" -ForegroundColor Yellow
pause

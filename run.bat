@echo off
chcp 65001 >nul
echo ========================================
echo 启动 Exness Trading Backend 服务
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python!
    echo 请先安装 Python 3.9+: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 创建日志目录
if not exist logs mkdir logs

REM 启动服务(使用uvicorn)
echo [提示] 正在启动 FastAPI 服务...
echo [提示] API文档: http://localhost:8000/docs
echo [提示] 健康检查: http://localhost:8000/health
echo [提示] 按 Ctrl+C 停止服务
echo ========================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 服务已停止
pause

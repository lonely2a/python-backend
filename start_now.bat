@echo off
chcp 65001 >nul
echo ========================================
echo Exness Trading Backend - 快速启动
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 设置Python路径
set PYTHON_PATH=C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python.exe

REM 检查Python是否存在
if not exist "%PYTHON_PATH%" (
    echo [错误] Python未找到: %PYTHON_PATH%
    echo 请确认Python已安装
    pause
    exit /b 1
)

REM 创建日志目录
if not exist logs mkdir logs

REM 启动服务
echo [提示] 正在启动 FastAPI 服务...
echo [提示] API文档: http://localhost:8000/docs
echo [提示] 健康检查: http://localhost:8000/health
echo [提示] 按 Ctrl+C 停止服务
echo ========================================
echo.

"%PYTHON_PATH%" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 服务已停止
pause

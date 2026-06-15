@echo off
chcp 65001 >nul
echo ========================================
echo Exness Trading Backend - 诊断和启动工具
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 步骤1: 检查Python
echo [步骤 1/4] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python!
    echo.
    echo 请先安装 Python 3.9+:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo [成功] Python 已安装
echo.

REM 步骤2: 检查pip
echo [步骤 2/4] 检查 pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 pip!
    pause
    exit /b 1
)

python -m pip --version
echo [成功] pip 已安装
echo.

REM 步骤3: 检查依赖
echo [步骤 3/4] 检查依赖包...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [警告] 依赖包未安装,正在安装...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [错误] 依赖安装失败!
        echo 请尝试手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo [成功] 依赖安装完成
) else (
    echo [成功] 依赖包已安装
)
echo.

REM 步骤4: 创建日志目录
if not exist logs mkdir logs

REM 步骤5: 启动服务
echo [步骤 4/4] 启动 FastAPI 服务...
echo.
echo ========================================
echo 服务启动中...
echo API文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

REM 使用uvicorn直接启动(更可靠)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 服务已停止
pause

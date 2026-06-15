@echo off
chcp 65001 >nul
echo ========================================
echo Exness Trading Backend - 环境诊断工具
echo ========================================
echo.

REM 切换到项目目录
cd /d "%~dp0"

echo [步骤 1/5] 检查 Python 安装...
echo.

REM 尝试多个可能的Python路径
set PYTHON_FOUND=0

REM 方法1: 直接python命令
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] 找到 Python:
    python --version
    set PYTHON_PATH=python
    set PYTHON_FOUND=1
    goto :install_deps
)

REM 方法2: WindowsApps路径
if exist "C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python.exe" (
    echo [成功] 找到 Python 在 WindowsApps:
    "C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python.exe" --version
    set PYTHON_PATH="C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python.exe"
    set PYTHON_FOUND=1
    goto :install_deps
)

REM 方法3: Program Files路径
if exist "C:\Program Files\Python311\python.exe" (
    echo [成功] 找到 Python 3.11:
    "C:\Program Files\Python311\python.exe" --version
    set PYTHON_PATH="C:\Program Files\Python311\python.exe"
    set PYTHON_FOUND=1
    goto :install_deps
)

if exist "C:\Program Files\Python312\python.exe" (
    echo [成功] 找到 Python 3.12:
    "C:\Program Files\Python312\python.exe" --version
    set PYTHON_PATH="C:\Program Files\Python312\python.exe"
    set PYTHON_FOUND=1
    goto :install_deps
)

if exist "C:\Program Files\Python39\python.exe" (
    echo [成功] 找到 Python 3.9:
    "C:\Program Files\Python39\python.exe" --version
    set PYTHON_PATH="C:\Program Files\Python39\python.exe"
    set PYTHON_FOUND=1
    goto :install_deps
)

REM 如果都没找到
if %PYTHON_FOUND% equ 0 (
    echo [错误] 未找到 Python!
    echo.
    echo 请按照以下步骤安装 Python:
    echo.
    echo 1. 访问: https://www.python.org/downloads/
    echo 2. 下载 Python 3.11 或 3.12 (Windows 64-bit)
    echo 3. 安装时务必勾选 "Add Python to PATH"
    echo 4. 安装完成后,重新运行此脚本
    echo.
    pause
    exit /b 1
)

:install_deps
echo.
echo [步骤 2/5] 检查并升级 pip...
%PYTHON_PATH% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] pip 不可用
    pause
    exit /b 1
)

%PYTHON_PATH% -m pip install --upgrade pip --quiet
echo [成功] pip 已升级
echo.

echo [步骤 3/5] 检查依赖包...
%PYTHON_PATH% -c "import fastapi" >nul 2>&1
if %errorlevel% equ 0 (
    echo [提示] 部分依赖已安装
) else (
    echo [提示] 需要安装依赖包
)
echo.

echo [步骤 4/5] 安装/更新依赖包 (这可能需要几分钟)...
echo.
%PYTHON_PATH% -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [错误] 依赖安装失败!
    echo 请检查网络连接或尝试手动安装
    pause
    exit /b 1
)

echo.
echo [成功] 依赖安装完成!
echo.

echo [步骤 5/5] 创建日志目录...
if not exist logs mkdir logs
echo [成功] 日志目录已创建
echo.

echo ========================================
echo 环境配置完成!即将启动服务...
echo ========================================
echo.
echo API文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo 按 Ctrl+C 停止服务
echo.

REM 启动服务
%PYTHON_PATH% -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 服务已停止
pause

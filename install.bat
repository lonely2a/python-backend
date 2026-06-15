@echo off
echo ========================================
echo Exness Trading Backend 安装脚本
echo ========================================
echo.

REM 检查Python版本
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python,请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [1/4] 检查 Python 环境...
python -c "import sys; print(f'Python 版本: {sys.version}')"

REM 升级pip
echo.
echo [2/4] 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo.
echo [3/4] 安装依赖包...
pip install -r requirements.txt

if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

REM 创建日志目录
if not exist logs mkdir logs

REM 检查.env文件
if not exist .env (
    echo.
    echo [警告] 未找到 .env 文件,正在创建...
    copy .env.example .env >nul
    echo [提示] 请编辑 .env 文件配置环境变量
)

echo.
echo [4/4] 安装完成!
echo.
echo ========================================
echo 下一步:
echo 1. 编辑 .env 文件配置环境变量
echo 2. 运行 python main.py 启动服务
echo 3. 访问 http://localhost:8000/docs 查看API文档
echo ========================================
echo.
pause

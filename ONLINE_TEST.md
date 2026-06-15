# 🌐 Exness Trading Backend - 在线测试方案

由于本地Python环境问题,我们提供以下在线测试方案:

---

## 方案1: Google Colab (推荐) ⭐

### 优点:
- ✅ 完全免费,无需安装任何东西
- ✅ 有GPU支持,运行速度快
- ✅ 可以直接在浏览器中运行和测试代码

### 步骤:

#### 1. 打开Google Colab
访问: https://colab.research.google.com/

#### 2. 创建新笔记本
点击 "New Notebook" → 选择 Python 3

#### 3. 复制粘贴以下代码到第一个单元格:

```python
# 安装依赖
!pip install fastapi uvicorn pydantic httpx requests nest-asyncio -q
print("✅ 依赖安装完成")

# 导入库
import asyncio
import nest_asyncio
nest_asyncio.apply()
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json

# 创建FastAPI应用
app = FastAPI(title="Exness Trading Backend - Test")

# 数据模型
class LoginRequest(BaseModel):
    login: int
    password: str
    server: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    account_info: Optional[dict] = None

# API端点
@app.get("/")
async def root():
    return {"message": "Exness Trading Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    return LoginResponse(
        success=True,
        message=f"登录成功: {request.login} @ {request.server}",
        account_info={
            "login": request.login,
            "balance": 1000.0,
            "equity": 1000.0,
            "leverage": 2000,
            "server": request.server
        }
    )

@app.get("/api/account/info")
async def get_account_info(login: int):
    return {
        "login": login,
        "balance": 1000.0,
        "equity": 1050.0,
        "margin": 10.0,
        "free_margin": 1040.0,
        "leverage": 2000,
        "server": "Exness-Demo"
    }

@app.get("/api/market/quote/{symbol}")
async def get_quote(symbol: str):
    import random
    base_price = 1.0850 if symbol == "EURUSD" else 1.2650
    return {
        "symbol": symbol,
        "bid": base_price + random.uniform(-0.001, 0.001),
        "ask": base_price + random.uniform(0.0005, 0.0015)
    }

print("✅ FastAPI应用创建成功!")
```

#### 4. 点击 "Play" 按钮运行

#### 5. 启动服务器并测试:

创建第二个单元格,粘贴:

```python
# 安装ngrok用于暴露服务
!pip install pyngrok flask-ngrok -q

# 启动服务器
import threading
import uvicorn

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 在后台线程中运行
thread = threading.Thread(target=run_server, daemon=True)
thread.start()

print("✅ 服务器已启动!")
print("📖 注意: Colab中无法直接访问localhost,需要使用ngrok或下载代码到本地运行")
```

---

## 方案2: Replit (最简单) 🚀

### 优点:
- ✅ 完全在线,无需任何配置
- ✅ 自动部署,立即获得公网URL
- ✅ 支持多人协作

### 步骤:

#### 1. 注册Replit
访问: https://replit.com/signup

#### 2. 创建新项目
- 点击 "Create Repl"
- 选择模板: **Python**
- 项目名称: `exness-trading-backend`

#### 3. 上传项目文件
- 点击 "Upload files"
- 选择 `E:\Code\CryptoAssist\python-backend` 目录中的所有文件
- 或者手动创建文件并复制内容

#### 4. 修改main.py
在Replit中,将 `main.py` 的最后部分改为:

```python
if __name__ == "__main__":
    import uvicorn
    
    # Replit会自动分配端口
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Replit中不需要reload
    )
```

#### 5. 点击 "Run" 按钮

Replit会自动:
- 安装依赖(从requirements.txt)
- 启动服务器
- 生成一个公网URL (如: https://exness-trading-backend.yourusername.repl.co)

#### 6. 访问API文档
在生成的URL后添加 `/docs`:
```
https://exness-trading-backend.yourusername.repl.co/docs
```

---

## 方案3: Render.com (生产级部署) 🏭

### 优点:
- ✅ 免费层级可用
- ✅ 自动HTTPS
- ✅ 适合长期运行

### 步骤:

#### 1. 注册Render
访问: https://render.com/

#### 2. 连接GitHub
- 先将项目推送到GitHub
- 在Render中连接GitHub账号

#### 3. 创建Web Service
- 选择你的GitHub仓库
- 设置:
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 4. 部署
点击 "Create Web Service",等待部署完成

#### 5. 访问
Render会提供一个URL,如: `https://exness-trading.onrender.com`

---

## 方案4: 使用Docker + 在线容器平台 

### 平台推荐:
- **GitPod**: https://www.gitpod.io/
- **CodeSandbox**: https://codesandbox.io/
- **StackBlitz**: https://stackblitz.com/

### Dockerfile (放在python-backend目录):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🎯 推荐方案对比

| 方案 | 难度 | 速度 | 适用场景 | 推荐度 |
|------|------|------|----------|--------|
| **Replit** | ⭐ 简单 | 快 | 快速测试、演示 | ⭐⭐⭐⭐⭐ |
| **Google Colab** | ⭐⭐ 中等 | 快 | 学习、实验 | ⭐⭐⭐⭐ |
| **Render.com** | ⭐⭐⭐ 较难 | 中 | 生产部署 | ⭐⭐⭐⭐ |
| **GitPod** | ⭐⭐ 较难 | 中 | 开发环境 | ⭐⭐⭐ |

---

## 💡 我的建议

**对于你现在的情况,我强烈推荐使用 Replit:**

1. **最快上手**: 5分钟内就能运行
2. **零配置**: 不需要处理Python环境问题
3. **立即可用**: 自动生成公网URL,手机也能访问
4. **免费**: 完全免费使用

### 快速开始Replit:

1. 访问: https://replit.com/languages/python3
2. 点击 "Start coding"
3. 在左侧文件树中,右键 → "Upload files"
4. 上传 `E:\Code\CryptoAssist\python-backend` 中的所有文件
5. 点击右上角 "Run" 按钮
6. 等待几秒,服务就会启动!

---

## ❓ 需要帮助?

如果你在使用在线平台时遇到问题,请告诉我:
1. 你选择了哪个平台?
2. 遇到了什么错误?
3. 截图给我看

我会帮你解决!

---

**你想现在试试哪个方案?我可以提供更详细的指导!** 🚀

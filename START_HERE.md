# 🚀 启动后端服务 - 简单三步

## 方式一: 双击脚本启动 (推荐)

### Windows用户:
1. **安装依赖** (首次运行):
   - 双击 `install.bat`
   - 等待安装完成

2. **启动服务**:
   - 双击 `run.bat`
   - 看到 "Uvicorn running on http://0.0.0.0:8000" 表示成功

3. **访问API文档**:
   - 打开浏览器访问: http://localhost:8000/docs

---

## 方式二: 命令行启动

### 步骤1: 打开命令行
按 `Win+R`,输入 `cmd`,回车

### 步骤2: 进入项目目录
```cmd
cd E:\Code\CryptoAssist\python-backend
```

### 步骤3: 安装依赖 (首次运行)
```cmd
pip install -r requirements.txt
```

### 步骤4: 启动服务
```cmd
python main.py
```

### 步骤5: 验证启动
看到以下输出表示成功:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
==================================================
Exness Trading Assistant Backend 启动中...
API文档地址: http://0.0.0.0:8000/docs
==================================================
```

---

## 访问服务

启动成功后,打开浏览器访问:

- **API文档 (Swagger UI)**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc  
- **健康检查**: http://localhost:8000/health

---

## 测试API

### 1. 在Swagger UI中测试

1. 访问 http://localhost:8000/docs
2. 展开 `/api/auth/login` 接口
3. 点击 "Try it out"
4. 输入测试数据:
   ```json
   {
     "login": 12345678,
     "password": "your_password", 
     "server": "Exness-Demo"
   }
   ```
5. 点击 "Execute"
6. 查看响应结果

### 2. 使用curl命令测试

```cmd
REM 健康检查
curl http://localhost:8000/health

REM 登录接口
curl -X POST "http://localhost:8000/api/auth/login" ^
-H "Content-Type: application/json" ^
-d "{\"login\": 12345678, \"password\": \"your_password\", \"server\": \"Exness-Demo\"}"
```

---

## ❓ 常见问题

### Q1: 提示 "端口被占用"?
**解决**: 
```cmd
REM 查找占用8000端口的进程
netstat -ano | findstr :8000

REM 关闭进程或更改端口
python main.py --port 8001
```

### Q2: 提示 "ModuleNotFoundError"?
**解决**: 重新安装依赖
```cmd
pip install -r requirements.txt
```

### Q3: MT5初始化失败?
**解决**: 
- 确认已安装MetaTrader 5终端
- 检查MT5是否能正常手动登录
- 编辑 `.env` 文件,设置正确的MT5路径

### Q4: 无法访问 http://localhost:8000/docs?
**解决**:
- 确认服务已启动(看命令行输出)
- 检查防火墙是否允许8000端口
- 尝试 http://127.0.0.1:8000/docs

---

## 📞 需要帮助?

如果遇到问题:
1. 查看日志文件: `logs/app_*.log`
2. 阅读 README.md 的常见问题部分
3. 查看 QUICKSTART.md 快速启动指南

---

**祝你使用愉快!** 🎉

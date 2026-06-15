# Python后端快速启动指南

## 📋 前置条件

在启动之前,请确保满足以下条件:

1. ✅ **Python 3.9+** 已安装
2. ✅ **MetaTrader 5终端** 已安装在Windows系统上
3. ✅ **Exness MT5账户** (建议使用Demo账户测试)

## 🚀 三步启动

### 步骤1: 安装依赖

双击运行 `install.bat` 或在命令行执行:

```bash
cd python-backend
pip install -r requirements.txt
```

### 步骤2: 配置环境(可选)

如果需要修改配置,编辑 `.env` 文件:

```bash
# 生产环境必须修改JWT密钥
SECRET_KEY=your-random-secret-key-here

# 如果MT5安装在非默认路径,取消注释并设置
# MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
```

### 步骤3: 启动服务

双击运行 `run.bat` 或在命令行执行:

```bash
cd python-backend
python main.py
```

## ✅ 验证启动

服务启动后,打开浏览器访问:

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

如果能看到Swagger UI界面,说明启动成功! 

## 🧪 测试API

### 方法一: 使用Swagger UI (推荐)

1. 访问 http://localhost:8000/docs
2. 展开 `/api/auth/login` 接口
3. 点击 "Try it out"
4. 输入Exness账户信息:
   ```json
   {
     "login": 12345678,
     "password": "your_password",
     "server": "Exness-Demo"
   }
   ```
5. 点击 "Execute" 执行请求
6. 查看响应结果

### 方法二: 使用测试脚本

```bash
cd python-backend/tests
python test_api.py
```

按提示输入Exness Demo账户信息进行完整测试。

## 📱 常用操作

### 查看日志

日志文件位于 `logs/` 目录:

```bash
# Windows PowerShell
Get-Content logs\app_2026-06-13.log -Tail 50 -Wait

# 或直接打开文件
notepad logs\app_2026-06-13.log
```

### 停止服务

在运行服务的命令行窗口按 `Ctrl+C`

### 重启服务

1. 按 `Ctrl+C` 停止当前服务
2. 重新运行 `python main.py`

## ❓ 常见问题排查

### 问题1: 端口被占用

**错误信息**: `OSError: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8000)`

**解决方案**:
```bash
# 方式1: 更改端口
python main.py --port 8001

# 方式2: 关闭占用8000端口的进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

### 问题2: MT5初始化失败

**错误信息**: `MT5初始化失败`

**排查步骤**:
1. 确认已安装MetaTrader 5终端
2. 检查MT5是否能正常手动登录
3. 尝试指定MT5路径:
   ```bash
   # 编辑 .env 文件
   MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
   ```

### 问题3: 登录失败

**错误信息**: `登录失败: ...`

**排查步骤**:
1. 检查账号、密码是否正确
2. 确认服务器名称正确 (如 `Exness-Demo`, `Exness-Real16`)
3. 在MT5终端中手动登录验证
4. 查看日志文件获取详细错误信息

### 问题4: 依赖安装失败

**错误信息**: `Could not find a version that satisfies the requirement...`

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 🔗 下一步

Python后端启动成功后,可以:

1. **浏览API文档**: http://localhost:8000/docs
2. **测试所有接口**: 参考 README.md 中的API示例
3. **开始Android开发**: 等待前端团队接入

## 📞 需要帮助?

如果遇到无法解决的问题:

1. 查看日志文件: `logs/app_*.log`
2. 检查项目README.md的常见问题部分
3. 提交Issue或联系开发者

---

**祝你开发顺利!** 🚀

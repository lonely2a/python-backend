# 🚀 Replit 快速启动指南

##  当前状态

✅ 代码已成功从GitHub导入到Replit  
️ 运行在 **Mock Mode** (模拟模式) - 因为Replit是Linux环境,MetaTrader5需要Windows

##  立即启动(3步)

### 步骤1: 等待AI完成配置

看到右侧AI对话框了吗?它会帮你:
- ✅ 安装Python依赖
- ✅ 创建Mock MT5模块
- ✅ 配置启动脚本

**等待AI显示 "Setup complete" 或类似消息**。

### 步骤2: 点击 Run 按钮

点击右上角绿色的 **"Run"** 按钮。

### 步骤3: 查看输出并访问

成功后会看到:
```
🚀 Exness Trading Backend 启动中...
📍 运行模式: Mock Mode (模拟MT5)
🔌 服务端口: 5000
 API文档: /docs
```

然后访问右侧显示的URL + `/docs`,例如:
```
https://exness-trading-backend.xiang1245306697.repl.co/docs
```

---

##  如果AI没有自动配置

### 手动配置步骤:

#### 1. 修改 .replit 文件

找到左侧的 `.replit` 文件,改为:

```toml
entrypoint = "main_replit_final.py"

[deployment]
run = ["python", "main_replit_final.py"]
build = ["pip", "install", "-r", "requirements.txt"]
```

#### 2. 点击 Run 按钮

#### 3. 等待启动完成

---

##  测试API

启动成功后:

1. **打开API文档**: URL + `/docs`
2. **测试健康检查**: `GET /health`
3. **测试登录**: `POST /api/auth/login`
4. **测试其他接口**

所有接口都会返回模拟数据,可以完整测试业务流程!

---

##  重要提示

- ⚠️ 当前是 **Mock模式**,数据是模拟的
- ️ MetaTrader5库需要 **Windows系统**
- 要测试真实MT5连接,需要在 **本地Windows环境** 运行
- Replit版本适合测试 **API结构和业务流程**

---

##  下一步

1. ✅ 在Replit中测试所有API接口
2.  学习API的使用方法
3.  开始Android前端开发
4.  在本地Windows环境部署真实MT5版本

---

**准备好了吗?点击 Run 按钮开始吧!** 

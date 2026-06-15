# Exness Trading Backend - Replit 部署说明

## ⚠️ 重要提示

**当前运行在 Mock Mode (模拟模式)**

由于 **MetaTrader5 库仅支持 Windows 操作系统**,而 Replit 运行在 Linux 环境,因此:

- ✅ 所有API接口都可以正常测试
- ✅ 业务逻辑和代码结构完全一致  
- ⚠️ 数据是模拟的,不是真实的MT5连接
- ️ 无法执行真实的交易操作

## 🚀 在 Replit 中启动

### 方法1: 使用AI自动配置(推荐)

Replit的AI会自动:
1. 安装Python依赖
2. 检测环境并切换到Mock模式
3. 启动服务

等待AI完成配置后,点击右上角的 **"Run"** 按钮即可。

### 方法2: 手动启动

如果AI没有自动配置,可以手动执行:

#### 步骤1: 修改 .replit 文件

确保 `.replit` 文件内容如下:

```toml
entrypoint = "main_replit_final.py"
modules = ["python-3.10:v1.20240430"]

[env]
PYTHONUNBUFFERED = "1"
PYTHONDONTWRITEBYTECODE = "1"

[nix]
channel = "stable-23_11"

[deployment]
run = ["python", "main_replit_final.py"]
build = ["pip", "install", "-r", "requirements.txt"]
```

#### 步骤2: 点击 Run 按钮

点击右上角绿色的 **"Run"** 按钮,等待服务启动。

#### 步骤3: 查看控制台输出

成功的标志是看到:

```
============================================================
🚀 Exness Trading Backend 启动中...
📍 运行模式: Mock Mode (模拟MT5)
🔌 服务端口: 5000
 API文档: /docs
 健康检查: /health
⚠️  注意: 当前使用模拟数据,非真实MT5连接
============================================================
INFO:     Uvicorn running on http://0.0.0.0:5000
```

## 📖 访问API文档

服务启动后,在右侧面板会显示你的项目URL,例如:

```
https://exness-trading-backend.xiang1245306697.repl.co
```

访问API文档:

```
https://exness-trading-backend.xiang1245306697.repl.co/docs
```

##  测试API

### 1. 健康检查

```
GET /health
```

响应:
```json
{
  "status": "healthy",
  "service": "exness-trading-backend",
  "mode": "mock"
}
```

### 2. 获取服务信息

```
GET /info
```

会显示当前运行在Mock模式的详细信息。

### 3. 登录接口(模拟)

```
POST /api/auth/login
```

请求体:
```json
{
  "login": 12345678,
  "password": "any_password",
  "server": "Exness-Demo"
}
```

响应(模拟数据):
```json
{
  "success": true,
  "session_token": "...",
  "message": "登录成功",
  "account_info": {
    "login": 12345678,
    "balance": 5432.10,
    "equity": 5450.00,
    "leverage": 2000,
    "server": "Exness-Demo"
  }
}
```

### 4. 获取账户信息

```
GET /api/account/info?login=12345678
```

### 5. 获取持仓列表

```
GET /api/account/positions
```

返回0-3个随机模拟持仓。

### 6. 下单(模拟)

```
POST /api/trade/place-order
```

请求体:
```json
{
  "symbol": "EURUSD",
  "type": "BUY",
  "volume": 0.01,
  "sl_points": 50,
  "tp_points": 100
}
```

### 7. 获取报价

```
GET /api/market/quote/EURUSD
```

返回模拟的实时报价(带随机波动)。

## 🔧 项目文件说明

### 关键文件

- `main_replit_final.py` - Replit专用入口文件(使用Mock MT5)
- `app/services/mt5_mock.py` - Mock MT5服务实现
- `app/services/mt5_service.py` - 智能切换真实/Mock MT5服务
- `requirements.txt` - 已注释MetaTrader5依赖(Linux不支持)

### Mock模式特性

Mock MT5服务提供与真实MT5相同的接口,但返回模拟数据:

- ✅ 账户信息: 随机余额、净值、杠杆
- ✅ 持仓列表: 0-3个随机持仓
- ✅ 下单功能: 生成随机订单ID
- ✅ 报价数据: 基础价格 + 随机波动
- ✅ 平仓功能: 模拟平仓成功

## 🔄 切换到真实MT5环境

如果要在Windows环境运行真实MT5连接:

1. **取消注释** `requirements.txt` 中的 `MetaTrader5==5.0.45`
2. **使用** `main.py` 而不是 `main_replit_final.py`
3. **在Windows系统上运行**
4. **安装MetaTrader 5终端**

或者使用本地开发环境:

```bash
cd python-backend
pip install -r requirements.txt  # 包含MetaTrader5
python main.py
```

##  常见问题

### Q1: 为什么看不到真实MT5数据?

A: Replit运行在Linux环境,MetaTrader5库仅支持Windows。当前使用Mock模式进行测试。

### Q2: Mock模式的数据准确吗?

A: Mock数据是随机生成的,用于测试API接口和业务流程,不代表真实市场数据。

### Q3: 如何在Replit中测试完整流程?

A: 可以测试完整的API调用链: 登录→查询账户→下单→查询持仓→平仓,只是数据是模拟的。

### Q4: 如何部署到生产环境?

A: 
1. 在Windows VPS上部署
2. 或使用Docker + WSL2
3. 或使用MetaApi云服务替代本地MT5

## 📞 需要帮助?

如果遇到任何问题:

1. 查看控制台输出的错误信息
2. 检查 `.replit` 配置文件是否正确
3. 确认 `requirements.txt` 已正确安装
4. 查看日志输出了解详细情况

---

**祝你测试顺利!** 

记住: 当前是Mock模式,适合测试API结构和业务流程。要测试真实MT5连接,需要在Windows环境运行。

# Exness Trading Assistant Backend

Exness MT5交易辅助系统的Python后端服务,基于FastAPI框架开发,提供账户管理、交易执行、行情查询等API接口。

## 功能特性

- ✅ **用户认证**: 通过账号、密码、服务器连接Exness MT5账户
- ✅ **账户管理**: 查询账户余额、净值、持仓等信息
- ✅ **交易执行**: 支持买入/卖出开单、平仓操作
- ✅ **行情监控**: 实时报价查询、WebSocket价格推送
- ✅ **JWT认证**: Token-based身份验证
- ✅ **自动文档**: Swagger UI自动生成API文档

## 技术栈

- **框架**: FastAPI 0.104+
- **MT5集成**: MetaTrader5官方库
- **认证**: JWT (python-jose)
- **日志**: Loguru
- **异步**: asyncio + uvicorn

## 快速开始

### 1. 环境要求

- Python 3.9+
- Windows操作系统 (MT5库仅支持Windows)
- 已安装MetaTrader 5终端
- Exness MT5账户(Demo或Real)

### 2. 安装依赖

```bash
cd python-backend
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `.env` 文件:

```bash
# 修改JWT密钥(生产环境必须)
SECRET_KEY=your-random-secret-key-here

# 如果需要指定MT5路径,取消注释并设置
# MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
```

### 4. 启动服务

**方式一: 直接运行**

```bash
python main.py
```

**方式二: 使用uvicorn**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问:
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 5. 测试API

#### 登录Exness账户

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login": 12345678,
    "password": "your_password",
    "server": "Exness-Demo"
  }'
```

响应示例:
```json
{
  "success": true,
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "登录成功",
  "account_info": {
    "login": 12345678,
    "balance": 1000.0,
    "equity": 1000.0,
    "leverage": 2000,
    "server": "Exness-Demo"
  }
}
```

#### 执行买入操作

```bash
curl -X POST "http://localhost:8000/api/trade/place-order" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "EURUSD",
    "type": "BUY",
    "volume": 0.01,
    "sl_points": 50,
    "tp_points": 100
  }'
```

#### 获取当前持仓

```bash
curl "http://localhost:8000/api/account/positions"
```

## API接口列表

### 认证接口

- `POST /api/auth/login` - 登录并连接MT5
- `POST /api/auth/logout` - 断开连接

### 账户接口

- `GET /api/account/info?login=12345678` - 获取账户信息
- `GET /api/account/positions?symbol=EURUSD` - 获取持仓列表
- `GET /api/account/history?start_date=2026-06-01&end_date=2026-06-13` - 获取历史订单

### 交易接口

- `POST /api/trade/place-order` - 执行交易
- `POST /api/trade/close-position` - 平仓

### 行情接口

- `GET /api/market/symbols` - 获取可交易品种列表
- `GET /api/market/quote/{symbol}` - 获取实时报价
- `WebSocket /api/market/ws/market/{symbol}` - 实时价格推送

## 项目结构

```
python-backend/
├── app/
│   ├── api/                    # API路由
│   │   ├── auth.py             # 认证接口
│   │   ├── trading.py          # 交易接口
│   │   ├── account.py          # 账户接口
│   │   └── market.py           # 行情接口
│   ├── core/                   # 核心模块
│   │   ├── config.py           # 配置管理
│   │   └── security.py         # 安全模块
│   ├── models/                 # 数据模型
│   │   ── schemas.py          # Pydantic模型
│   ├── services/               # 业务服务
│   │   └── mt5_service.py      # MT5服务封装
│   └── utils/                  # 工具函数
├── logs/                       # 日志目录
├── tests/                      # 测试代码
├── main.py                     # 应用入口
├── requirements.txt            # 依赖包
├── .env                        # 环境变量
└── README.md                   # 本文档
```

## 开发说明

### 添加新API

1. 在 `app/models/schemas.py` 中定义请求/响应模型
2. 在 `app/services/mt5_service.py` 中实现业务逻辑
3. 在 `app/api/` 目录下创建或更新路由文件
4. 在 `main.py` 中注册路由

### 错误处理

所有API统一返回JSON格式的错误响应:

```json
{
  "detail": "错误描述信息"
}
```

HTTP状态码:
- `200` - 成功
- `401` - 未授权(Token无效或过期)
- `422` - 参数验证失败
- `500` - 服务器内部错误

### 日志查看

日志文件位于 `logs/` 目录,按日期分割:

```bash
# 查看今天的日志
tail -f logs/app_2026-06-13.log
```

## 常见问题

### Q: MT5初始化失败?

A: 确保已安装MetaTrader 5终端,并且MT5_PATH配置正确。

### Q: 登录时提示"登录失败"?

A: 检查账号、密码、服务器名称是否正确。可在MT5终端中手动登录验证。

### Q: WebSocket连接断开?

A: 检查网络连接,确保防火墙允许8000端口通信。

### Q: 如何部署到生产环境?

A: 
1. 修改 `.env` 中的 `SECRET_KEY` 为强密钥
2. 配置HTTPS反向代理(Nginx/IIS)
3. 使用supervisor或systemd管理进程
4. 配置日志轮转和监控

## 注意事项

⚠️ **重要提示**:

1. **仅在Demo账户测试**: 开发阶段请使用Exness Demo账户,避免真实资金损失
2. **保护敏感信息**: 不要将 `.env` 文件和密码提交到代码仓库
3. **合规性**: 确保自动化交易符合Exness服务条款
4. **风险管理**: 建议始终设置止损(SL)和止盈(TP)

## 许可证

MIT License

## 联系方式

如有问题,请提交Issue或联系开发者。

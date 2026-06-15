"""FastAPI应用主入口 - Replit最终版(使用Mock MT5)"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# 导入路由
from app.api import auth, trading, account, market


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


# 创建FastAPI应用
app = FastAPI(
    title="Exness Trading Backend - Replit",
    description="Exness MT5交易辅助系统后端API (Mock Mode)",
    version="1.0.0-mock",
    docs_url="/docs",
    redoc_url="/redoc"
)


# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(trading.router, prefix="/api")
app.include_router(account.router, prefix="/api")
app.include_router(market.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    port = int(os.environ.get("PORT", 5000))
    logger.info("=" * 60)
    logger.info(f"🚀 Exness Trading Backend 启动中...")
    logger.info(f"📍 运行模式: Mock Mode (模拟MT5)")
    logger.info(f"🔌 服务端口: {port}")
    logger.info(f"📖 API文档: /docs")
    logger.info(f" 健康检查: /health")
    logger.info(f"⚠️  注意: 当前使用模拟数据,非真实MT5连接")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("Exness Trading Backend 已关闭")


@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "Exness Trading Backend API",
        "version": "1.0.0-mock",
        "mode": "Mock Mode",
        "docs": "/docs",
        "status": "running",
        "note": "This is a mock implementation for testing on Replit/Linux"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "exness-trading-backend",
        "mode": "mock"
    }


@app.get("/info")
async def get_info():
    """获取服务信息"""
    return {
        "service": "Exness Trading Backend",
        "version": "1.0.0-mock",
        "environment": "Replit/Linux",
        "mt5_mode": "Mock (Simulated)",
        "features": [
            "User Authentication (Mock)",
            "Account Management (Mock)",
            "Trading Operations (Mock)",
            "Market Data (Mock)",
            "WebSocket Price Feed (Mock)"
        ],
        "limitations": [
            "MetaTrader5 library requires Windows",
            "All data is simulated in this environment",
            "For real MT5 connection, deploy on Windows server"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Replit会自动设置PORT环境变量,默认5000
    port = int(os.environ.get("PORT", 5000))
    
    logger.info(f"Starting server on 0.0.0.0:{port}")
    
    uvicorn.run(
        "main_replit_final:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

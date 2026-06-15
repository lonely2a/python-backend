"""FastAPI应用主入口 - Replit版本"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# 导入路由
from app.api import auth, trading, account, market


# 配置日志(简化版,适合Replit)
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


# 创建FastAPI应用
app = FastAPI(
    title="Exness Trading Backend",
    description="Exness MT5交易辅助系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# 添加CORS中间件(允许跨域访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replit中允许所有来源
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
    port = int(os.environ.get("PORT", 8000))
    logger.info("=" * 50)
    logger.info(f"Exness Trading Backend 启动中...")
    logger.info(f"服务端口: {port}")
    logger.info(f"API文档: /docs")
    logger.info(f"健康检查: /health")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("Exness Trading Backend 已关闭")


@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "Exness Trading Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "exness-trading-backend"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Replit会自动设置PORT环境变量
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"启动服务器: 0.0.0.0:{port}")
    
    uvicorn.run(
        "main_replit:app",  # 注意这里改为 main_replit
        host="0.0.0.0",
        port=port,
        reload=False,  # Replit中不需要reload
        log_level="info"
    )

"""FastAPI应用主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
import asyncio
from typing import Optional

from app.core.config import settings
from app.api import auth, trading, account, market
from app.services.mt5_service import mt5_service


# 全局变量：移动止损后台任务
trailing_stop_task: Optional[asyncio.Task] = None


async def trailing_stop_background_task(interval_seconds: int = 120):
    """
    移动止损后台任务
    每interval_seconds秒检查一次持仓并应用移动止损（按美元价格规则）
    """
    logger.info(f" 移动止损后台任务启动，检查间隔: {interval_seconds}秒")
    logger.info(f" 策略规则: ≥400美元→开仓价+10美元; ≥700美元→开仓价+100美元; ≥1500美元→直接平仓")
    logger.info(f" 强制止损规则: 总亏损≥100美元→自动平仓所有持仓")
    
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            
            # 先检查强制止损条件
            forced_stop_result = await mt5_service.check_forced_stop_loss(max_total_loss_usd=100.0)
            
            if forced_stop_result.get("triggered", False):
                logger.warning(
                    f"⚠️ 强制止损已触发: {forced_stop_result['message']}"
                )
                continue  # 如果触发了强制止损，跳过本次移动止损检查
            
            # 执行移动止损检查（使用新的enable_trailing_stop参数）
            result = await mt5_service.check_and_apply_trailing_stops(
                enable_trailing_stop=True
            )
            
            if result.get("adjusted", 0) > 0:
                logger.info(
                    f"✅ 移动止损: 调整{result['adjusted']}个持仓, "
                    f"跳过{result['skipped']}个, 失败{result['failed']}个"
                )
                
        except Exception as e:
            logger.error(f"移动止损后台任务异常: {str(e)}")


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    level="DEBUG"
)


# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Exness Trading Assistant Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源,生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(trading.router, prefix=settings.API_V1_STR)
app.include_router(account.router, prefix=settings.API_V1_STR)
app.include_router(market.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    global trailing_stop_task
    
    logger.info("=" * 50)
    logger.info(f"{settings.PROJECT_NAME} 启动中...")
    logger.info(f"API文档地址: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 50)

    # 初始化MT5连接(延迟初始化,避免启动时的path问题)
    try:
        if settings.MT5_PATH and settings.MT5_PATH.strip():
            await mt5_service.initialize(path=settings.MT5_PATH)
        else:
            await mt5_service.initialize()
        logger.info("MT5服务初始化成功")
    except Exception as e:
        logger.warning(f"MT5服务将在首次使用时初始化: {str(e)}")
    
    # 启动移动止损后台任务（每2分钟检查一次）
    trailing_stop_task = asyncio.create_task(
        trailing_stop_background_task(interval_seconds=120)
    )
    logger.info(" 移动止损后台任务已启动（每2分钟检查一次）")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    global trailing_stop_task
    
    logger.info(f"{settings.PROJECT_NAME} 关闭中...")

    # 停止移动止损后台任务
    if trailing_stop_task:
        trailing_stop_task.cancel()
        logger.info("移动止损后台任务已停止")

    # 关闭MT5连接
    try:
        await mt5_service.shutdown()
        logger.info("MT5连接已关闭")
    except Exception as e:
        logger.error(f"关闭MT5连接失败: {str(e)}")


@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "Exness Trading Assistant Backend API",
        "version": "1.0.0",
        "docs": "/docs"
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

    logger.info(f"启动服务器: {settings.HOST}:{settings.PORT}")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )

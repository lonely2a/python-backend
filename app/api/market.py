"""行情API - 处理交易品种和报价查询"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Optional
from app.models.schemas import (
    SymbolsResponse,
    SymbolInfo,
    Quote,
    PriceUpdate
)
from app.services.mt5_service import mt5_service
from loguru import logger
import asyncio
from datetime import datetime

router = APIRouter(prefix="/market", tags=["行情"])


@router.get("/symbols", response_model=SymbolsResponse)
async def get_symbols():
    """
    获取所有可交易品种列表

    Returns:
        SymbolsResponse: 品种列表
    """
    try:
        # 常见的外汇和贵金属交易品种
        common_symbols = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD",
            "XAUUSD", "XAGUSD",  # 黄金、白银
            "BTCUSD", "ETHUSD",  # 加密货币
        ]

        symbols = []
        for symbol_name in common_symbols:
            try:
                info = await mt5_service.get_symbol_info(symbol_name)
                symbols.append(SymbolInfo(**info))
            except Exception:
                # 如果获取失败,跳过该品种
                continue

        return SymbolsResponse(symbols=symbols)

    except Exception as e:
        logger.error(f"获取品种列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quote/{symbol}", response_model=Quote)
async def get_quote(symbol: str):
    """
    获取单个品种实时报价

    Args:
        symbol: 交易品种名称

    Returns:
        Quote: 报价信息
    """
    try:
        quote = await mt5_service.get_quote(symbol)

        return Quote(
            symbol=quote["symbol"],
            bid=quote["bid"],
            ask=quote["ask"],
            timestamp=quote["timestamp"]
        )

    except Exception as e:
        logger.error(f"获取报价失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/market/{symbol}")
async def websocket_market(websocket: WebSocket, symbol: str):
    """
    WebSocket实时价格推送

    Args:
        websocket: WebSocket连接
        symbol: 交易品种名称
    """
    await websocket.accept()
    logger.info(f"WebSocket连接建立: {symbol}")

    try:
        while True:
            try:
                # 获取最新价格
                quote = await mt5_service.get_quote(symbol)

                # 发送价格更新
                price_update = PriceUpdate(
                    symbol=quote["symbol"],
                    bid=quote["bid"],
                    ask=quote["ask"],
                    timestamp=quote["timestamp"]
                )

                await websocket.send_json(price_update.dict())

                # 每秒更新一次
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"获取价格失败: {str(e)}")
                await websocket.send_json({
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                await asyncio.sleep(1)

    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: {symbol}")
    except Exception as e:
        logger.error(f"WebSocket异常: {str(e)}")
    finally:
        await websocket.close()

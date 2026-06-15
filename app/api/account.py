"""账户API - 处理账户信息查询"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models.schemas import (
    AccountInfo,
    PositionsResponse,
    Position,
    HistoryResponse,
    HistoryOrder,
    ErrorResponse
)
from app.services.mt5_service import mt5_service
from loguru import logger
from datetime import datetime

router = APIRouter(prefix="/account", tags=["账户"])


@router.get("/info", response_model=AccountInfo)
async def get_account_info(login: int):
    """
    获取账户信息

    Args:
        login: MT5账号

    Returns:
        AccountInfo: 账户信息
    """
    try:
        # 验证login参数
        if not login or login == 0:
            raise HTTPException(
                status_code=400,
                detail="无效的MT5账号"
            )
        
        info = await mt5_service.get_account_info(login=login)

        return AccountInfo(
            login=info["login"],
            balance=info["balance"],
            equity=info["equity"],
            margin=info["margin"],
            free_margin=info["free_margin"],
            margin_level=info["margin_level"],
            leverage=info["leverage"],
            server=info["server"]
        )

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"获取账户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=PositionsResponse)
async def get_positions(symbol: Optional[str] = None):
    """
    获取当前持仓

    Args:
        symbol: 交易品种(可选)

    Returns:
        PositionsResponse: 持仓列表
    """
    try:
        positions = await mt5_service.get_positions(symbol=symbol)

        return PositionsResponse(positions=positions)

    except Exception as e:
        logger.error(f"获取持仓失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    start_date: str,
    end_date: str,
    symbol: Optional[str] = None
):
    """
    获取历史订单

    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        symbol: 交易品种(可选)

    Returns:
        HistoryResponse: 历史订单列表
    """
    try:
        # TODO: 实现历史订单查询
        # MT5的历史订单查询需要使用mt5.history_deals_get()
        # 这里先返回空列表作为占位
        
        logger.info(f"查询历史订单: {start_date} ~ {end_date}")

        return HistoryResponse(history=[])

    except Exception as e:
        logger.error(f"获取历史订单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

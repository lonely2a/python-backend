"""交易API - 处理开单和平仓操作"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.models.schemas import (
    PlaceOrderRequest,
    PlaceOrderResponse,
    ClosePositionRequest,
    ClosePositionResponse,
    CloseAllPositionsResponse,
    ErrorResponse
)
from app.services.mt5_service import mt5_service
from app.core.security import verify_token
from loguru import logger

router = APIRouter(prefix="/trade", tags=["交易"])


def get_current_user(token: str) -> dict:
    """获取当前用户(通过Token验证)"""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的Token")
    return payload


@router.post("/place-order", response_model=PlaceOrderResponse)
async def place_order(request: PlaceOrderRequest, token: str = Depends(lambda: None)):
    """
    执行交易订单

    Args:
        request: 下单请求(品种、类型、手数、止损、止盈)
        token: JWT Token

    Returns:
        PlaceOrderResponse: 订单结果
    """
    try:
        # TODO: 从token中提取login信息
        # 暂时跳过token验证,后续完善
        
        # 检查每日开单频次限制
        limit_check = mt5_service.check_daily_order_limit(max_orders=6)
        if not limit_check["allowed"]:
            logger.warning(f"开单频次限制: {limit_check['message']}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "DAILY_ORDER_LIMIT_EXCEEDED",
                    "message": limit_check["message"],
                    "current_count": limit_check["current_count"],
                    "max_orders": limit_check["max_orders"]
                }
            )
        
        # EMA策略验证（如果启用）
        if request.check_ema_strategy:
            logger.info(f"开始EMA{request.ema_period}策略验证: {request.symbol} {request.type.value}")
            
            validation_result = await mt5_service.validate_ema_strategy(
                symbol=request.symbol,
                order_type=request.type.value,
                ema_period=request.ema_period,
                timeframe_minutes=request.timeframe
            )
            
            if not validation_result["allowed"]:
                logger.warning(f"策略验证失败: {validation_result['reason']}")
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "error": "STRATEGY_VIOLATION",
                        "message": validation_result["reason"],
                        "trend_info": validation_result.get("trend_info")
                    }
                )
            
            logger.info(f"策略验证通过: {validation_result['reason']}")
        
        # 禁止手动平仓策略验证：必须设置TP或启用移动止损
        if request.disable_manual_close:
            has_tp = (request.tp_price is not None and request.tp_price > 0) or \
                     (request.tp_points is not None and request.tp_points > 0)
            
            if not has_tp and not request.enable_trailing_stop:
                logger.warning("禁止手动平仓策略验证失败: 未设置止盈且未启用移动止损")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "MISSING_TAKE_PROFIT",
                        "message": "启用禁止手动平仓策略时，必须设置止盈(TP)或启用移动止损策略，否则订单将永远无法平仓",
                        "requirement": "请至少选择以下一项：\n1. 设置止盈价格或止盈点数\n2. 启用移动止损策略"
                    }
                )
            
            logger.info(f"禁止手动平仓策略验证通过: {'已设置止盈' if has_tp else '已启用移动止损'}")
        
        result = await mt5_service.place_order(
            symbol=request.symbol,
            order_type=request.type.value,
            volume=request.volume,
            sl_points=request.sl_points,
            tp_points=request.tp_points,
            sl_price=request.sl_price,
            tp_price=request.tp_price,
            comment=request.comment,
            magic=request.magic,
            enable_trailing_stop=request.enable_trailing_stop,
            disable_manual_close=request.disable_manual_close
        )

        logger.info(f"下单成功: {request.symbol} {request.type} {request.volume}")

        return PlaceOrderResponse(
            success=True,
            order_id=result["order_id"],
            deal_id=result["deal_id"],
            price=result["price"],
            volume=result["volume"],
            message=result["message"]
        )

    except HTTPException:
        # 重新抛出HTTP异常（策略验证失败等）
        raise
    except Exception as e:
        logger.error(f"下单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close-position")
async def close_position(request: ClosePositionRequest):
    """
    平仓指定订单

    Args:
        request: 平仓请求(订单票号)

    Returns:
        dict: 平仓结果
    """
    try:
        result = await mt5_service.close_position(ticket=request.ticket)

        # 检查是否被策略阻止
        if result.get("blocked_by_strategy"):
            logger.warning(f"平仓被阻止: Ticket {request.ticket} - {result['message']}")
            return {
                "success": False,
                "blocked_by_strategy": True,
                "message": result["message"]
            }

        if result["success"]:
            logger.info(f"平仓成功: Ticket {request.ticket}")
            return ClosePositionResponse(
                success=True,
                message=result["message"]
            )
        else:
            logger.error(f"平仓失败: {result['message']}")
            return ClosePositionResponse(
                success=False,
                message=result["message"]
            )

    except Exception as e:
        logger.error(f"平仓失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trailing-stop/check", tags=["移动止损"])
async def check_trailing_stop(
    enable_trailing_stop: bool = True
):
    """
    手动触发移动止损检查

    Args:
        enable_trailing_stop: 全局开关（当持仓没有独立设置时使用，默认开启）

    Returns:
        dict: 处理结果统计
    """
    try:
        result = await mt5_service.check_and_apply_trailing_stops(
            enable_trailing_stop=enable_trailing_stop
        )

        logger.info(
            f"移动止损检查完成: 总计{result['total']}个持仓, "
            f"调整{result['adjusted']}个, 跳过{result['skipped']}个"
        )

        return {
            "success": True,
            "message": f"移动止损检查完成",
            "summary": {
                "total_positions": result["total"],
                "checked": result["checked"],
                "adjusted": result["adjusted"],
                "skipped": result["skipped"],
                "failed": result["failed"]
            },
            "details": result.get("details", [])
        }

    except Exception as e:
        logger.error(f"移动止损失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close-all", response_model=CloseAllPositionsResponse, tags=["平仓"])
async def close_all_positions():
    """
    一键平仓所有可平仓的持仓

    Returns:
        CloseAllPositionsResponse: 一键平仓结果
    """
    try:
        result = await mt5_service.close_all_positions()

        logger.info(
            f"一键平仓完成: 总计{result['total']}个持仓, "
            f"成功{result['success']}个, 失败{result['failed']}个, "
            f"策略跳过{result['skipped_by_strategy']}个"
        )

        return CloseAllPositionsResponse(
            success=True,
            total=result["total"],
            attempted=result["attempted"],
            success_count=result["success"],
            failed=result["failed"],
            skipped_by_strategy=result["skipped_by_strategy"],
            details=result.get("details", []),
            message=f"一键平仓完成: 成功{result['success']}个, 失败{result['failed']}个, 跳过{result['skipped_by_strategy']}个"
        )

    except Exception as e:
        logger.error(f"一键平仓失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

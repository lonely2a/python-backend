"""Pydantic数据模型 - 用于API请求/响应验证"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class OrderType(str, Enum):
    """订单类型枚举"""
    BUY = "BUY"
    SELL = "SELL"


# ==================== 认证相关模型 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    login: int = Field(..., description="MT5账号", example=12345678)
    password: str = Field(..., description="交易密码", min_length=6)
    server: str = Field(..., description="Exness服务器", example="Exness-Real16")
    save_credentials: bool = Field(False, description="是否保存凭证")


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool
    session_token: Optional[str] = None
    message: Optional[str] = None
    account_info: Optional[dict] = None


class LogoutResponse(BaseModel):
    """登出响应"""
    success: bool
    message: str


# ==================== 账户相关模型 ====================

class AccountInfo(BaseModel):
    """账户信息"""
    login: int
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    leverage: int
    server: str


class Position(BaseModel):
    """持仓信息"""
    ticket: int
    symbol: str
    type: str  # BUY or SELL
    volume: float
    price_open: float
    profit: float
    time: datetime


class PositionsResponse(BaseModel):
    """持仓列表响应"""
    positions: list[Position]


class HistoryOrder(BaseModel):
    """历史订单"""
    ticket: int
    symbol: str
    type: str
    volume: float
    price_open: float
    price_close: float
    profit: float
    time_open: datetime
    time_close: datetime


class HistoryResponse(BaseModel):
    """历史订单响应"""
    history: list[HistoryOrder]


# ==================== 交易相关模型 ====================

class PlaceOrderRequest(BaseModel):
    """下单请求"""
    symbol: str = Field(..., description="交易品种", example="EURUSD")
    type: OrderType = Field(..., description="订单类型")
    volume: float = Field(..., description="手数", gt=0, example=0.01)
    sl_points: Optional[int] = Field(None, description="止损点数（与sl_price二选一）", ge=0)
    tp_points: Optional[int] = Field(None, description="止盈点数（与tp_price二选一）", ge=0)
    sl_price: Optional[float] = Field(None, description="止损价格（与sl_points二选一，优先使用）")
    tp_price: Optional[float] = Field(None, description="止盈价格（与tp_points二选一，优先使用）")
    comment: str = Field("", description="订单注释", max_length=50)
    magic: int = Field(0, description="EA魔术号")
    # 策略验证相关
    check_ema_strategy: bool = Field(False, description="是否启用EMA60趋势策略验证")
    ema_period: int = Field(60, description="EMA周期（默认60）", ge=1)
    timeframe: int = Field(15, description="K线时间周期（分钟），默认M15")
    # 移动止损策略
    enable_trailing_stop: bool = Field(True, description="是否启用移动止损策略（默认开启）")
    # 禁止手动平仓策略
    disable_manual_close: bool = Field(True, description="是否禁止手动平仓（默认开启，开启后订单无法手动平仓）")


class PlaceOrderResponse(BaseModel):
    """下单响应"""
    success: bool
    order_id: Optional[int] = None
    deal_id: Optional[int] = None
    price: Optional[float] = None
    volume: Optional[float] = None
    message: Optional[str] = None


class ClosePositionRequest(BaseModel):
    """平仓请求"""
    ticket: int = Field(..., description="订单票号")


class ClosePositionResponse(BaseModel):
    """平仓响应"""
    success: bool
    message: Optional[str] = None


class CloseAllPositionsResponse(BaseModel):
    """一键平仓响应"""
    success: bool
    total: int = 0
    attempted: int = 0
    success_count: int = 0
    failed: int = 0
    skipped_by_strategy: int = 0
    details: list = []
    message: Optional[str] = None


# ==================== 行情相关模型 ====================

class SymbolInfo(BaseModel):
    """交易品种信息"""
    name: str
    description: str
    spread: int
    digits: int
    point: float
    volume_min: float
    volume_max: float
    volume_step: float


class SymbolsResponse(BaseModel):
    """交易品种列表响应"""
    symbols: list[SymbolInfo]


class Quote(BaseModel):
    """报价信息"""
    symbol: str
    bid: float
    ask: float
    timestamp: datetime


class PriceUpdate(BaseModel):
    """WebSocket价格推送"""
    symbol: str
    bid: float
    ask: float
    timestamp: datetime


# ==================== 通用响应模型 ====================

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    message: str

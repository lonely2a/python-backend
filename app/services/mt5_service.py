"""MT5服务封装 - 提供MT5连接和交易功能"""
import os
import sys
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger
import numpy as np

# 检测是否在Replit/Linux环境,如果是则使用Mock版本
IS_REPLIT = os.environ.get("REPL_ID") is not None or sys.platform != "win32"

if IS_REPLIT:
    # Replit/Linux环境: 使用Mock服务
    from app.services.mt5_mock import MockMT5Service as MT5ServiceImpl
    logger.warning("⚠️  Running in MOCK MODE - MetaTrader5 requires Windows")
else:
    # Windows环境: 使用真实MT5
    try:
        import MetaTrader5 as mt5
        from app.services.mt5_mock import MockMT5Service  # 作为fallback
        MT5ServiceImpl = None  # type: ignore
    except ImportError:
        logger.warning("⚠️  MetaTrader5 not available, using Mock mode")
        from app.services.mt5_mock import MockMT5Service as MT5ServiceImpl


class MT5Service:
    """MT5服务类"""

    def __init__(self):
        self.connected_accounts: Dict[int, dict] = {}  # login -> connection info
        self._initialized = False
        self.trailing_stop_settings: Dict[int, bool] = {}  # ticket -> enable_trailing_stop
        self.disable_manual_close_settings: Dict[int, bool] = {}  # ticket -> disable_manual_close
        self.order_history: List[Dict[str, Any]] = []  # 订单历史记录（用于频次限制）
        
        # 加载持久化设置
        self.settings_file = "strategy_settings.json"
        self._load_settings()

    async def initialize(self, path: Optional[str] = None) -> bool:
        """
        初始化MT5连接

        Args:
            path: MT5终端路径,None表示使用默认路径

        Returns:
            bool: 初始化是否成功
        """
        if self._initialized:
            return True

        try:
            # 如果path为空或None,不传递path参数
            if path and path.strip():
                result = mt5.initialize(path=path)
            else:
                result = mt5.initialize()
            
            if not result:
                error = mt5.last_error()
                logger.error(f"MT5初始化失败: {error}")
                return False

            self._initialized = True
            logger.info("MT5初始化成功")
            return True

        except Exception as e:
            logger.error(f"MT5初始化异常: {str(e)}")
            return False

    def _load_settings(self):
        """从文件加载策略设置"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载禁止手动平仓设置（ticket是字符串，需要转换为整数）
                self.disable_manual_close_settings = {
                    int(k): v for k, v in data.get('disable_manual_close', {}).items()
                }
                
                # 加载移动止损设置
                self.trailing_stop_settings = {
                    int(k): v for k, v in data.get('trailing_stop', {}).items()
                }
                
                logger.info(f"已加载策略设置: {len(self.disable_manual_close_settings)}个禁止平仓设置, {len(self.trailing_stop_settings)}个移动止损设置")
            else:
                logger.info("未找到策略设置文件，使用空设置")
        except Exception as e:
            logger.error(f"加载策略设置失败: {str(e)}")

    def _save_settings(self):
        """保存策略设置到文件"""
        try:
            data = {
                'disable_manual_close': {str(k): v for k, v in self.disable_manual_close_settings.items()},
                'trailing_stop': {str(k): v for k, v in self.trailing_stop_settings.items()}
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"策略设置已保存")
        except Exception as e:
            logger.error(f"保存策略设置失败: {str(e)}")

    async def connect(
        self,
        login: int,
        password: str,
        server: str
    ) -> Dict[str, Any]:
        """
        连接到Exness MT5账户

        Args:
            login: MT5账号
            password: 交易密码
            server: Exness服务器名称

        Returns:
            dict: 包含账户信息的字典

        Raises:
            Exception: 连接失败时抛出异常
        """
        # 确保MT5已初始化
        if not self._initialized:
            await self.initialize()

        try:
            # 登录到MT5账户
            authorized = mt5.login(login, password=password, server=server)

            if not authorized:
                error = mt5.last_error()
                raise Exception(f"登录失败: {error}")

            # 获取账户信息
            account_info = mt5.account_info()
            if account_info is None:
                raise Exception("无法获取账户信息")

            # 保存连接信息
            self.connected_accounts[login] = {
                "connected_at": datetime.now(),
                "server": server,
                "account_info": account_info
            }

            logger.info(f"成功连接到Exness账户: {login} @ {server}")

            return self._format_account_info(account_info)

        except Exception as e:
            logger.error(f"连接Exness账户失败: {str(e)}")
            raise

    def _format_account_info(self, info) -> Dict[str, Any]:
        """格式化账户信息"""
        return {
            "login": info.login,
            "balance": float(info.balance),
            "equity": float(info.equity),
            "margin": float(info.margin),
            "free_margin": float(info.margin_free),
            "margin_level": float(info.margin_level) if info.margin_level else 0.0,
            "leverage": info.leverage,
            "server": info.server
        }

    async def get_account_info(self, login: int) -> Dict[str, Any]:
        """
        获取账户信息

        Args:
            login: MT5账号

        Returns:
            dict: 账户信息
        """
        # 注释掉连接检查，因为MT5.account_info()会返回当前连接的账户信息
        # if login not in self.connected_accounts:
        #     raise Exception("账户未连接")

        account_info = mt5.account_info()
        if account_info is None:
            raise Exception("无法获取账户信息，请确认已连接到MT5账户")

        return self._format_account_info(account_info)

    async def get_positions(self, symbol: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        获取当前持仓（使用实时价格）

        Args:
            symbol: 交易品种,可选

        Returns:
            list: 持仓列表
        """
        try:
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()

            if positions is None:
                return []

            result = []
            for pos in positions:
                # 获取实时市场价格
                tick = mt5.symbol_info_tick(pos.symbol)
                current_price = float(tick.bid if tick else pos.price_current)
                
                result.append({
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL",
                    "volume": float(pos.volume),
                    "price_open": float(pos.price_open),
                    "price_current": current_price,
                    "profit": float(pos.profit),
                    "time": datetime.fromtimestamp(pos.time).isoformat()
                })
            
            return result

        except Exception as e:
            logger.error(f"获取持仓失败: {str(e)}")
            raise

    async def place_order(
        self,
        symbol: str,
        order_type: str,
        volume: float,
        sl_points: Optional[float] = None,
        tp_points: Optional[float] = None,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        comment: str = "",
        magic: int = 0,
        enable_trailing_stop: bool = True,
        disable_manual_close: bool = True
    ) -> Dict[str, Any]:
        """
        执行交易订单

        Args:
            symbol: 交易品种
            order_type: 订单类型 (BUY/SELL)
            volume: 手数
            sl_points: 止损点数（与sl_price二选一）
            tp_points: 止盈点数（与tp_price二选一）
            sl_price: 止损价格（优先使用，与sl_points二选一）
            tp_price: 止盈价格（优先使用，与tp_points二选一）
            comment: 订单注释
            magic: EA魔术号
            enable_trailing_stop: 是否启用移动止损策略（默认开启）
            disable_manual_close: 是否禁止手动平仓（默认开启）

        Returns:
            dict: 订单结果
        """
        try:
            # 获取当前价格
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                raise Exception(f"无法获取 {symbol} 的价格")

            price = tick.ask if order_type == "BUY" else tick.bid

            # 准备交易请求
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
                "price": price,
                "deviation": 20,
                "magic": magic,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,  # 使用FOK模式（更通用）
            }

            # 计算止损止盈 - 优先使用价格，其次使用点数
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                raise Exception(f"无法获取 {symbol} 的信息")

            point = symbol_info.point

            # 设置止损
            if sl_price is not None:
                # 使用价格设置止损
                request["sl"] = sl_price
            elif sl_points is not None and sl_points > 0:
                # 使用点数设置止损
                if order_type == "BUY":
                    request["sl"] = price - sl_points * point
                else:
                    request["sl"] = price + sl_points * point

            # 设置止盈
            if tp_price is not None:
                # 使用价格设置止盈
                request["tp"] = tp_price
            elif tp_points is not None and tp_points > 0:
                # 使用点数设置止盈
                if order_type == "BUY":
                    request["tp"] = price + tp_points * point
                else:
                    request["tp"] = price - tp_points * point

            # 发送订单
            result = mt5.order_send(request)
            
            # 检查返回结果
            if result is None:
                error = mt5.last_error()
                raise Exception(f"订单发送失败: {error}")
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise Exception(f"订单失败: {result.comment} (retcode={result.retcode})")

            logger.info(
                f"订单成功: {order_type} {symbol} {volume}手 @ {price}, "
                f"OrderID: {result.order}, DealID: {result.deal}"
            )

            # 保存移动止损设置和禁止手动平仓设置
            ticket = result.order
            self.trailing_stop_settings[ticket] = enable_trailing_stop
            self.disable_manual_close_settings[ticket] = disable_manual_close
            
            # 持久化保存到文件
            self._save_settings()
            
            logger.info(f"策略设置: Ticket {ticket} - 移动止损:{'启用' if enable_trailing_stop else '禁用'}, 禁止平仓:{'是' if disable_manual_close else '否'}")

            # 记录订单历史（用于频次限制）
            now = datetime.now()
            self.order_history.append({
                "ticket": ticket,
                "symbol": symbol,
                "type": order_type,
                "volume": volume,
                "timestamp": now,
                "date": now.strftime("%Y-%m-%d")
            })
            logger.info(f"订单历史已记录: 今日第{self.get_today_order_count()}笔订单")

            return {
                "success": True,
                "order_id": result.order,
                "deal_id": result.deal,
                "price": price,
                "volume": volume,
                "message": f"{order_type}成功: {symbol} {volume}手 @ {price}"
            }

        except Exception as e:
            logger.error(f"下单失败: {str(e)}")
            raise

    def get_today_order_count(self) -> int:
        """
        获取今日订单数量（用于频次限制）

        Returns:
            int: 今日订单数量
        """
        today = datetime.now().strftime("%Y-%m-%d")
        count = sum(1 for order in self.order_history if order["date"] == today)
        return count

    def check_daily_order_limit(self, max_orders: int = 6) -> Dict[str, Any]:
        """
        检查每日开单频次限制

        Args:
            max_orders: 每日最大订单数（默认6笔）

        Returns:
            dict: {
                "allowed": bool,
                "current_count": int,
                "max_orders": int,
                "message": str
            }
        """
        current_count = self.get_today_order_count()
        
        if current_count >= max_orders:
            return {
                "allowed": False,
                "current_count": current_count,
                "max_orders": max_orders,
                "message": f"今日已开立{current_count}笔订单，达到每日上限({max_orders}笔)，请明日再试"
            }
        
        return {
            "allowed": True,
            "current_count": current_count,
            "max_orders": max_orders,
            "message": f"今日已开立{current_count}笔订单，还可开立{max_orders - current_count}笔"
        }

    async def apply_trailing_stop(
        self,
        ticket: int,
        enable_trailing_stop: bool = True
    ) -> Dict[str, Any]:
        """
        应用移动止损策略（按美元价格规则）
        
        新规则（按美元价格差）：
        - 盈利≥400美元且<700美元：止损移至开仓价+10美元
        - 盈利≥700美元：止损移至开仓价+100美元

        Args:
            ticket: 持仓票号
            enable_trailing_stop: 是否启用移动止损策略

        Returns:
            dict: {
                "success": bool,
                "action": "adjusted" | "skipped" | "failed",
                "message": str,
                "old_sl": float,
                "new_sl": float
            }
        """
        if not enable_trailing_stop:
            return {
                "success": True,
                "action": "skipped",
                "message": "移动止损策略未启用",
                "old_sl": 0,
                "new_sl": 0
            }
        
        try:
            # 获取持仓信息
            position = mt5.positions_get(ticket=ticket)
            if position is None or len(position) == 0:
                return {
                    "success": False,
                    "action": "failed",
                    "message": f"找不到持仓: {ticket}",
                    "old_sl": 0,
                    "new_sl": 0
                }

            pos = position[0]
            
            # 获取品种信息以计算点值
            symbol_info = mt5.symbol_info(pos.symbol)
            if symbol_info is None:
                return {
                    "success": False,
                    "action": "failed",
                    "message": f"无法获取 {pos.symbol} 的信息",
                    "old_sl": 0,
                    "new_sl": 0
                }

            point = symbol_info.point
            current_price = pos.price_current
            open_price = pos.price_open
            current_sl = pos.sl if pos.sl else 0.0
            position_type = pos.type  # 0=BUY, 1=SELL
            
            # 计算当前盈利金额（美元）
            if position_type == mt5.POSITION_TYPE_BUY:
                profit_usd = current_price - open_price
            else:  # SELL
                profit_usd = open_price - current_price
            
            # 调试日志：记录详细价格信息
            logger.debug(
                f"移动止损计算: Ticket {ticket}, "
                f"{pos.symbol}, 类型={'BUY' if position_type == 0 else 'SELL'}, "
                f"开仓价={open_price:.2f}, 当前价={current_price:.2f}, "
                f"盈利={profit_usd:.2f}美元"
            )
            
            # 🎯 盈利≥1500美元直接平仓止盈
            if profit_usd >= 1500:
                logger.info(f"🎯 盈利{profit_usd:.0f}美元 ≥ 1500美元，执行直接平仓止盈: Ticket {ticket}")
                
                # 准备平仓请求
                tick = mt5.symbol_info_tick(pos.symbol)
                if tick is None:
                    return {
                        "success": False,
                        "action": "failed",
                        "message": f"无法获取 {pos.symbol} 的价格",
                        "old_sl": current_sl,
                        "new_sl": 0
                    }
                
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": pos.symbol,
                    "volume": pos.volume,
                    "type": mt5.ORDER_TYPE_SELL if position_type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                    "position": ticket,
                    "price": tick.bid if position_type == mt5.POSITION_TYPE_BUY else tick.ask,
                    "deviation": 20,
                    "magic": pos.magic,
                    "comment": "Auto Close by Trailing Stop",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                close_result = mt5.order_send(close_request)
                
                if close_result is None or close_result.retcode != mt5.TRADE_RETCODE_DONE:
                    error_msg = close_result.comment if close_result else str(mt5.last_error())
                    return {
                        "success": False,
                        "action": "failed",
                        "message": f"直接平仓失败: {error_msg}",
                        "old_sl": current_sl,
                        "new_sl": 0
                    }
                
                logger.info(f"✅ 直接平仓成功: Ticket {ticket}, 盈利{profit_usd:.2f}美元")
                return {
                    "success": True,
                    "action": "closed",
                    "message": f"盈利{profit_usd:.2f}美元 ≥ 1500美元，已直接平仓止盈",
                    "old_sl": current_sl,
                    "new_sl": 0,
                    "profit_usd": profit_usd
                }
            
            # 检查是否达到最小触发条件（400美元）
            if profit_usd < 400:
                return {
                    "success": True,
                    "action": "skipped",
                    "message": f"盈利{profit_usd:.2f}美元 < 400美元，未达到触发条件",
                    "old_sl": current_sl,
                    "new_sl": current_sl
                }
            
            # 根据盈利区间计算新的止损价格（按美元）
            if 400 <= profit_usd < 700:
                # 盈利400-700美元：止损移至开仓价+10美元
                lock_profit_usd = 10
            elif profit_usd >= 700:
                # 盈利≥700美元：止损移至开仓价+100美元
                lock_profit_usd = 100
            else:
                # 不应该到这里，但以防万一
                return {
                    "success": True,
                    "action": "skipped",
                    "message": f"盈利{profit_usd:.2f}美元不在有效范围内",
                    "old_sl": current_sl,
                    "new_sl": current_sl
                }
            
            # 计算新的止损价格（直接按美元加减）
            if position_type == mt5.POSITION_TYPE_BUY:
                new_sl = open_price + lock_profit_usd
            else:  # SELL
                new_sl = open_price - lock_profit_usd
            
            # 检查是否需要调整止损
            should_adjust = False
            if position_type == mt5.POSITION_TYPE_BUY:
                # 多单：新止损应该高于旧止损（或旧止损为0）
                if current_sl == 0.0 or new_sl > current_sl:
                    should_adjust = True
            else:
                # 空单：新止损应该低于旧止损（或旧止损为0）
                if current_sl == 0.0 or new_sl < current_sl:
                    should_adjust = True
            
            if not should_adjust:
                return {
                    "success": True,
                    "action": "skipped",
                    "message": f"当前止损已优于目标止损，无需调整（盈利{profit_points:.0f}点，目标锁定{lock_profit_points}点）",
                    "old_sl": current_sl,
                    "new_sl": current_sl
                }
            
            # 执行止损调整
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": pos.symbol,
                "position": ticket,
                "sl": new_sl,
                "tp": pos.tp if pos.tp else 0.0,
            }
            
            result = mt5.order_send(request)
            
            if result is None:
                error = mt5.last_error()
                return {
                    "success": False,
                    "action": "failed",
                    "message": f"止损调整失败: {error}",
                    "old_sl": current_sl,
                    "new_sl": new_sl
                }
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    "success": False,
                    "action": "failed",
                    "message": f"止损调整失败: {result.comment}",
                    "old_sl": current_sl,
                    "new_sl": new_sl
                }
            
            logger.info(
                f"✅ 移动止损成功: Ticket {ticket}, "
                f"{pos.symbol}, 盈利{profit_usd:.2f}美元, "
                f"止损 {current_sl:.2f} → {new_sl:.2f} (锁定{lock_profit_usd}美元)"
            )
            
            return {
                "success": True,
                "action": "adjusted",
                "message": f"移动止损成功: 盈利{profit_usd:.2f}美元, 止损调整为{new_sl:.2f} (锁定{lock_profit_usd}美元)",
                "old_sl": current_sl,
                "new_sl": new_sl,
                "profit_usd": profit_usd,
                "lock_profit_usd": lock_profit_usd
            }

        except Exception as e:
            logger.error(f"移动止损异常: {str(e)}")
            return {
                "success": False,
                "action": "failed",
                "message": f"异常: {str(e)}",
                "old_sl": 0,
                "new_sl": 0
            }

    async def check_forced_stop_loss(self, max_total_loss_usd: float = 100.0) -> Dict[str, Any]:
        """
        检查强制止损条件：如果所有持仓的总亏损达到指定金额，触发强制平仓
        
        Args:
            max_total_loss_usd: 最大允许总亏损金额（美元），默认100美元
            
        Returns:
            dict: {
                "triggered": bool,  # 是否触发强制止损
                "total_profit": float,  # 当前总盈亏
                "max_loss": float,  # 最大允许亏损
                "closed_count": int,  # 成功平仓数量
                "failed_count": int,  # 失败数量
                "message": str
            }
        """
        try:
            positions = await self.get_positions()
            
            if not positions:
                return {
                    "triggered": False,
                    "total_profit": 0.0,
                    "max_loss": max_total_loss_usd,
                    "closed_count": 0,
                    "failed_count": 0,
                    "message": "无持仓，无需检查"
                }
            
            # 计算所有持仓的总盈亏
            total_profit = sum(pos["profit"] for pos in positions)
            
            logger.info(f"强制止损检查: 总盈亏={total_profit:.2f}美元, 阈值=-{max_total_loss_usd:.2f}美元")
            
            # 检查是否达到强制止损条件
            if total_profit <= -max_total_loss_usd:
                logger.warning(f"⚠️ 触发强制止损! 总亏损{total_profit:.2f}美元 ≤ -{max_total_loss_usd:.2f}美元")
                
                # 执行一键平仓
                close_result = await self.close_all_positions()
                
                return {
                    "triggered": True,
                    "total_profit": total_profit,
                    "max_loss": max_total_loss_usd,
                    "closed_count": close_result.get("success", 0),
                    "failed_count": close_result.get("failed", 0),
                    "skipped_count": close_result.get("skipped_by_strategy", 0),
                    "message": f"强制止损已触发: 总亏损{total_profit:.2f}美元，已平仓{close_result.get('success', 0)}个持仓"
                }
            else:
                remaining = max_total_loss_usd + total_profit
                return {
                    "triggered": False,
                    "total_profit": total_profit,
                    "max_loss": max_total_loss_usd,
                    "remaining": remaining,
                    "closed_count": 0,
                    "failed_count": 0,
                    "message": f"总盈亏{total_profit:.2f}美元，距离强制止损还有{remaining:.2f}美元"
                }
                
        except Exception as e:
            logger.error(f"强制止损检查异常: {str(e)}")
            return {
                "triggered": False,
                "total_profit": 0.0,
                "max_loss": max_total_loss_usd,
                "closed_count": 0,
                "failed_count": 0,
                "error": str(e),
                "message": f"强制止损检查失败: {str(e)}"
            }

    async def check_and_apply_trailing_stops(
        self,
        enable_trailing_stop: bool = True
    ) -> Dict[str, Any]:
        """
        检查所有持仓并应用移动止损（新规则）

        Args:
            enable_trailing_stop: 全局开关（当持仓没有独立设置时使用）

        Returns:
            dict: 处理结果统计
        """
        try:
            positions = await self.get_positions()
            
            results = {
                "total": len(positions),
                "checked": 0,
                "adjusted": 0,
                "skipped": 0,
                "failed": 0,
                "details": []
            }
            
            for pos in positions:
                ticket = pos["ticket"]
                results["checked"] += 1
                
                # 获取该持仓的移动止损设置（优先使用保存的设置，否则使用全局开关）
                ts_enabled = self.trailing_stop_settings.get(ticket, enable_trailing_stop)
                
                result = await self.apply_trailing_stop(
                    ticket,
                    ts_enabled
                )
                
                results["details"].append({
                    "ticket": ticket,
                    "symbol": pos["symbol"],
                    "type": pos["type"],
                    "profit": pos["profit"],
                    **result
                })
                
                if result["action"] == "adjusted":
                    results["adjusted"] += 1
                elif result["action"] == "skipped":
                    results["skipped"] += 1
                else:
                    results["failed"] += 1
            
            logger.info(
                f"移动止损检查完成: 总计{results['total']}个持仓, "
                f"调整{results['adjusted']}个, 跳过{results['skipped']}个, "
                f"失败{results['failed']}个"
            )
            
            return results

        except Exception as e:
            logger.error(f"批量移动止损失败: {str(e)}")
            return {
                "total": 0,
                "checked": 0,
                "adjusted": 0,
                "skipped": 0,
                "failed": 0,
                "error": str(e)
            }

    async def close_position(self, ticket: int) -> Dict[str, Any]:
        """
        平仓指定订单

        Args:
            ticket: 订单票号

        Returns:
            dict: 平仓结果
        """
        try:
            # 调试日志：记录当前设置状态
            setting_value = self.disable_manual_close_settings.get(ticket, None)
            logger.debug(f"平仓检查: Ticket {ticket} - 禁止平仓设置: {setting_value}, 所有设置: {list(self.disable_manual_close_settings.keys())}")
            
            # 检查是否禁止手动平仓
            if self.disable_manual_close_settings.get(ticket, False):
                logger.info(f"阻止平仓: Ticket {ticket} - 已启用禁止手动平仓策略")
                return {
                    "success": False,
                    "blocked_by_strategy": True,
                    "message": f"订单 {ticket} 已启用禁止手动平仓策略，无法平仓"
                }

            # 获取持仓信息
            position = mt5.positions_get(ticket=ticket)
            if position is None or len(position) == 0:
                raise Exception(f"找不到持仓: {ticket}")

            pos = position[0]

            # 准备平仓请求
            tick = mt5.symbol_info_tick(pos.symbol)
            if tick is None:
                raise Exception(f"无法获取 {pos.symbol} 的价格")

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": ticket,
                "price": tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask,
                "deviation": 20,
                "magic": pos.magic,
                "comment": "Close Position",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise Exception(f"平仓失败: {result.comment}")

            logger.info(f"平仓成功: Ticket {ticket}")

            return {
                "success": True,
                "message": f"平仓成功: Ticket {ticket}"
            }

        except Exception as e:
            logger.error(f"平仓失败: {str(e)}")
            raise

    async def close_all_positions(self) -> Dict[str, Any]:
        """
        一键平仓所有可平仓的持仓（跳过禁止手动平仓的订单）

        Returns:
            dict: 平仓结果统计
        """
        try:
            positions = await self.get_positions()
            
            results = {
                "total": len(positions),
                "attempted": 0,
                "success": 0,
                "failed": 0,
                "skipped_by_strategy": 0,
                "details": []
            }
            
            for pos in positions:
                ticket = pos["ticket"]
                
                # 检查是否禁止手动平仓
                if self.disable_manual_close_settings.get(ticket, False):
                    results["skipped_by_strategy"] += 1
                    results["details"].append({
                        "ticket": ticket,
                        "symbol": pos["symbol"],
                        "type": pos["type"],
                        "action": "skipped",
                        "reason": "禁止手动平仓策略",
                        "message": f"订单 {ticket} 已启用禁止手动平仓策略，已跳过"
                    })
                    logger.info(f"跳过平仓: Ticket {ticket} - 禁止手动平仓策略")
                    continue
                
                # 尝试平仓
                results["attempted"] += 1
                try:
                    result = await self.close_position(ticket)
                    
                    if result["success"]:
                        results["success"] += 1
                        results["details"].append({
                            "ticket": ticket,
                            "symbol": pos["symbol"],
                            "type": pos["type"],
                            "action": "closed",
                            **result
                        })
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "ticket": ticket,
                            "symbol": pos["symbol"],
                            "type": pos["type"],
                            "action": "failed",
                            **result
                        })
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({
                        "ticket": ticket,
                        "symbol": pos["symbol"],
                        "type": pos["type"],
                        "action": "failed",
                        "error": str(e)
                    })
            
            logger.info(
                f"一键平仓完成: 总计{results['total']}个持仓, "
                f"尝试{results['attempted']}个, 成功{results['success']}个, "
                f"失败{results['failed']}个, 策略跳过{results['skipped_by_strategy']}个"
            )
            
            return results

        except Exception as e:
            logger.error(f"一键平仓失败: {str(e)}")
            return {
                "total": 0,
                "attempted": 0,
                "success": 0,
                "failed": 0,
                "skipped_by_strategy": 0,
                "error": str(e)
            }

    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取交易品种信息

        Args:
            symbol: 交易品种名称

        Returns:
            dict: 品种信息
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                raise Exception(f"无法获取 {symbol} 的信息")

            return {
                "name": symbol_info.name,
                "description": symbol_info.description,
                "spread": symbol_info.spread,
                "digits": symbol_info.digits,
                "point": symbol_info.point,
                "volume_min": float(symbol_info.volume_min),
                "volume_max": float(symbol_info.volume_max),
                "volume_step": float(symbol_info.volume_step)
            }

        except Exception as e:
            logger.error(f"获取品种信息失败: {str(e)}")
            raise

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        获取实时报价

        Args:
            symbol: 交易品种

        Returns:
            dict: 报价信息
        """
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                raise Exception(f"无法获取 {symbol} 的报价")

            return {
                "symbol": symbol,
                "bid": float(tick.bid),
                "ask": float(tick.ask),
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error(f"获取报价失败: {str(e)}")
            raise

    async def get_candles(
        self,
        symbol: str,
        timeframe: int = mt5.TIMEFRAME_M15,
        count: int = 200
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据

        Args:
            symbol: 交易品种
            timeframe: 时间周期 (默认M15)
            count: K线数量

        Returns:
            list: K线数据列表
        """
        try:
            # 获取K线数据
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                raise Exception(f"无法获取 {symbol} 的K线数据")

            candles = []
            for rate in rates:
                candles.append({
                    "time": datetime.fromtimestamp(rate['time']),
                    "open": float(rate['open']),
                    "high": float(rate['high']),
                    "low": float(rate['low']),
                    "close": float(rate['close']),
                    "tick_volume": float(rate['tick_volume'])
                })

            return candles

        except Exception as e:
            logger.error(f"获取K线失败: {str(e)}")
            raise

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """
        计算EMA（指数移动平均线）

        Args:
            prices: 价格列表（通常是收盘价）
            period: EMA周期

        Returns:
            list: EMA值列表
        """
        if len(prices) < period:
            raise ValueError(f"价格数据不足，需要至少{period}个数据点")

        # 使用numpy计算EMA
        ema = []
        multiplier = 2 / (period + 1)
        
        # 第一个EMA值使用SMA（简单移动平均）
        sma = sum(prices[:period]) / period
        ema.append(sma)
        
        # 后续使用EMA公式
        for i in range(period, len(prices)):
            current_ema = (prices[i] * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(current_ema)
        
        return ema

    async def get_ema_trend(
        self,
        symbol: str,
        timeframe: int = mt5.TIMEFRAME_M15,
        ema_period: int = 60,
        lookback: int = 30
    ) -> Dict[str, Any]:
        """
        获取EMA趋势方向（使用线性回归斜率判断）

        Args:
            symbol: 交易品种
            timeframe: 时间周期
            ema_period: EMA周期
            lookback: 回看根数（用于判断趋势，默认30根K线，约7.5小时@M15）

        Returns:
            dict: {
                "current_ema": 当前EMA值,
                "trend": "up" | "down" | "flat",
                "ema_values": 最近lookback+1个EMA值,
                "message": 趋势描述
            }
        """
        try:
            # 获取足够的K线数据来计算EMA
            required_candles = ema_period + lookback + 20
            candles = await self.get_candles(symbol, timeframe, required_candles)
            
            # 提取收盘价
            close_prices = [candle['close'] for candle in candles]
            
            # 计算EMA
            ema_values = self.calculate_ema(close_prices, ema_period)
            
            # 取最近的lookback+1个EMA值
            recent_ema = ema_values[-(lookback + 1):]
            
            current_ema = recent_ema[-1]
            previous_ema = recent_ema[0]
            
            # 方法1：计算变化率
            change_rate = ((current_ema - previous_ema) / previous_ema) * 100
            
            # 方法2：使用线性回归计算斜率（更准确）
            x = np.arange(len(recent_ema))
            slope = np.polyfit(x, recent_ema, 1)[0]
            
            # 计算斜率相对于EMA值的百分比
            slope_percent = (slope / current_ema) * 100
            
            # 判断趋势方向 - 使用斜率百分比
            # 回看周期30根K线（7.5小时@M15），较短周期需要稍高的阈值来过滤噪音
            # 阈值太低会导致频繁判断为有趋势，太高会判断为水平
            threshold = 0.015  # 0.015% 的斜率变化视为有明显趋势
            
            if abs(slope_percent) < threshold:
                trend = "flat"
                message = f"EMA{ema_period}接近水平，无明显趋势"
            elif slope > 0:
                trend = "up"
                message = f"EMA{ema_period}向上，上升趋势"
            else:
                trend = "down"
                message = f"EMA{ema_period}向下，下降趋势"
            
            logger.info(f"{symbol} EMA{ema_period}({timeframe}): {message}, "
                       f"变化率={change_rate:.2f}%, 斜率={slope_percent:.3f}%")
            
            return {
                "current_ema": current_ema,
                "trend": trend,
                "ema_values": recent_ema,
                "change_rate": change_rate,
                "slope_percent": slope_percent,
                "message": message
            }

        except Exception as e:
            logger.error(f"获取EMA趋势失败: {str(e)}")
            raise

    async def validate_ema_strategy(
        self,
        symbol: str,
        order_type: str,
        ema_period: int = 60,
        timeframe_minutes: int = 15,
        lookback: int = 30
    ) -> Dict[str, Any]:
        """
        验证EMA60策略是否允许开单

        Args:
            symbol: 交易品种
            order_type: 订单类型 (BUY/SELL)
            ema_period: EMA周期
            timeframe_minutes: K线时间周期（分钟）
            lookback: 回看K线数量（默认30根，约7.5小时，用于判断趋势）

        Returns:
            dict: {
                "allowed": bool,  # 是否允许开单
                "reason": str,    # 原因说明
                "trend_info": dict  # 趋势信息
            }
        """
        try:
            # 映射timeframe
            timeframe_map = {
                1: mt5.TIMEFRAME_M1,
                5: mt5.TIMEFRAME_M5,
                15: mt5.TIMEFRAME_M15,
                30: mt5.TIMEFRAME_M30,
                60: mt5.TIMEFRAME_H1,
                240: mt5.TIMEFRAME_H4,
                1440: mt5.TIMEFRAME_D1,
            }
            
            timeframe = timeframe_map.get(timeframe_minutes, mt5.TIMEFRAME_M15)
            
            # 获取EMA趋势（回看60根K线）
            trend_info = await self.get_ema_trend(symbol, timeframe, ema_period, lookback=lookback)
            
            trend = trend_info["trend"]
            
            # 策略逻辑：
            # - BUY: 需要趋势向上(up)或水平(flat)，禁止向下(down)
            # - SELL: 需要趋势向下(down)或水平(flat)，禁止向上(up)
            
            if order_type == "BUY":
                if trend == "down":
                    return {
                        "allowed": False,
                        "reason": f"不符合交易策略，禁止开多单。当前{trend_info['message']}，耐心等待合适时机",
                        "trend_info": trend_info
                    }
                else:
                    return {
                        "allowed": True,
                        "reason": f"符合开多策略。{trend_info['message']}",
                        "trend_info": trend_info
                    }
            elif order_type == "SELL":
                if trend == "up":
                    return {
                        "allowed": False,
                        "reason": f"不符合交易策略，禁止开空单。当前{trend_info['message']}，耐心等待合适时机",
                        "trend_info": trend_info
                    }
                else:
                    return {
                        "allowed": True,
                        "reason": f"符合开空策略。{trend_info['message']}",
                        "trend_info": trend_info
                    }
            else:
                return {
                    "allowed": False,
                    "reason": f"无效的订单类型: {order_type}",
                    "trend_info": None
                }

        except Exception as e:
            logger.error(f"EMA策略验证失败: {str(e)}")
            return {
                "allowed": False,
                "reason": f"策略验证出错: {str(e)}",
                "trend_info": None
            }

    async def disconnect(self, login: int) -> bool:
        """
        断开账户连接

        Args:
            login: MT5账号

        Returns:
            bool: 是否成功断开
        """
        if login in self.connected_accounts:
            del self.connected_accounts[login]
            logger.info(f"断开账户连接: {login}")
            return True
        return False

    async def shutdown(self):
        """关闭MT5连接"""
        if self._initialized:
            mt5.shutdown()
            self._initialized = False
            self.connected_accounts.clear()
            logger.info("MT5连接已关闭")


# 创建全局MT5服务实例
mt5_service = MT5Service()

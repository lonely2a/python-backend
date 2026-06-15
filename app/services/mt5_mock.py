"""MT5模拟服务 - 用于Replit/Linux环境测试"""
from typing import Optional, Dict, Any
from datetime import datetime
import random
from loguru import logger


class MockMT5Service:
    """模拟MT5服务类 - 提供与真实MT5相同的接口"""

    def __init__(self):
        self.connected_accounts: Dict[int, dict] = {}
        self._initialized = False
        
        # 模拟数据
        self.mock_symbols = {
            "EURUSD": {"bid": 1.0850, "ask": 1.0852, "spread": 2},
            "GBPUSD": {"bid": 1.2650, "ask": 1.2653, "spread": 3},
            "USDJPY": {"bid": 149.50, "ask": 149.53, "spread": 3},
            "XAUUSD": {"bid": 2350.00, "ask": 2350.50, "spread": 50},
        }

    async def initialize(self, path: Optional[str] = None) -> bool:
        """初始化模拟服务"""
        self._initialized = True
        logger.info("Mock MT5 Service initialized")
        return True

    async def connect(self, login: int, password: str, server: str) -> Dict[str, Any]:
        """模拟连接MT5账户"""
        if not self._initialized:
            await self.initialize()

        # 模拟账户信息
        account_info = {
            "login": login,
            "balance": round(random.uniform(1000, 10000), 2),
            "equity": round(random.uniform(1000, 10000), 2),
            "margin": round(random.uniform(10, 100), 2),
            "free_margin": round(random.uniform(900, 9900), 2),
            "margin_level": round(random.uniform(1000, 10000), 2),
            "leverage": random.choice([100, 200, 500, 1000, 2000]),
            "server": server
        }

        self.connected_accounts[login] = {
            "connected_at": datetime.now(),
            "server": server,
            "account_info": account_info
        }

        logger.info(f"Mock: Connected to account {login} @ {server}")
        return account_info

    async def get_account_info(self, login: int) -> Dict[str, Any]:
        """获取模拟账户信息"""
        if login not in self.connected_accounts:
            raise Exception("Account not connected")
        
        # 更新净值(模拟波动)
        info = self.connected_accounts[login]["account_info"]
        info["equity"] = info["balance"] + random.uniform(-50, 50)
        
        return info

    async def get_positions(self, symbol: Optional[str] = None) -> list[Dict[str, Any]]:
        """获取模拟持仓"""
        positions = []
        
        # 生成0-3个随机持仓
        num_positions = random.randint(0, 3)
        symbols_list = list(self.mock_symbols.keys())
        
        for i in range(num_positions):
            sym = random.choice(symbols_list)
            symbol_data = self.mock_symbols[sym]
            
            position = {
                "ticket": 100000 + i,
                "symbol": sym,
                "type": random.choice(["BUY", "SELL"]),
                "volume": round(random.uniform(0.01, 0.1), 2),
                "price_open": symbol_data["bid"],
                "profit": round(random.uniform(-20, 20), 2),
                "time": datetime.now()
            }
            positions.append(position)
        
        return positions

    async def place_order(
        self,
        symbol: str,
        order_type: str,
        volume: float,
        sl_points: float = 0,
        tp_points: float = 0,
        comment: str = "",
        magic: int = 0
    ) -> Dict[str, Any]:
        """模拟下单"""
        if symbol not in self.mock_symbols:
            # 如果品种不在列表中,生成随机价格
            price = round(random.uniform(1.0, 100.0), 5)
        else:
            symbol_data = self.mock_symbols[symbol]
            price = symbol_data["ask"] if order_type == "BUY" else symbol_data["bid"]

        order_id = random.randint(200000, 999999)
        deal_id = random.randint(200000, 999999)

        logger.info(f"Mock Order: {order_type} {symbol} {volume} @ {price}")

        return {
            "success": True,
            "order_id": order_id,
            "deal_id": deal_id,
            "price": price,
            "volume": volume,
            "message": f"Mock {order_type}: {symbol} {volume} lot @ {price}"
        }

    async def close_position(self, ticket: int) -> Dict[str, Any]:
        """模拟平仓"""
        logger.info(f"Mock: Closed position {ticket}")
        
        return {
            "success": True,
            "message": f"Mock: Position {ticket} closed"
        }

    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """获取模拟品种信息"""
        if symbol in self.mock_symbols:
            data = self.mock_symbols[symbol]
            return {
                "name": symbol,
                "description": f"{symbol} Forex Pair",
                "spread": data["spread"],
                "digits": 5 if "JPY" not in symbol else 3,
                "point": 0.00001 if "JPY" not in symbol else 0.001,
                "volume_min": 0.01,
                "volume_max": 100.0,
                "volume_step": 0.01
            }
        else:
            # 生成随机品种信息
            return {
                "name": symbol,
                "description": f"{symbol} Custom Symbol",
                "spread": random.randint(1, 10),
                "digits": 5,
                "point": 0.00001,
                "volume_min": 0.01,
                "volume_max": 100.0,
                "volume_step": 0.01
            }

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """获取模拟报价"""
        if symbol in self.mock_symbols:
            data = self.mock_symbols[symbol]
            # 添加小幅随机波动
            fluctuation = random.uniform(-0.0005, 0.0005)
            return {
                "symbol": symbol,
                "bid": data["bid"] + fluctuation,
                "ask": data["ask"] + fluctuation,
                "timestamp": datetime.now()
            }
        else:
            # 生成随机报价
            base_price = random.uniform(1.0, 100.0)
            return {
                "symbol": symbol,
                "bid": round(base_price, 5),
                "ask": round(base_price + 0.0002, 5),
                "timestamp": datetime.now()
            }

    async def disconnect(self, login: int) -> bool:
        """断开模拟连接"""
        if login in self.connected_accounts:
            del self.connected_accounts[login]
            logger.info(f"Mock: Disconnected account {login}")
            return True
        return False

    async def shutdown(self):
        """关闭模拟服务"""
        self.connected_accounts.clear()
        self._initialized = False
        logger.info("Mock MT5 Service shutdown")


# 创建全局模拟服务实例
mock_mt5_service = MockMT5Service()

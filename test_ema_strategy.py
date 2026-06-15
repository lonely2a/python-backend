"""测试EMA60策略验证功能"""
import asyncio
from app.services.mt5_service import mt5_service


async def test_ema_strategy():
    """测试EMA策略验证"""
    
    print("=" * 60)
    print("EMA60策略验证测试")
    print("=" * 60)
    
    # 初始化MT5
    await mt5_service.initialize()
    
    # 连接账户
    try:
        await mt5_service.connect(
            login=277738781,
            password="Yls888888!",
            server="Exness-MT5Trial5"
        )
        print("[OK] MT5账户连接成功\n")
    except Exception as e:
        print(f"[WARN] MT5账户连接失败（可能已连接）: {e}\n")
    
    # 测试品种和订单类型
    test_cases = [
        ("EURUSD", "BUY"),
        ("EURUSD", "SELL"),
        ("GBPUSD", "BUY"),
        ("GBPUSD", "SELL"),
    ]
    
    for symbol, order_type in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {symbol} - {order_type}")
        print('='*60)
        
        try:
            # 获取EMA趋势
            trend_info = await mt5_service.get_ema_trend(
                symbol=symbol,
                timeframe=15,  # M15
                ema_period=60,
                lookback=5
            )
            
            print(f"当前EMA60值: {trend_info['current_ema']:.5f}")
            print(f"趋势方向: {trend_info['trend']}")
            print(f"变化率: {trend_info['change_rate']:.2f}%")
            print(f"描述: {trend_info['message']}")
            
            # 验证策略
            validation = await mt5_service.validate_ema_strategy(
                symbol=symbol,
                order_type=order_type,
                ema_period=60,
                timeframe_minutes=15
            )
            
            print(f"\n策略验证结果:")
            allowed_str = "[OK] 是" if validation['allowed'] else "[NO] 否"
            print(f"  允许开单: {allowed_str}")
            print(f"  原因: {validation['reason']}")
            
        except Exception as e:
            print(f"[ERROR] 测试失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 关闭连接
    await mt5_service.shutdown()


if __name__ == "__main__":
    asyncio.run(test_ema_strategy())

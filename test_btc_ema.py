"""测试BTCUSD EMA60趋势"""
import asyncio
from app.services.mt5_service import mt5_service


async def main():
    print("=" * 70)
    print("BTCUSD EMA60 趋势分析")
    print("=" * 70)
    
    # 初始化并连接
    await mt5_service.initialize()
    try:
        await mt5_service.connect(
            login=277738781,
            password="Yls888888!",
            server="Exness-MT5Trial5"
        )
    except:
        pass
    
    # 获取EMA趋势
    trend = await mt5_service.get_ema_trend(
        symbol="BTCUSD",
        timeframe=15,  # M15
        ema_period=60,
        lookback=5
    )
    
    print(f"\n品种: BTCUSD")
    print(f"时间周期: M15 (15分钟)")
    print(f"EMA周期: 60")
    print(f"\n当前EMA60值: {trend['current_ema']:.2f}")
    print(f"趋势方向: {trend['trend'].upper()}")
    print(f"变化率: {trend['change_rate']:.2f}%")
    print(f"描述: {trend['message']}")
    
    print(f"\n最近6个EMA值:")
    for i, ema in enumerate(reversed(trend['ema_values'])):
        print(f"  [{i}] {ema:.2f}")
    
    # 策略验证
    print(f"\n{'='*70}")
    print("策略验证结果:")
    print('='*70)
    
    buy_validation = await mt5_service.validate_ema_strategy("BTCUSD", "BUY", 60, 15)
    sell_validation = await mt5_service.validate_ema_strategy("BTCUSD", "SELL", 60, 15)
    
    print(f"\n开多单(BUY): {'✅ 允许' if buy_validation['allowed'] else '❌ 禁止'}")
    print(f"原因: {buy_validation['reason']}")
    
    print(f"\n开空单(SELL): {'✅ 允许' if sell_validation['allowed'] else '❌ 禁止'}")
    print(f"原因: {sell_validation['reason']}")
    
    await mt5_service.shutdown()
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

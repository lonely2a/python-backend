import asyncio
from app.services.mt5_service import mt5_service

async def test():
    await mt5_service.initialize()
    
    trend = await mt5_service.get_ema_trend('BTCUSD', 15, 60, lookback=10)
    
    print(f'BTCUSD EMA60 Trend Analysis:')
    print(f'  Current EMA: {trend["current_ema"]:.2f}')
    print(f'  Trend: {trend["trend"]}')
    print(f'  Change Rate: {trend["change_rate"]:.2f}%')
    if 'slope_percent' in trend:
        print(f'  Slope Percent: {trend["slope_percent"]:.3f}%')
    print(f'  Message: {trend["message"]}')
    print(f'\n  Recent EMA values (last 11):')
    for i, ema in enumerate(reversed(trend['ema_values'])):
        print(f'    [{i}] {ema:.2f}')
    
    buy_val = await mt5_service.validate_ema_strategy('BTCUSD', 'BUY', 60, 15)
    sell_val = await mt5_service.validate_ema_strategy('BTCUSD', 'SELL', 60, 15)
    
    print(f'\nStrategy Validation:')
    print(f'  BUY allowed: {buy_val["allowed"]} - {buy_val["reason"]}')
    print(f'  SELL allowed: {sell_val["allowed"]} - {sell_val["reason"]}')
    
    await mt5_service.shutdown()

if __name__ == "__main__":
    asyncio.run(test())

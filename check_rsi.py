from ib_async import IB, Stock, util
import pandas as pd
import asyncio

async def check_stocks():
    ib = IB()
    try:
        await ib.connectAsync('127.0.0.1', 7497, clientId=99)
    except Exception as e:
        print('Error connecting:', e)
        return
        
    stocks = [
        Stock('TSLA', 'SMART', 'USD'),
        Stock('AAPL', 'SMART', 'USD'),
        Stock('MSFT', 'SMART', 'USD'),
        Stock('NVDA', 'SMART', 'USD')
    ]
    
    for contract in stocks:
        try:
            await ib.qualifyContractsAsync(contract)
            bars = await ib.reqHistoricalDataAsync(contract, endDateTime='', durationStr='10 D', barSizeSetting='1 hour', whatToShow='TRADES', useRTH=True, formatDate=1)
            if not bars:
                continue
            df = util.df(bars)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            print(f"{contract.symbol} RSI: {rsi.iloc[-1]:.2f}")
        except Exception as e:
            print(f"{contract.symbol} error: {e}")
            
    ib.disconnect()

asyncio.run(check_stocks())

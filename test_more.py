from ib_async import IB, Stock, util
import pandas as pd
import asyncio

async def test_stock(ib, symbol, currency):
    contract = Stock(symbol, 'SMART', currency)
    await ib.qualifyContractsAsync(contract)
    hourly_bars = await ib.reqHistoricalDataAsync(contract, endDateTime='', durationStr='1 Y', barSizeSetting='1 hour', whatToShow='TRADES', useRTH=True, formatDate=1)
    daily_bars = await ib.reqHistoricalDataAsync(contract, endDateTime='', durationStr='1 Y', barSizeSetting='1 day', whatToShow='TRADES', useRTH=True, formatDate=1)
    if not hourly_bars or not daily_bars: return
    df_h = util.df(hourly_bars)
    df_d = util.df(daily_bars)
    df_h['date'] = pd.to_datetime(df_h['date'])
    df_d['date'] = pd.to_datetime(df_d['date'])
    df_d['SMA_50'] = df_d['close'].rolling(window=50).mean()
    df_d['date_only'] = df_d['date'].dt.date
    df_h['date_only'] = df_h['date'].dt.date
    df = pd.merge(df_h, df_d[['date_only', 'SMA_50']], on='date_only', how='left')
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    in_trade = False
    entry_price = 0
    wins = 0
    losses = 0
    for index, row in df.iterrows():
        if in_trade:
            if row['high'] >= entry_price * 1.05: # Changed to 5% TP
                wins += 1
                in_trade = False
                continue
            if row['low'] <= entry_price * 0.90: # Changed to 10% SL
                losses += 1
                in_trade = False
                continue
        if not in_trade:
            if pd.isna(row['SMA_50']) or pd.isna(row['RSI_14']): continue
            if row['close'] > row['SMA_50'] and row['RSI_14'] < 30:
                in_trade = True
                entry_price = row['close']
    
    total = wins + losses
    rate = (wins / total * 100) if total > 0 else 0
    print(f"{symbol}: {total} trades | {wins} Wins | {losses} Losses | {rate:.2f}% Win Rate")

async def run_backtest():
    ib = IB()
    await ib.connectAsync('127.0.0.1', 7497, clientId=101)
    for sym in [('SPY', 'USD'), ('MSFT', 'USD'), ('BHP', 'AUD'), ('CBA', 'AUD'), ('TSLA', 'USD')]:
        await test_stock(ib, sym[0], sym[1])
    ib.disconnect()

asyncio.run(run_backtest())

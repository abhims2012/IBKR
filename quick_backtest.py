from ib_async import IB, Stock, util
import pandas as pd
import asyncio

async def run_backtest():
    ib = IB()
    try:
        await ib.connectAsync('127.0.0.1', 7497, clientId=101)
    except Exception as e:
        print('Error connecting:', e)
        return
        
    contract = Stock('AAPL', 'SMART', 'USD')
    await ib.qualifyContractsAsync(contract)
    
    print('Fetching 1 year of Hourly Data...')
    hourly_bars = await ib.reqHistoricalDataAsync(
        contract,
        endDateTime='',
        durationStr='1 Y',
        barSizeSetting='1 hour',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1
    )
    
    print('Fetching 1 year of Daily Data...')
    daily_bars = await ib.reqHistoricalDataAsync(
        contract,
        endDateTime='',
        durationStr='1 Y',
        barSizeSetting='1 day',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1
    )
    ib.disconnect()
    
    if not hourly_bars or not daily_bars:
        print("Failed to get data")
        return
        
    df_h = util.df(hourly_bars)
    df_d = util.df(daily_bars)
    
    df_h['date'] = pd.to_datetime(df_h['date'])
    df_d['date'] = pd.to_datetime(df_d['date'])
    
    # Calculate 50 SMA on daily
    df_d['SMA_50'] = df_d['close'].rolling(window=50).mean()
    
    # Convert dates to map daily SMA to hourly bars
    df_d['date_only'] = df_d['date'].dt.date
    df_h['date_only'] = df_h['date'].dt.date
    
    # Merge daily SMA onto hourly
    df = pd.merge(df_h, df_d[['date_only', 'SMA_50']], on='date_only', how='left')
    
    # Calculate 14 RSI on hourly
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # Simulate trades
    in_trade = False
    entry_price = 0
    wins = 0
    losses = 0
    
    print('Running simulation...')
    for index, row in df.iterrows():
        # Check exits if in trade
        if in_trade:
            # Did it hit TP?
            if row['high'] >= entry_price * 1.10:
                wins += 1
                in_trade = False
                continue
            # Did it hit SL?
            if row['low'] <= entry_price * 0.95:
                losses += 1
                in_trade = False
                continue
                
        # Check entry if not in trade
        if not in_trade:
            # Need valid SMA and RSI
            if pd.isna(row['SMA_50']) or pd.isna(row['RSI_14']):
                continue
                
            if row['close'] > row['SMA_50'] and row['RSI_14'] < 30:
                in_trade = True
                entry_price = row['close']
                
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"\n--- AAPL 1-Year Backtest ---")
    print(f"Total Trades: {total_trades}")
    print(f"Wins (Hit +10% TP): {wins}")
    print(f"Losses (Hit -5% SL): {losses}")
    print(f"Win Rate: {win_rate:.2f}%")

asyncio.run(run_backtest())

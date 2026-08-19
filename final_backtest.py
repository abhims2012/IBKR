from ib_async import IB, Stock, util
import pandas as pd
import asyncio

async def test_stock(ib, symbol, currency):
    contract = Stock(symbol, 'SMART', currency)
    await ib.qualifyContractsAsync(contract)
    
    bars = await ib.reqHistoricalDataAsync(
        contract, endDateTime='', durationStr='1 Y', 
        barSizeSetting='15 mins', whatToShow='TRADES', useRTH=True, formatDate=1
    )
    daily_bars = await ib.reqHistoricalDataAsync(
        contract, endDateTime='', durationStr='1 Y', 
        barSizeSetting='1 day', whatToShow='TRADES', useRTH=True, formatDate=1
    )
    if not bars or not daily_bars: return 0, 0, 0, 0
    
    df_h = util.df(bars)
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
    total_profit = 0
    trade_size = 500.0 # $500 per trade
    
    for index, row in df.iterrows():
        if pd.isna(row['SMA_50']) or pd.isna(row['RSI_14']):
            continue
            
        if in_trade:
            if row['high'] >= entry_price * 1.05: # +5% TP
                in_trade = False
                qty = trade_size / entry_price
                profit = (entry_price * 1.05 - entry_price) * qty
                total_profit += profit
                wins += 1
            elif row['low'] <= entry_price * 0.90: # -10% SL
                in_trade = False
                qty = trade_size / entry_price
                profit = (entry_price * 0.90 - entry_price) * qty
                total_profit += profit
                losses += 1
        else:
            if row['close'] > row['SMA_50'] and row['RSI_14'] < 30:
                in_trade = True
                entry_price = row['close']
                
    if in_trade:
        exit_price = df.iloc[-1]['close']
        qty = trade_size / entry_price
        profit = (exit_price - entry_price) * qty
        total_profit += profit
        if profit > 0: wins += 1
        else: losses += 1
        
    return wins + losses, wins, losses, total_profit

async def run_backtest():
    ib = IB()
    await ib.connectAsync('127.0.0.1', 7497, clientId=101)
    
    # Mix of 5 US and 5 ASX stocks
    portfolio = [
        ('AAPL', 'USD'), ('MSFT', 'USD'), ('TSLA', 'USD'), ('NVDA', 'USD'), ('JPM', 'USD'),
        ('BHP', 'AUD'), ('CBA', 'AUD'), ('CSL', 'AUD'), ('NAB', 'AUD'), ('MQG', 'AUD')
    ]
    
    total_pnl = 0
    total_wins = 0
    total_losses = 0
    
    for sym, currency in portfolio:
        try:
            trades, wins, losses, pnl = await test_stock(ib, sym, currency)
            total_wins += wins
            total_losses += losses
            total_pnl += pnl
            print(f"{sym}: {trades} trades | {wins} W | {losses} L | PnL: ${pnl:.2f}")
        except Exception as e:
            pass
            
    ib.disconnect()
    
    total_trades = total_wins + total_losses
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"Total Trades (10 stocks): {total_trades}")
    print(f"Overall Win Rate: {win_rate:.2f}%")
    print(f"Total Net Profit: ${total_pnl:.2f}")

asyncio.run(run_backtest())

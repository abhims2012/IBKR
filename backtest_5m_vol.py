from ib_async import IB, Stock, util
import pandas as pd
import asyncio

async def test_stock(ib, symbol, currency):
    contract = Stock(symbol, 'SMART', currency)
    await ib.qualifyContractsAsync(contract)
    
    # Fetch 30 days of 5-min bars
    try:
        bars = await asyncio.wait_for(ib.reqHistoricalDataAsync(
            contract, endDateTime='', durationStr='30 D', 
            barSizeSetting='5 mins', whatToShow='TRADES', useRTH=True, formatDate=1
        ), timeout=20.0)
        daily_bars = await asyncio.wait_for(ib.reqHistoricalDataAsync(
            contract, endDateTime='', durationStr='100 D', 
            barSizeSetting='1 day', whatToShow='TRADES', useRTH=True, formatDate=1
        ), timeout=20.0)
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return 0, 0, 0, 0
        
    if not bars or not daily_bars: return 0, 0, 0, 0
    
    df_h = util.df(bars)
    df_d = util.df(daily_bars)
    
    df_h['date'] = pd.to_datetime(df_h['date'])
    df_d['date'] = pd.to_datetime(df_d['date'])
    
    df_d['SMA_50'] = df_d['close'].rolling(window=50).mean()
    df_d['date_only'] = df_d['date'].dt.date
    df_h['date_only'] = df_h['date'].dt.date
    
    # Merge Daily SMA onto 5-min bars
    df = pd.merge(df_h, df_d[['date_only', 'SMA_50']], on='date_only', how='left')
    
    # Calculate 5-Min RSI 14
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # Calculate Volume Spike (Current Vol > 2x 20-period Avg Vol)
    df['Vol_SMA_20'] = df['volume'].rolling(window=20).mean()
    
    in_trade = False
    entry_price = 0
    wins = 0
    losses = 0
    total_profit = 0
    trade_size = 500.0 # $500 per trade
    
    for index, row in df.iterrows():
        if pd.isna(row['SMA_50']) or pd.isna(row['RSI_14']) or pd.isna(row['Vol_SMA_20']):
            continue
            
        if in_trade:
            # 10% Bracket
            if row['high'] >= entry_price * 1.10: # +10% TP
                in_trade = False
                qty = trade_size / entry_price
                profit = (entry_price * 1.10 - entry_price) * qty
                total_profit += profit
                wins += 1
            elif row['low'] <= entry_price * 0.90: # -10% SL
                in_trade = False
                qty = trade_size / entry_price
                profit = (entry_price * 0.90 - entry_price) * qty
                total_profit += profit
                losses += 1
        else:
            # New Entry Rules: Uptrend + RSI < 40 + Vol > 2x Avg
            if row['close'] > row['SMA_50'] and row['RSI_14'] < 40 and row['volume'] > (row['Vol_SMA_20'] * 2):
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
    await ib.connectAsync('127.0.0.1', 7497, clientId=819)
    
    # Mix of 10 US stocks
    portfolio = [
        ('AAPL', 'USD'), ('MSFT', 'USD'), ('TSLA', 'USD'), ('NVDA', 'USD'), ('JPM', 'USD'),
        ('AMZN', 'USD'), ('META', 'USD'), ('GOOGL', 'USD'), ('BRK.B', 'USD'), ('AVGO', 'USD')
    ]
    
    total_pnl = 0
    total_wins = 0
    total_losses = 0
    
    print("--- 30-Day Aggressive Sniper Backtest (5-Min RSI < 40 + 2x Vol Spike) ---")
    print(f"TP/SL: +10% / -10% | Position Size: $500 USD")
    print("--------------------------------------------------------------------------")
    
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
    
    print("--------------------------------------------------------------------------")
    print(f"Total Trades (30 Days / 10 Stocks): {total_trades}")
    print(f"Overall Win Rate: {win_rate:.2f}%")
    print(f"Total Net Profit: ${total_pnl:.2f}")

asyncio.run(run_backtest())

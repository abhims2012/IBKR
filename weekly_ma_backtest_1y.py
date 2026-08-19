from ib_async import IB, Stock, util
import pandas as pd
import asyncio
import datetime

async def test_stock(ib, symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    await ib.qualifyContractsAsync(contract)
    # Fetch 2 years so we have enough data to calculate the 30-week SMA for the start of the 1-year period
    bars = await ib.reqHistoricalDataAsync(
        contract, 
        endDateTime='', 
        durationStr='2 Y', 
        barSizeSetting='1 week', 
        whatToShow='TRADES', 
        useRTH=True, 
        formatDate=1
    )
    if not bars: return 0, 0, 0, 0
    df = util.df(bars)
    
    # Calculate Weekly SMAs
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_30'] = df['close'].rolling(window=30).mean()
    
    # Slice to only the last 1 year (52 weeks)
    df = df.tail(52)
    
    in_trade = False
    entry_price = 0
    wins = 0
    losses = 0
    total_profit = 0
    trade_size_usd = 1000.0
    
    for index, row in df.iterrows():
        if pd.isna(row['SMA_10']) or pd.isna(row['SMA_30']):
            continue
            
        if in_trade:
            # Check Stop Loss (-10%) and Take Profit (+30%)
            if row['high'] >= entry_price * 1.30:
                in_trade = False
                qty = trade_size_usd / entry_price
                profit = (entry_price * 1.30 - entry_price) * qty
                total_profit += profit
                wins += 1
            elif row['low'] <= entry_price * 0.90:
                in_trade = False
                qty = trade_size_usd / entry_price
                profit = (entry_price * 0.90 - entry_price) * qty
                total_profit += profit
                losses += 1
        else:
            # Check for entry crossover (10 crosses above 30)
            if row['SMA_10'] > row['SMA_30']:
                in_trade = True
                entry_price = row['close']
                    
    # Force close any open trades at the end of the year to see final PnL
    if in_trade:
        exit_price = df.iloc[-1]['close']
        qty = trade_size_usd / entry_price
        profit = (exit_price - entry_price) * qty
        total_profit += profit
        if profit > 0:
            wins += 1
        else:
            losses += 1
            
    total_trades = wins + losses
    return total_trades, wins, losses, total_profit

async def run_backtest():
    ib = IB()
    await ib.connectAsync('127.0.0.1', 7497, clientId=101)
    
    portfolio = ['AAPL', 'MSFT', 'NVDA', 'JPM', 'WMT', 'PG', 'HD', 'CVX', 'KO', 'PEP']
    total_pnl = 0
    total_wins = 0
    total_losses = 0
    
    print("--- 1-Year Weekly MA 10/30 (TP +30%, SL -10%) Backtest ---")
    print(f"Starting Balance: $10,000 USD | Position Size: $1,000 USD")
    print("--------------------------------------------------")
    
    for sym in portfolio:
        try:
            trades, wins, losses, pnl = await test_stock(ib, sym)
            total_wins += wins
            total_losses += losses
            total_pnl += pnl
            print(f"{sym}: {trades} trades | Win: {wins} | Loss: {losses} | PnL: ${pnl:.2f}")
        except Exception as e:
            print(f"{sym} error: {e}")
            
    ib.disconnect()
    
    print("--------------------------------------------------")
    total_trades = total_wins + total_losses
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    final_balance = 10000 + total_pnl
    roi = (total_pnl / 10000) * 100
    
    print(f"Total Trades: {total_trades}")
    print(f"Overall Win Rate: {win_rate:.2f}%")
    print(f"Total Net Profit: ${total_pnl:.2f}")
    print(f"Final Account Balance: ${final_balance:.2f} (ROI: {roi:.2f}%)")

asyncio.run(run_backtest())

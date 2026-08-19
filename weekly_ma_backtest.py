from ib_async import IB, Stock, util
import pandas as pd
import asyncio

async def test_stock(ib, symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    await ib.qualifyContractsAsync(contract)
    bars = await ib.reqHistoricalDataAsync(
        contract, 
        endDateTime='', 
        durationStr='5 Y', 
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
    
    in_trade = False
    entry_price = 0
    wins = 0
    losses = 0
    total_profit = 0
    trade_size_usd = 100.0
    
    for index, row in df.iterrows():
        if pd.isna(row['SMA_10']) or pd.isna(row['SMA_30']):
            continue
            
        if not in_trade:
            # Check for crossover (10 crosses above 30)
            if row['SMA_10'] > row['SMA_30']:
                in_trade = True
                entry_price = row['close']
        else:
            # Check for crossunder (10 crosses below 30)
            if row['SMA_10'] < row['SMA_30']:
                in_trade = False
                exit_price = row['close']
                qty = trade_size_usd / entry_price
                profit = (exit_price - entry_price) * qty
                total_profit += profit
                if profit > 0:
                    wins += 1
                else:
                    losses += 1
                    
    # Force close any open trades at the end of 5 years to see final PnL
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
    
    print("--- 5-Year Weekly MA 10/30 Crossover Backtest ---")
    print(f"Starting Balance: ,000 USD | Position Size:  USD")
    print("--------------------------------------------------")
    
    for sym in portfolio:
        try:
            trades, wins, losses, pnl = await test_stock(ib, sym)
            total_wins += wins
            total_losses += losses
            total_pnl += pnl
            print(f"{sym}: {trades} trades | Win: {wins} | Loss: {losses} | PnL: ")
        except Exception as e:
            print(f"{sym} error: {e}")
            
    ib.disconnect()
    
    print("--------------------------------------------------")
    total_trades = total_wins + total_losses
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    # In this scenario, they only use  * 10 stocks = ,000 of their ,000 at any one time.
    final_balance = 10000 + total_pnl
    roi = (total_pnl / 10000) * 100
    capital_efficiency = (total_pnl / 1000) * 100 # ROI on actual invested capital
    
    print(f"Total Trades: {total_trades}")
    print(f"Overall Win Rate: {win_rate:.2f}%")
    print(f"Total Net Profit: ")
    print(f"Final Account Balance:  (ROI: {roi:.2f}%)")
    print(f"ROI on Invested Capital (,000 max): {capital_efficiency:.2f}%")

asyncio.run(run_backtest())

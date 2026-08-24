import yfinance as yf
import pandas as pd
import numpy as np

def run_backtest():
    portfolio = ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'JPM', 'AMZN', 'META', 'GOOGL', 'BRK-B', 'AVGO']
    
    total_pnl = 0
    total_wins = 0
    total_losses = 0
    trade_size = 500.0 # $500 per trade
    
    print("--- 60-Day Aggressive Sniper Backtest (5-Min RSI < 40 + 2x Vol Spike) ---")
    print(f"TP/SL: +10% / -10% | Position Size: $500 USD")
    print("--------------------------------------------------------------------------")
    
    for sym in portfolio:
        try:
            # Fetch 60 days of 5 min data
            df = yf.download(sym, period='60d', interval='5m', progress=False)
            if df.empty:
                continue
                
            # Flatten multi-index columns if necessary (yfinance bug)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Fetch 1 year of daily data for 50-day SMA
            df_daily = yf.download(sym, period='1y', interval='1d', progress=False)
            if isinstance(df_daily.columns, pd.MultiIndex):
                df_daily.columns = df_daily.columns.get_level_values(0)
                
            df_daily['SMA_50'] = df_daily['Close'].rolling(window=50).mean()
            
            # Align timezone and merge
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC').tz_convert('America/New_York')
            else:
                df.index = df.index.tz_convert('America/New_York')
                
            if df_daily.index.tz is None:
                df_daily.index = df_daily.index.tz_localize('UTC').tz_convert('America/New_York')
            else:
                df_daily.index = df_daily.index.tz_convert('America/New_York')
            
            df['date_only'] = df.index.date
            df_daily['date_only'] = df_daily.index.date
            
            df = pd.merge(df.reset_index(), df_daily[['date_only', 'SMA_50']].reset_index(drop=True), on='date_only', how='left')
            df.set_index('Datetime', inplace=True)
            
            # Calculate 5-Min RSI 14
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
            rs = gain / loss
            df['RSI_14'] = 100 - (100 / (1 + rs))
            
            # Calculate Volume Spike
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            
            in_trade = False
            entry_price = 0
            wins = 0
            losses = 0
            pnl = 0
            
            for index, row in df.iterrows():
                if pd.isna(row['SMA_50']) or pd.isna(row['RSI_14']) or pd.isna(row['Vol_SMA_20']):
                    continue
                    
                if in_trade:
                    if row['High'] >= entry_price * 1.10: # +10% TP
                        in_trade = False
                        qty = trade_size / entry_price
                        profit = (entry_price * 1.10 - entry_price) * qty
                        pnl += profit
                        wins += 1
                    elif row['Low'] <= entry_price * 0.90: # -10% SL
                        in_trade = False
                        qty = trade_size / entry_price
                        profit = (entry_price * 0.90 - entry_price) * qty
                        pnl += profit
                        losses += 1
                else:
                    if row['Close'] > row['SMA_50'] and row['RSI_14'] < 40 and row['Volume'] > (row['Vol_SMA_20'] * 2):
                        in_trade = True
                        entry_price = row['Close']
                        
            if in_trade:
                exit_price = df.iloc[-1]['Close']
                qty = trade_size / entry_price
                profit = (exit_price - entry_price) * qty
                pnl += profit
                if profit > 0: wins += 1
                else: losses += 1
                
            total_wins += wins
            total_losses += losses
            total_pnl += pnl
            print(f"{sym}: {wins+losses} trades | {wins} W | {losses} L | PnL: ${pnl:.2f}")
        except Exception as e:
            print(f"{sym} error: {e}")
            pass
            
    total_trades = total_wins + total_losses
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    print("--------------------------------------------------------------------------")
    print(f"Total Trades (60 Days / 10 Stocks): {total_trades}")
    print(f"Overall Win Rate: {win_rate:.2f}%")
    print(f"Total Net Profit: ${total_pnl:.2f}")

if __name__ == '__main__':
    run_backtest()

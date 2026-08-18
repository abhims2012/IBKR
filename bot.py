import asyncio
import math
import datetime
import pytz
import pandas as pd
import os
import json
from ib_async import IB, Stock, LimitOrder, StopOrder, BracketOrder, util

# Basic Settings
PORT = 7497 # 7497 is typical for TWS paper trading. 4002 for IB Gateway paper trading.
CLIENT_ID = 1

# Strategy Settings
MAX_POSITIONS_AUD = 8
MAX_POSITIONS_USD = 10
MAX_ORDER_SIZE_USD = 100.0
MAX_ORDER_SIZE_AUD = 500.0
DAILY_SPEND_LIMIT_USD = 1500.0
DAILY_SPEND_LIMIT_AUD = 1500.0
TAKE_PROFIT_PCT = 0.05 # 5%
STOP_LOSS_PCT = 0.10  # 10%
SCAN_INTERVAL_SECONDS = 300 # Scan every 5 minutes

# Mixed Watchlist for US and Australian stocks
def get_watchlist():
    DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(DIR, 'watchlist.json')
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading watchlist.json: {e}")
    return []

# Track daily spend per currency
daily_spend = {
    'date': None,
    'USD': 0.0,
    'AUD': 0.0
}

def is_market_open(currency, current_time_aest):
    """
    Checks if a specific market is open based on the currency, time, and day of the week (AEST).
    """
    time_only = current_time_aest.time()
    day_of_week = current_time_aest.weekday() # 0 = Monday, 6 = Sunday
    
    if currency == 'USD':
        # US Market in AEST: Monday 23:30 to Saturday 07:00
        start = datetime.time(23, 30)
        end = datetime.time(7, 0)
        
        # Tuesday(1) through Friday(4): Open early morning AND late night
        if day_of_week in [1, 2, 3, 4]:
            return time_only >= start or time_only <= end
        # Monday(0): Only open late night
        elif day_of_week == 0:
            return time_only >= start
        # Saturday(5): Only open early morning (wrapping up Friday US session)
        elif day_of_week == 5:
            return time_only <= end
        else:
            return False
            
    elif currency == 'AUD':
        # ASX in AEST: Monday(0) to Friday(4), 10:00 to 16:00
        start = datetime.time(10, 0)
        end = datetime.time(16, 0)
        
        if day_of_week in [0, 1, 2, 3, 4]:
            return start <= time_only <= end
        return False
        
    return False

async def is_sniper_setup(ib, contract):
    """
    Checks if the stock meets the sniper criteria:
    1. Uptrend (Current price > 50-day SMA)
    2. Oversold (1-hour 14-period RSI < 30)
    """
    try:
        # IBKR Pacing Protection
        await asyncio.sleep(0.5)

        # 1. Fetch Daily Data for 50-SMA
        daily_bars = await asyncio.wait_for(
            ib.reqHistoricalDataAsync(
                contract,
                endDateTime='',
                durationStr='100 D', # 100 days
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            ),
            timeout=15.0
        )
        if not daily_bars or len(daily_bars) < 50:
            return False, "Not enough daily data for 50-SMA.", 0, 0
            
        df_daily = util.df(daily_bars)
        
        # Calculate 50 SMA using native pandas
        df_daily['SMA_50'] = df_daily['close'].rolling(window=50).mean()
        
        current_sma = df_daily['SMA_50'].iloc[-1]
        current_daily_close = df_daily['close'].iloc[-1]

        if current_daily_close <= current_sma:
            return False, f"Price ({current_daily_close}) is below 50-SMA ({current_sma:.2f}). Not in an uptrend.", current_sma, 0

        # 2. Fetch Hourly Data for 14-RSI
        hourly_bars = await asyncio.wait_for(
            ib.reqHistoricalDataAsync(
                contract,
                endDateTime='',
                durationStr='10 D',
                barSizeSetting='1 hour',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            ),
            timeout=15.0
        )
        if not hourly_bars or len(hourly_bars) < 15:
            return False, "Not enough hourly data for 14-RSI.", current_sma, 0

        df_hourly = util.df(hourly_bars)
        
        # Calculate 14 RSI using native pandas
        delta = df_hourly['close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain / loss
        df_hourly['RSI_14'] = 100 - (100 / (1 + rs))
        
        current_rsi = df_hourly['RSI_14'].iloc[-1]

        if current_rsi >= 30:
            return False, f"Hourly RSI is {current_rsi:.2f} (Needs to be < 30).", current_sma, current_rsi

        return True, f"Sniper setup found! Price > 50-SMA & 1H-RSI = {current_rsi:.2f}", current_sma, current_rsi

    except asyncio.TimeoutError:
        return False, "Timeout: IBKR failed to respond with data within 15 seconds.", 0, 0
    except Exception as e:
        return False, f"Error calculating technicals: {e}", 0, 0

def log_trade(symbol, action, price, sma, rsi, rationale_msg):
    history = []
    DIR = os.path.dirname(os.path.abspath(__file__))
    trades_path = os.path.join(DIR, 'trades.json')
    if os.path.exists(trades_path):
        try:
            with open(trades_path, 'r') as f:
                history = json.load(f)
        except:
            pass
    
    trade = {
        'date': datetime.datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S'),
        'symbol': symbol,
        'action': action,
        'price': price,
        'sma': sma,
        'rsi': rsi,
        'rationale': rationale_msg
    }
    history.append(trade)
    
    # Keep only last 30 days of trades by date (simple approach: keep last 100 trades)
    history = history[-100:]
    
    with open(trades_path, 'w') as f:
        json.dump(history, f, indent=4)

async def main():
    ib = IB()
    print("Connecting to IBKR...")
    try:
        await ib.connectAsync('127.0.0.1', PORT, clientId=CLIENT_ID)
        print("Successfully connected to IBKR.")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    aest = pytz.timezone('Australia/Sydney')
    print(f"Starting continuous scanner. Interval: {SCAN_INTERVAL_SECONDS} seconds.")

    from report import generate_and_push_report
    last_report_time = None

    while True:
        if not ib.isConnected():
            print("Connection to IBKR lost. Attempting to reconnect...")
            try:
                await ib.connectAsync('127.0.0.1', PORT, clientId=CLIENT_ID)
                print("Reconnected successfully.")
            except Exception as e:
                print(f"Reconnection failed: {e}. Retrying in 10 seconds...")
                await asyncio.sleep(10)
                continue
                
        now_aest = datetime.datetime.now(aest)
        current_date = now_aest.date()

        await ib.reqPositionsAsync()
        await asyncio.sleep(1)

        # Generate report every 15 minutes
        if last_report_time is None or (now_aest - last_report_time).total_seconds() >= 900:
            print("--- Generating 15-Min HTML Report ---")
            try:
                await generate_and_push_report(ib)
                last_report_time = now_aest
            except Exception as e:
                print(f"Failed to generate report: {e}")

        # Reset daily spend on a new day
        if daily_spend['date'] != current_date:
            print(f"--- New Day ({current_date}): Resetting Daily Spend limits ---")
            daily_spend['date'] = current_date
            daily_spend['USD'] = 0.0
            daily_spend['AUD'] = 0.0

        print(f"\n--- Starting Scan at {now_aest.strftime('%Y-%m-%d %H:%M:%S %Z')} ---")
        print(f"Current Daily Spend: USD ${daily_spend['USD']:.2f}/{DAILY_SPEND_LIMIT_USD} | AUD ${daily_spend['AUD']:.2f}/{DAILY_SPEND_LIMIT_AUD}")

        # Count only bot positions
        DIR = os.path.dirname(os.path.abspath(__file__))
        trades_path = os.path.join(DIR, 'trades.json')
        history = []
        if os.path.exists(trades_path):
            try:
                with open(trades_path, 'r') as f:
                    history = json.load(f)
            except:
                pass
                
        bot_positions_aud = 0
        bot_positions_usd = 0
        for pos in ib.positions():
            symbol = pos.contract.symbol
            currency = pos.contract.currency
            is_bot = False
            for trade in reversed(history):
                if trade['symbol'] == symbol:
                    is_bot = True
                    break
            if is_bot:
                if currency == 'AUD':
                    bot_positions_aud += 1
                elif currency == 'USD':
                    bot_positions_usd += 1
                
        print(f"Current open positions (Bot only): AUD {bot_positions_aud}/{MAX_POSITIONS_AUD} | USD {bot_positions_usd}/{MAX_POSITIONS_USD}")

        WATCHLIST = get_watchlist()
        if not WATCHLIST:
            print("Watchlist is empty or missing! Skipping scan.")

        for asset in WATCHLIST:
            symbol = asset['symbol']
            exchange = asset['exchange']
            currency = asset['currency']
            
            if not is_market_open(currency, now_aest):
                print(f"[{symbol}] Market ({currency}) is closed. Skipping.")
                continue

            if currency == 'AUD' and bot_positions_aud >= MAX_POSITIONS_AUD:
                print(f"Maximum AUD positions ({MAX_POSITIONS_AUD}) reached. Holding for exits...")
                continue
            elif currency == 'USD' and bot_positions_usd >= MAX_POSITIONS_USD:
                print(f"Maximum USD positions ({MAX_POSITIONS_USD}) reached. Holding for exits...")
                continue

            contract = Stock(symbol, exchange, currency)
            try:
                await ib.qualifyContractsAsync(contract)
            except:
                print(f"[{symbol}] Could not qualify. Skipping.")
                continue

            already_held = any(p.contract.symbol == symbol for p in ib.positions())
            if already_held:
                print(f"[{symbol}] Already holding a position. Skipping.")
                continue

            print(f"[{symbol}] Checking Sniper Setup (RSI/SMA)...")
            is_setup, setup_msg, current_sma, current_rsi = await is_sniper_setup(ib, contract)
            if not is_setup:
                print(f"[{symbol}] {setup_msg}")
                continue
            print(f"[{symbol}] {setup_msg}")

            # Get current market data
            ib.reqMarketDataType(3) 
            ticker = ib.reqMktData(contract, snapshot=True)
            for _ in range(50):
                await asyncio.sleep(0.1)
                if not math.isnan(ticker.last) or not math.isnan(ticker.bid) or not math.isnan(ticker.close):
                    break
                    
            price = ticker.last if not math.isnan(ticker.last) else 0
            if price == 0 or math.isnan(price):
                 if not math.isnan(ticker.bid) and not math.isnan(ticker.ask) and ticker.bid > 0 and ticker.ask > 0:
                      price = (ticker.bid + ticker.ask) / 2
                 elif not math.isnan(ticker.close):
                      price = ticker.close
                      
            if price == 0 or math.isnan(price):
                print(f"[{symbol}] Could not retrieve price.")
                continue

            max_size = MAX_ORDER_SIZE_AUD if currency == 'AUD' else MAX_ORDER_SIZE_USD
            quantity = int(max_size // price)
            total_value = quantity * price
            
            if quantity < 1:
                print(f"[{symbol}] Price (${price:.2f}) > max order size (${max_size}). Cannot buy.")
                continue

            daily_limit = DAILY_SPEND_LIMIT_AUD if currency == 'AUD' else DAILY_SPEND_LIMIT_USD
            if daily_spend[currency] + total_value > daily_limit:
                print(f"[{symbol}] Trade cost (${total_value:.2f}) exceeds remaining daily spend limit for {currency}.")
                continue

            print(f"[{symbol}] ENTERING TRADE! Quantity: {quantity} (Total Value: ${total_value:.2f} {currency})")
            
            parent = ib.bracketOrder(
                action='BUY',
                quantity=quantity,
                limitPrice=round(price, 2), 
                takeProfitPrice=round(price * (1 + TAKE_PROFIT_PCT), 2),
                stopLossPrice=round(price * (1 - STOP_LOSS_PCT), 2)
            )
            
            for order in parent:
                order.tif = 'GTC'
                order.outsideRth = True
                ib.placeOrder(contract, order)
                
            print(f"[{symbol}] Bracket order placed. TP: ${round(price * (1 + TAKE_PROFIT_PCT), 2)}, SL: ${round(price * (1 - STOP_LOSS_PCT), 2)}")
            
            # Log the trade rationale
            log_trade(symbol, 'BUY', price, current_sma, current_rsi, setup_msg)
            
            # Update daily spend
            daily_spend[currency] += total_value
            print(f"Updated Daily Spend: {currency} ${daily_spend[currency]:.2f}")
            
            await asyncio.sleep(1)

        print(f"Scan complete. Sleeping for {SCAN_INTERVAL_SECONDS} seconds...")
        await asyncio.sleep(SCAN_INTERVAL_SECONDS)

if __name__ == '__main__':
    util.run(main())

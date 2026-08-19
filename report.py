import os
import json
import datetime
import pytz
import subprocess
import pandas as pd
import asyncio
from jinja2 import Environment, FileSystemLoader
from ib_async import Stock, util

def get_meta(symbol, meta_data):
    return meta_data.get(symbol, {'name': symbol, 'sector': 'Unknown'})

async def generate_and_push_report(ib):
    DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Load Metadata
    meta_data = {}
    try:
        with open(os.path.join(DIR, 'company_meta.json'), 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
    except:
        pass
        
    # 2. Load History
    history = []
    trades_path = os.path.join(DIR, 'trades.json')
    if os.path.exists(trades_path):
        try:
            with open(trades_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
                for t in history:
                    cm = get_meta(t['symbol'], meta_data)
                    t['name'] = cm.get('name', t['symbol'])
                    t['sector'] = cm.get('sector', 'Unknown')
        except Exception as e:
            print(f"Error loading trades.json: {e}")

    # 3. PnL
    accounts = ib.managedAccounts()
    account = accounts[0] if accounts else ''
    pnl = ib.reqPnL(account, '')
    await asyncio.sleep(2)
    unrealized_pnl = getattr(pnl, 'unrealizedPnL', 0.0)
    realized_pnl = getattr(pnl, 'realizedPnL', 0.0)
    if unrealized_pnl is None or pd.isna(unrealized_pnl): unrealized_pnl = 0.0
    if realized_pnl is None or pd.isna(realized_pnl): realized_pnl = 0.0
    ib.cancelPnL(account, '')

    # 4. Positions
    positions = []
    for pos in ib.positions():
        try:
            symbol = pos.contract.symbol
            qty = pos.position
            cm = get_meta(symbol, meta_data)
            name = cm.get('name', symbol)
            sector = cm.get('sector', 'Unknown')
            currency = pos.contract.currency
            avg_cost = pos.avgCost
            
            contract = pos.contract
            try:
                await ib.qualifyContractsAsync(contract)
            except:
                pass
            
            ib.reqMarketDataType(3) 
            ticker = ib.reqMktData(contract, snapshot=True)
            for _ in range(50):
                await asyncio.sleep(0.1)
                if not pd.isna(ticker.last) or not pd.isna(ticker.bid) or not pd.isna(ticker.close):
                    break
                    
            price = ticker.last if not pd.isna(ticker.last) else 0
            if price == 0 or pd.isna(price):
                 if not pd.isna(ticker.bid) and not pd.isna(ticker.ask) and ticker.bid > 0 and ticker.ask > 0:
                      price = (ticker.bid + ticker.ask) / 2
                 elif not pd.isna(ticker.close):
                      price = ticker.close
                      
            pos_unrealized = (price - avg_cost) * qty if price > 0 else 0.0

            rationale = None
            for trade in reversed(history):
                if trade['symbol'] == symbol:
                    rationale = trade
                    break
                    
            if not rationale:
                continue
                    
            try:
                bars = await asyncio.wait_for(ib.reqHistoricalDataAsync(
                    contract, endDateTime='', durationStr='60 D', barSizeSetting='1 day',
                    whatToShow='TRADES', useRTH=True, formatDate=1
                ), timeout=15.0)
            except asyncio.TimeoutError:
                print(f"Timeout getting historical data for {symbol} chart")
                bars = []
            
            chart_json = "{}"
            if bars:
                df = util.df(bars)
                df['SMA_50'] = df['close'].rolling(window=50).mean()
                
                trace_candle = {
                    'x': df['date'].astype(str).tolist(),
                    'open': df['open'].tolist(), 'high': df['high'].tolist(),
                    'low': df['low'].tolist(), 'close': df['close'].tolist(),
                    'type': 'candlestick', 'name': symbol
                }
                trace_sma = {
                    'x': df['date'].astype(str).tolist(),
                    'y': df['SMA_50'].tolist(),
                    'type': 'scatter', 'mode': 'lines',
                    'name': '50 SMA', 'line': {'color': 'blue'}
                }
                layout = {
                    'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
                    'margin': {'l': 30, 'r': 30, 'b': 30, 't': 10},
                    'xaxis': {'rangeslider': {'visible': False}, 'gridcolor': '#334155'},
                    'yaxis': {'gridcolor': '#334155'}, 'font': {'color': '#94a3b8'}
                }
                chart_json = json.dumps({'data': [trace_candle, trace_sma], 'layout': layout})

            positions.append({
                'symbol': symbol,
                'name': name,
                'sector': sector,
                'currency': currency,
                'quantity': qty,
                'avg_cost': avg_cost,
                'market_price': price,
                'unrealized_pnl': pos_unrealized,
                'rationale': rationale,
                'chart_json': chart_json
            })
        except Exception as e:
            print(f"Error processing position {pos.contract.symbol}: {e}")
            continue
        
    bot_unrealized_pnl = sum(pos['unrealized_pnl'] for pos in positions)
    
    # 5. Render
    env = Environment(loader=FileSystemLoader(DIR))
    template = env.get_template('template.html')
    
    html_out = template.render(
        last_updated=datetime.datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S AEST'),
        unrealized_pnl=bot_unrealized_pnl,
        realized_pnl=realized_pnl,
        positions=positions,
        history=history
    )
    
    index_path = os.path.join(DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
        
    print("Generated index.html successfully.")
    
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f"Auto-update report"], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("Pushed to GitHub Pages successfully.")
    except Exception as e:
        print(f"Failed to push to GitHub: {e}")

if __name__ == '__main__':
    from ib_async import IB
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7497, clientId=999)
        asyncio.run(generate_and_push_report(ib))
    finally:
        ib.disconnect()

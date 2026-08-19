import os
import json
import datetime
import pytz
import subprocess
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from ib_async import Stock, util

async def generate_and_push_report(ib):
    meta_data = {}
    try:
        with open(os.path.join(DIR, 'company_meta.json'), 'r') as f:
            meta_data = json.load(f)
    except:
        pass
    # Load company metadata
    meta_data = {}
    try:
        with open(os.path.join(DIR, 'company_meta.json'), 'r') as f:
            meta_data = json.load(f)
    except:
        pass
    # Load history
    DIR = os.path.dirname(os.path.abspath(__file__))
    trades_path = os.path.join(DIR, 'trades.json')
    history = []
    if os.path.exists(trades_path):
        try:
            with open(trades_path, 'r') as f:
                history = json.load(f)
        except Exception as e:
            print(f"Error loading trades.json: {e}")

    # Subscribe to PnL
    # Assuming account is the first one
    accounts = ib.managedAccounts()
    account = accounts[0] if accounts else ''
    
    pnl = ib.reqPnL(account, '')
    # Wait briefly for PnL data
    import asyncio
    await asyncio.sleep(2)
    
    unrealized_pnl = getattr(pnl, 'unrealizedPnL', 0.0)
    realized_pnl = getattr(pnl, 'realizedPnL', 0.0)
    if unrealized_pnl is None or pd.isna(unrealized_pnl): unrealized_pnl = 0.0
    if realized_pnl is None or pd.isna(realized_pnl): realized_pnl = 0.0
    
    ib.cancelPnL(account, '')

    # Get active positions
    positions = []
    for pos in ib.positions():
        try:
            symbol = pos.contract.symbol
            qty = pos.position
            comp_meta = meta_data.get(symbol, {'name': symbol, 'sector': 'Unknown'})
            name = comp_meta.get('name', symbol)
            sector = comp_meta.get('sector', 'Unknown')
            currency = pos.contract.currency
            avg_cost = pos.avgCost
            
            contract = pos.contract
            try:
                await ib.qualifyContractsAsync(contract)
            except:
                pass
            
            # Get live data for position
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

            # Try to find rationale in history
            rationale = None
            for trade in reversed(history):
                if trade['symbol'] == symbol:
                    rationale = trade
                    break
                    
            # If no rationale is found, it's a manual trade. Skip it.
            if not rationale:
                continue
                    
            # Generate chart
            # Fetch 60 days of data for the chart
            bars = await ib.reqHistoricalDataAsync(
                contract,
                endDateTime='',
                durationStr='60 D',
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            
            chart_json = "{}"
            if bars:
                df = util.df(bars)
                df['SMA_50'] = df['close'].rolling(window=50).mean()
                
                # Create Plotly figure as dict to convert to JSON
                trace_candle = {
                    'x': df['date'].astype(str).tolist(),
                    'open': df['open'].tolist(),
                    'high': df['high'].tolist(),
                    'low': df['low'].tolist(),
                    'close': df['close'].tolist(),
                    'type': 'candlestick',
                    'name': symbol
                }
                
                trace_sma = {
                    'x': df['date'].astype(str).tolist(),
                    'y': df['SMA_50'].tolist(),
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': '50 SMA',
                    'line': {'color': 'blue'}
                }
                
                layout = {
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'margin': {'l': 30, 'r': 30, 'b': 30, 't': 10},
                    'xaxis': {'rangeslider': {'visible': False}, 'gridcolor': '#334155'},
                    'yaxis': {'gridcolor': '#334155'},
                    'font': {'color': '#94a3b8'}
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
        
    # Calculate total unrealized PnL strictly from the bot's positions
    bot_unrealized_pnl = sum(pos['unrealized_pnl'] for pos in positions)
    
    # Render HTML
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
    with open(index_path, 'w') as f:
        f.write(html_out)
        
    print("Generated index.html successfully.")
    
    # Run Git Commands to publish
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f"Auto-update report {datetime.datetime.now().isoformat()}"], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("Pushed to GitHub Pages successfully.")
    except Exception as e:
        print(f"Failed to push to GitHub: {e}")

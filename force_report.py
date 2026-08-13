import json, datetime, pytz, os, subprocess
from ib_async import IB, util
from jinja2 import Environment, FileSystemLoader

async def run():
    ib = IB()
    await ib.connectAsync('127.0.0.1', 7497, clientId=19)
    await ib.reqPositionsAsync()
    import asyncio
    await asyncio.sleep(2)
    
    positions_list = ib.positions()
    print(f"Found {len(positions_list)} positions: {[p.contract.symbol for p in positions_list]}")
    
    DIR = os.path.dirname(os.path.abspath('report.py'))
    trades_path = os.path.join(DIR, 'trades.json')
    with open(trades_path, 'r') as f:
        history = json.load(f)
        
    positions = []
    for pos in positions_list:
        symbol = pos.contract.symbol
        qty = pos.position
        avg_cost = pos.avgCost
        
        rationale = None
        for trade in reversed(history):
            if trade['symbol'] == symbol:
                rationale = trade
                break
        if not rationale:
            continue
            
        contract = pos.contract
        await ib.qualifyContractsAsync(contract)
        bars = await ib.reqHistoricalDataAsync(contract, endDateTime='', durationStr='60 D', barSizeSetting='1 day', whatToShow='TRADES', useRTH=True, formatDate=1)
        
        chart_json = "{}"
        if bars:
            df = util.df(bars)
            df['SMA_50'] = df['close'].rolling(window=50).mean()
            trace_candle = {'x': df['date'].astype(str).tolist(), 'open': df['open'].tolist(), 'high': df['high'].tolist(), 'low': df['low'].tolist(), 'close': df['close'].tolist(), 'type': 'candlestick', 'name': symbol}
            trace_sma = {'x': df['date'].astype(str).tolist(), 'y': df['SMA_50'].tolist(), 'type': 'scatter', 'mode': 'lines', 'name': '50 SMA', 'line': {'color': 'blue'}}
            chart_json = json.dumps({'data': [trace_candle, trace_sma], 'layout': {'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)'}})

        positions.append({'symbol': symbol, 'quantity': qty, 'avg_cost': avg_cost, 'market_price': avg_cost, 'unrealized_pnl': 0, 'rationale': rationale, 'chart_json': chart_json})
        print(f"Added {symbol} to report")
        
    env = Environment(loader=FileSystemLoader(DIR))
    template = env.get_template('template.html')
    html_out = template.render(last_updated=datetime.datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S AEST'), unrealized_pnl=0, realized_pnl=0, positions=positions, history=history)
    
    with open('index.html', 'w') as f:
        f.write(html_out)
    print("HTML written")
    
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', f"Manual Force Update"], check=True)
    subprocess.run(['git', 'push'], check=True)
    print("Pushed")

import asyncio
asyncio.run(run())

import json
with open('trades.json', 'r') as f:
    trades = json.load(f)

for t in trades:
    if 'currency' not in t:
        if t['symbol'] in ['BHP', 'CBA', 'CSL', 'NAB', 'BXB', 'CPU']:
            t['currency'] = 'AUD'
        else:
            t['currency'] = 'USD'
            
with open('trades.json', 'w') as f:
    json.dump(trades, f, indent=4)

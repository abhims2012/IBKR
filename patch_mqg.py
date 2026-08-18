import json
with open('trades.json', 'r') as f:
    trades = json.load(f)

for t in trades:
    if t['symbol'] == 'MQG':
        t['currency'] = 'AUD'
            
with open('trades.json', 'w') as f:
    json.dump(trades, f, indent=4)

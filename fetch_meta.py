import json
import os
import yfinance as yf

meta_path = 'company_meta.json'
meta_data = {}
if os.path.exists(meta_path):
    try:
        with open(meta_path, 'r') as f:
            meta_data = json.load(f)
    except:
        pass

watchlist = []
with open('watchlist.json', 'r') as f:
    watchlist = json.load(f)

trades = []
if os.path.exists('trades.json'):
    with open('trades.json', 'r') as f:
        trades = json.load(f)

# Collect all unique symbols with their currency
symbols_to_fetch = {}
for w in watchlist:
    symbols_to_fetch[w['symbol']] = w.get('currency', 'USD')
for t in trades:
    if t['symbol'] not in symbols_to_fetch:
        symbols_to_fetch[t['symbol']] = t.get('currency', 'USD')

new_fetches = 0
for sym, curr in symbols_to_fetch.items():
    if sym in meta_data and 'name' in meta_data[sym]:
        continue
        
    print(f"Fetching {sym}...")
    yf_sym = f"{sym}.AX" if curr == 'AUD' else sym
    try:
        ticker = yf.Ticker(yf_sym)
        info = ticker.info
        name = info.get('shortName', sym)
        sector = info.get('sector', 'Unknown')
        meta_data[sym] = {'name': name, 'sector': sector}
        new_fetches += 1
    except Exception as e:
        print(f"Failed to fetch {sym}: {e}")
        meta_data[sym] = {'name': sym, 'sector': 'Unknown'}

with open(meta_path, 'w') as f:
    json.dump(meta_data, f, indent=4)

print(f"Done! Fetched {new_fetches} new company profiles.")

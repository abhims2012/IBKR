import json
import urllib.request
import re

# Fetch S&P 100 components to guarantee top quality highly liquid US stocks
url = "https://en.wikipedia.org/wiki/S%26P_100"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

table_match = re.search(r'<table class="wikitable sortable.*?>(.*?)</table>', html, re.DOTALL)
tickers = []
if table_match:
    rows = re.findall(r'<tr>(.*?)</tr>', table_match.group(1), re.DOTALL)
    for row in rows:
        cols = re.findall(r'<td>(.*?)</td>', row, re.DOTALL)
        if len(cols) >= 1:
            ticker = re.sub(r'<[^>]+>', '', cols[0]).strip()
            # Handle dots in tickers e.g. BRK.B -> BRK-B or BRK B. IBKR uses BRK B or just BRK.B. Let's just skip complex ones.
            if '.' in ticker: continue
            if ticker and ticker not in tickers:
                tickers.append(ticker)

print(f"Scraped {len(tickers)} S&P 100 tickers.")

# Load watchlist
with open('watchlist.json', 'r') as f:
    watchlist = json.load(f)
    
existing_symbols = [item['symbol'] for item in watchlist]

added = 0
for t in tickers:
    if t not in existing_symbols:
        watchlist.append({
            "symbol": t,
            "exchange": "SMART",
            "currency": "USD"
        })
        added += 1
        
with open('watchlist.json', 'w') as f:
    json.dump(watchlist, f, indent=4)
    
print(f"Added {added} new high-liquidity US stocks to the watchlist. Total Watchlist size is now {len(watchlist)}.")

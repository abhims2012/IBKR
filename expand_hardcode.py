import json

top_us_stocks = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK B", "LLY", "V", 
    "JNJ", "XOM", "WMT", "JPM", "MA", "PG", "AVGO", "HD", "CVX", "MRK", "ORCL", 
    "ABBV", "PEP", "COST", "KO", "BAC", "ADBE", "TMO", "CSCO", "MCD", "PFE", "CRM", 
    "NFLX", "AMD", "ABT", "LIN", "CMCSA", "DHR", "INTC", "TXN", "WFC", "DIS", "PM", 
    "COP", "VZ", "NEE", "INTU", "QCOM", "IBM", "AMGN", "UNH", "SPY", "QQQ", "DIA",
    "BA", "HON", "UNP", "GE", "RTX", "CAT", "UPS", "LMT", "DE", "MMM", "GS", "MS",
    "BLK", "C", "AXP", "T", "TMUS", "CHTR", "NKE", "SBUX", "BKNG", "TJX", "TGT",
    "LOW", "SYY", "CVS", "CI", "UNP", "ISRG", "SYK", "MDT", "GILD", "VRTX", "REGN",
    "ZTS", "BDX", "BSX", "EW", "ILMN", "ALGN", "IDXX", "A", "MTD", "WAT", "PKI",
    "IQV", "CRL", "DXCM", "PODD", "TFX", "COO", "HOLX", "STE", "XRAY", "HSIC",
    "PDCO", "CYH", "UHS", "THC", "HCA", "CAH", "MCK", "ABC", "CNC", "MOH", "HUM",
    "CVS", "WBA", "RAD", "GPC", "ORLY", "AZO", "AAP", "TSCO", "HD", "LOW", "FND",
    "TSLA", "F", "GM", "HMC", "TM", "TTM", "STLA", "RACE", "HOG", "PII", "THO",
    "WGO", "LCII", "PATK", "SNDR", "KNX", "JBHT", "ODFL", "SAIA", "ARCB", "YRCW",
    "XPO", "CHRW", "EXPD", "LSTR", "RXO", "GXO", "HUBG", "UNP", "CSX", "NSC", "CP"
]

with open('watchlist.json', 'r') as f:
    watchlist = json.load(f)
    
existing = set([item['symbol'] for item in watchlist])

added = 0
for t in top_us_stocks:
    if t not in existing:
        watchlist.append({
            "symbol": t,
            "exchange": "SMART",
            "currency": "USD"
        })
        added += 1

with open('watchlist.json', 'w') as f:
    json.dump(watchlist, f, indent=4)
    
print(f"Added {added} new high-liquidity US stocks. Total Watchlist size: {len(watchlist)}.")

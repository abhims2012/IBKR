import json
import os

us_symbols = [
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'META', 'GOOGL', 'TSLA', 'BRK.B', 'AVGO', 'JPM',
    'UNH', 'LLY', 'V', 'XOM', 'JNJ', 'PG', 'MA', 'HD', 'CVX', 'MRK',
    'ABBV', 'PEP', 'COST', 'KO', 'ADBE', 'WMT', 'MCD', 'CRM', 'TMO', 'CSCO',
    'ACN', 'BAC', 'NFLX', 'LIN', 'AMD', 'CMCSA', 'INTC', 'ABT', 'ORCL', 'DHR',
    'PFE', 'WFC', 'TXN', 'DIS', 'PM', 'COP', 'VZ', 'NEE', 'INTU', 'QCOM'
]

asx_symbols = [
    'BHP', 'CBA', 'CSL', 'NAB', 'WBC', 'ANZ', 'MQG', 'WES', 'TLS', 'RIO',
    'GMG', 'TCL', 'FMG', 'WOW', 'COL', 'STO', 'WDS', 'ALL', 'QBE', 'SCG',
    'BXB', 'NCM', 'COH', 'SUN', 'MIN', 'RMD', 'REA', 'AMC', 'SHL', 'S32',
    'SGP', 'PLS', 'IAG', 'CPU', 'NST', 'BSL', 'XRO', 'ORG', 'FPH', 'VCX',
    'APA', 'TRE', 'ASX', 'SEK', 'SVW', 'ALX', 'CAR', 'TWE', 'GPT', 'AWC'
]

watchlist = []

for sym in us_symbols:
    watchlist.append({'symbol': sym, 'exchange': 'SMART', 'currency': 'USD'})

for sym in asx_symbols:
    watchlist.append({'symbol': sym, 'exchange': 'SMART', 'currency': 'AUD'})

with open('watchlist.json', 'w') as f:
    json.dump(watchlist, f, indent=4)

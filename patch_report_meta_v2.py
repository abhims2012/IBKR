with open('report.py', 'r') as f:
    code = f.read()

# Replace generate_and_push_report def to load metadata
code = code.replace(
'''def generate_and_push_report(ib):''',
'''def generate_and_push_report(ib):
    meta_data = {}
    try:
        with open(os.path.join(DIR, 'company_meta.json'), 'r') as f:
            meta_data = json.load(f)
    except:
        pass'''
)

# In the loop for pos in ib.positions(): we have:
# symbol = pos.contract.symbol
code = code.replace(
'''            symbol = pos.contract.symbol
            qty = pos.position''',
'''            symbol = pos.contract.symbol
            qty = pos.position
            comp_meta = meta_data.get(symbol, {'name': symbol, 'sector': 'Unknown'})
            name = comp_meta.get('name', symbol)
            sector = comp_meta.get('sector', 'Unknown')
            currency = pos.contract.currency'''
)

# And in positions.append
code = code.replace(
'''            positions.append({
                'symbol': symbol,''',
'''            positions.append({
                'symbol': symbol,
                'name': name,
                'sector': sector,
                'currency': currency,'''
)

# For trades_history loop
code = code.replace(
'''    # Inject trade history if exists
    trade_history = []
    trades_path = os.path.join(DIR, 'trades.json')''',
'''    # Inject trade history if exists
    trade_history = []
    trades_path = os.path.join(DIR, 'trades.json')'''
)

# At the end of trades history load
code = code.replace(
'''            # Sort by date descending
            trade_history.sort(key=lambda x: x.get('date', ''), reverse=True)''',
'''            for t in trade_history:
                comp_meta = meta_data.get(t['symbol'], {'name': t['symbol'], 'sector': 'Unknown'})
                t['name'] = comp_meta.get('name', t['symbol'])
                t['sector'] = comp_meta.get('sector', 'Unknown')
            
            # Sort by date descending
            trade_history.sort(key=lambda x: x.get('date', ''), reverse=True)'''
)

with open('report.py', 'w') as f:
    f.write(code)

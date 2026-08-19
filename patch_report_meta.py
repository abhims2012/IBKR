with open('report.py', 'r') as f:
    code = f.read()

code = code.replace(
'''def generate_and_push_report(ib):''',
'''def generate_and_push_report(ib):
    # Load company metadata
    meta_data = {}
    try:
        with open(os.path.join(DIR, 'company_meta.json'), 'r') as f:
            meta_data = json.load(f)
    except:
        pass'''
)

code = code.replace(
'''            positions.append({
                'symbol': symbol,
                'quantity': qty,
                'avg_cost': avg_cost,
                'market_price': price,
                'unrealized_pnl': pos_unrealized,
                'chart_json': chart_json,
                'currency': pos.contract.currency
            })''',
'''            comp_meta = meta_data.get(symbol, {'name': symbol, 'sector': 'Unknown'})
            positions.append({
                'symbol': symbol,
                'name': comp_meta.get('name', symbol),
                'sector': comp_meta.get('sector', 'Unknown'),
                'quantity': qty,
                'avg_cost': avg_cost,
                'market_price': price,
                'unrealized_pnl': pos_unrealized,
                'chart_json': chart_json,
                'currency': pos.contract.currency
            })'''
)

code = code.replace(
'''    # Inject trade history if exists''',
'''    # Inject trade history and append metadata
    for t in trades_history:
        comp_meta = meta_data.get(t['symbol'], {'name': t['symbol'], 'sector': 'Unknown'})
        t['name'] = comp_meta.get('name', t['symbol'])
        t['sector'] = comp_meta.get('sector', 'Unknown')
        
    # Inject trade history if exists'''
)

with open('report.py', 'w') as f:
    f.write(code)

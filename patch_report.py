with open('report.py', 'r') as f:
    code = f.read()

code = code.replace(
'''            positions.append({
                'symbol': symbol,
                'quantity': qty,
                'avg_cost': avg_cost,
                'market_price': price,
                'unrealized_pnl': pos_unrealized,
                'chart_json': chart_json
            })''',
'''            positions.append({
                'symbol': symbol,
                'quantity': qty,
                'avg_cost': avg_cost,
                'market_price': price,
                'unrealized_pnl': pos_unrealized,
                'chart_json': chart_json,
                'currency': pos.contract.currency
            })'''
)

with open('report.py', 'w') as f:
    f.write(code)

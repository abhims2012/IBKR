with open('report.py', 'r') as f:
    code = f.read()

code = code.replace(
'''    if os.path.exists(trades_path):
        try:
            with open(trades_path, 'r') as f:
                history = json.load(f)
        except Exception as e:
            print(f"Error loading trades.json: {e}")''',
'''    if os.path.exists(trades_path):
        try:
            with open(trades_path, 'r') as f:
                history = json.load(f)
                history.sort(key=lambda x: x.get('date', ''), reverse=True)
                for t in history:
                    comp_meta = meta_data.get(t['symbol'], {'name': t['symbol'], 'sector': 'Unknown'})
                    t['name'] = comp_meta.get('name', t['symbol'])
                    t['sector'] = comp_meta.get('sector', 'Unknown')
        except Exception as e:
            print(f"Error loading trades.json: {e}")'''
)

with open('report.py', 'w') as f:
    f.write(code)

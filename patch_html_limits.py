with open('template.html', 'r') as f:
    code = f.read()

code = code.replace(
'''                            <li><strong>Max ASX Order:</strong>  AUD</li>
                            <li><strong>Max US Order:</strong>  USD</li>
                            <li><strong>Daily ASX Limit:</strong>  AUD</li>
                            <li><strong>Daily US Limit:</strong>  USD</li>''',
'''                            <li><strong>Max ASX Order:</strong>  AUD</li>
                            <li><strong>Max US Order:</strong>  USD</li>
                            <li><strong>Total Exposure Limit (ASX):</strong> ,000 AUD</li>
                            <li><strong>Total Exposure Limit (US):</strong> ,000 USD</li>'''
)

with open('template.html', 'w') as f:
    f.write(code)

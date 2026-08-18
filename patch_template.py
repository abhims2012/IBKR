with open('template.html', 'r') as f:
    code = f.read()

code = code.replace('<li><strong>Take Profit:</strong> +10%</li>', '<li><strong>Take Profit:</strong> +5%</li>')
code = code.replace('<li><strong>Stop Loss:</strong> -5%</li>', '<li><strong>Stop Loss:</strong> -10%</li>')

with open('template.html', 'w') as f:
    f.write(code)

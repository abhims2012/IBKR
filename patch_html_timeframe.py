with open('template.html', 'r') as f:
    code = f.read()

code = code.replace(
    "1-hour 14-RSI &lt; 30", 
    "15-min 14-RSI &lt; 30"
)

with open('template.html', 'w') as f:
    f.write(code)

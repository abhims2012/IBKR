with open('bot.py', 'r') as f:
    code = f.read()

code = code.replace(
    "1-hour 14-period RSI < 30", 
    "15-min 14-period RSI < 30"
)
code = code.replace(
    "barSizeSetting='1 hour'", 
    "barSizeSetting='15 mins'"
)
code = code.replace(
    "Hourly RSI is {current_rsi:.2f}", 
    "15-Min RSI is {current_rsi:.2f}"
)
code = code.replace(
    "& 1H-RSI =", 
    "& 15M-RSI ="
)

with open('bot.py', 'w') as f:
    f.write(code)

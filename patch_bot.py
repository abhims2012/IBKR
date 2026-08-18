with open('bot.py', 'r') as f:
    code = f.read()

code = code.replace('TAKE_PROFIT_PCT = 0.10 # 10%', 'TAKE_PROFIT_PCT = 0.05 # 5%')
code = code.replace('STOP_LOSS_PCT = 0.05   # 5%', 'STOP_LOSS_PCT = 0.10  # 10%')

with open('bot.py', 'w') as f:
    f.write(code)

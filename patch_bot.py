with open('bot.py', 'r') as f:
    code = f.read()

code = code.replace(
'''def log_trade(symbol, action, price, sma, rsi, rationale_msg):''',
'''def log_trade(symbol, action, price, sma, rsi, rationale_msg, currency=''):'''
)

code = code.replace(
'''        'rationale': rationale_msg
    }''',
'''        'rationale': rationale_msg,
        'currency': currency
    }'''
)

code = code.replace(
'''            log_trade(symbol, 'BUY', price, current_sma, current_rsi, setup_msg)''',
'''            log_trade(symbol, 'BUY', price, current_sma, current_rsi, setup_msg, currency)'''
)

with open('bot.py', 'w') as f:
    f.write(code)

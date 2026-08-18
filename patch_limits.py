with open('bot.py', 'r') as f:
    code = f.read()

code = code.replace(
    "MAX_ORDER_SIZE_USD = 100.0", 
    "MAX_ORDER_SIZE_USD = 500.0"
)
code = code.replace(
    "DAILY_SPEND_LIMIT_USD = 1500.0", 
    "DAILY_SPEND_LIMIT_USD = 5000.0"
)
code = code.replace(
    "DAILY_SPEND_LIMIT_AUD = 1500.0", 
    "DAILY_SPEND_LIMIT_AUD = 5000.0"
)

with open('bot.py', 'w') as f:
    f.write(code)

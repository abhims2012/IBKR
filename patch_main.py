with open('bot.py', 'r') as f:
    code = f.read()

replacement = '''    while True:
        if not ib.isConnected():
            print("Connection to IBKR lost. Attempting to reconnect...")
            try:
                await ib.connectAsync('127.0.0.1', PORT, clientId=CLIENT_ID)
                print("Reconnected successfully.")
            except Exception as e:
                print(f"Reconnection failed: {e}. Retrying in 10 seconds...")
                await asyncio.sleep(10)
                continue
                
        now_aest = datetime.datetime.now(aest)'''

code = code.replace(
'''    while True:
        now_aest = datetime.datetime.now(aest)''',
replacement
)

with open('bot.py', 'w') as f:
    f.write(code)

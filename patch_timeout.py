with open('report.py', 'r') as f:
    code = f.read()

code = code.replace(
'''            bars = await ib.reqHistoricalDataAsync(
                contract, endDateTime='', durationStr='60 D', barSizeSetting='1 day',
                whatToShow='TRADES', useRTH=True, formatDate=1
            )''',
'''            try:
                bars = await asyncio.wait_for(ib.reqHistoricalDataAsync(
                    contract, endDateTime='', durationStr='60 D', barSizeSetting='1 day',
                    whatToShow='TRADES', useRTH=True, formatDate=1
                ), timeout=15.0)
            except asyncio.TimeoutError:
                print(f"Timeout getting historical data for {symbol} chart")
                bars = []'''
)

with open('report.py', 'w') as f:
    f.write(code)

with open('bot.py', 'r') as f:
    code = f.read()

code = code.replace(
'''        daily_bars = await ib.reqHistoricalDataAsync(
            contract,
            endDateTime='',
            durationStr='100 D', # 100 days
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )''',
'''        daily_bars = await asyncio.wait_for(
            ib.reqHistoricalDataAsync(
                contract,
                endDateTime='',
                durationStr='100 D', # 100 days
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            ),
            timeout=15.0
        )'''
)

code = code.replace(
'''        hourly_bars = await ib.reqHistoricalDataAsync(
            contract,
            endDateTime='',
            durationStr='10 D',
            barSizeSetting='1 hour',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )''',
'''        hourly_bars = await asyncio.wait_for(
            ib.reqHistoricalDataAsync(
                contract,
                endDateTime='',
                durationStr='10 D',
                barSizeSetting='1 hour',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            ),
            timeout=15.0
        )'''
)

code = code.replace(
'''    except Exception as e:
        return False, f"Error calculating technicals: {e}", 0, 0''',
'''    except asyncio.TimeoutError:
        return False, "Timeout: IBKR failed to respond with data within 15 seconds.", 0, 0
    except Exception as e:
        return False, f"Error calculating technicals: {e}", 0, 0'''
)

with open('bot.py', 'w') as f:
    f.write(code)

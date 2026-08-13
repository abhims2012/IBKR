from ib_async import IB, Stock, util
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=18)
ib.sleep(2)
for pos in ib.positions():
    if pos.contract.symbol == 'BHP':
        try:
            print(f"Contract before: {pos.contract}")
            ib.qualifyContracts(pos.contract)
            print(f"Contract after: {pos.contract}")
            bars = ib.reqHistoricalData(
                pos.contract,
                endDateTime='',
                durationStr='60 D',
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            print(f"Got {len(bars)} bars")
        except Exception as e:
            print(f"Error: {e}")
ib.disconnect()

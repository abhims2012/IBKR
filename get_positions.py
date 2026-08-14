from ib_async import IB
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=35)
for pos in ib.positions():
    print(f"Pos: {pos.contract.symbol} | {pos.contract.currency} | {pos.position} | {pos.avgCost}")
ib.disconnect()

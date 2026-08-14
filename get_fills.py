from ib_async import IB
import datetime
import pytz

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=33)
fills = ib.fills()
for fill in fills:
    print(f"Fill: {fill.time} | {fill.contract.symbol} | {fill.execution.side} | {fill.execution.shares} | {fill.execution.price}")
ib.disconnect()

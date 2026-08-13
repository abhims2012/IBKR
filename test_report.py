from ib_async import IB, util
from report import generate_and_push_report
import asyncio

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=17)
ib.sleep(2)
print(f"Positions before report: {ib.positions()}")
asyncio.run(generate_and_push_report(ib))

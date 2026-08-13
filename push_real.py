import asyncio
from ib_async import IB
from report import generate_and_push_report

async def main():
    ib = IB()
    await ib.connectAsync('127.0.0.1', 7497, clientId=22)
    await ib.reqPositionsAsync()
    await asyncio.sleep(2)
    await generate_and_push_report(ib)

asyncio.run(main())

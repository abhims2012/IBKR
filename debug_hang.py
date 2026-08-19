import os
import asyncio
from ib_async import IB

async def main():
    print("Connecting...")
    ib = IB()
    try:
        await asyncio.wait_for(ib.connectAsync('127.0.0.1', 7497, clientId=998), timeout=5.0)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return
        
    print("Getting positions...")
    positions = ib.positions()
    print(f"Got {len(positions)} positions.")
    
    for pos in positions:
        print(f"Qualifying {pos.contract.symbol}...")
        try:
            await asyncio.wait_for(ib.qualifyContractsAsync(pos.contract), timeout=5.0)
            print("Qualified!")
        except Exception as e:
            print(f"Failed to qualify {pos.contract.symbol}: {e}")
            
    print("Done testing.")
    ib.disconnect()

asyncio.run(main())

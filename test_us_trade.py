from ib_async import IB, Stock, LimitOrder, Order
import json
import datetime
import pytz
import asyncio
import os
from report import generate_and_push_report

async def place_test_trade():
    ib = IB()
    await ib.connectAsync('127.0.0.1', 7497, clientId=999)
    
    contract = Stock('AAPL', 'SMART', 'USD')
    await ib.qualifyContractsAsync(contract)
    
    # Get last price using historical data instead of ticker
    bars = await ib.reqHistoricalDataAsync(contract, endDateTime='', durationStr='1 D', barSizeSetting='1 day', whatToShow='TRADES', useRTH=True, formatDate=1)
    price = bars[-1].close
        
    print(f"AAPL Last Price: {price}")
    
    # Create Bracket Order
    qty = 1
    takeProfitPrice = round(price * 1.05, 2)
    stopLossPrice = round(price * 0.90, 2)
    
    parent = LimitOrder('BUY', qty, price)
    parent.orderId = ib.client.getReqId()
    parent.transmit = False
    parent.outsideRth = True
    parent.tif = 'GTC'
    
    takeProfit = LimitOrder('SELL', qty, takeProfitPrice)
    takeProfit.orderId = ib.client.getReqId()
    takeProfit.transmit = False
    takeProfit.parentId = parent.orderId
    takeProfit.outsideRth = True
    takeProfit.tif = 'GTC'
    
    stopLoss = Order(
        orderId=ib.client.getReqId(),
        action='SELL',
        orderType='STP',
        totalQuantity=qty,
        auxPrice=stopLossPrice,
        parentId=parent.orderId,
        transmit=True,
        outsideRth=True,
        tif='GTC'
    )
    
    # Place Orders
    ib.placeOrder(contract, parent)
    ib.placeOrder(contract, takeProfit)
    ib.placeOrder(contract, stopLoss)
    
    print("Test US Bracket Order Placed!")
    
    # Log trade
    trade = {
        'date': datetime.datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S'),
        'symbol': 'AAPL',
        'action': 'BUY',
        'price': price,
        'sma': 0,
        'rsi': 0,
        'rationale': "Manual Test Trade to verify US routing",
        'currency': 'USD'
    }
    
    history = []
    trades_path = 'trades.json'
    if os.path.exists(trades_path):
        with open(trades_path, 'r') as f:
            history = json.load(f)
            
    history.append(trade)
    with open(trades_path, 'w') as f:
        json.dump(history, f, indent=4)
        
    print("Log updated. Triggering report push...")
    
    # Push report
    await ib.reqPositionsAsync()
    await asyncio.sleep(2)
    await generate_and_push_report(ib)
    
    ib.disconnect()
    print("Done!")

asyncio.run(place_test_trade())

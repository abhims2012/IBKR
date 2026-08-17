from ib_async import IB
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=37)
for trade in ib.trades():
    if trade.contract.symbol == 'BXB':
        print(f"BXB Order: {trade.order.action} {trade.order.totalQuantity} | Status: {trade.orderStatus.status} | Filled: {trade.orderStatus.filled}")
ib.disconnect()

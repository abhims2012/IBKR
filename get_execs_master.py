from ib_async import IB, ExecutionFilter
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=0)
execs = ib.reqExecutions(ExecutionFilter(clientId=0))
for ex in execs:
    print(f"Exec: {ex.execution.time} | {ex.contract.symbol} | {ex.execution.side} | {ex.execution.shares} | {ex.execution.price}")
ib.disconnect()

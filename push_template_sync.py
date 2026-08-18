from ib_async import IB, util
from report import generate_and_push_report

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=89)
ib.reqPositions()
util.sleep(2)
ib.run(generate_and_push_report(ib))
ib.disconnect()

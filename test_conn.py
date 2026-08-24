from ib_async import IB
import sys
ib = IB()
try:
    print("Connecting...")
    ib.connect('127.0.0.1', 7497, clientId=9991, timeout=5.0)
    print("Connected successfully!")
    ib.disconnect()
except Exception as e:
    print(f"Error: {e}")
sys.exit(0)

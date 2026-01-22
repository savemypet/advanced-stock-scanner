from ib_insync import IB, util

ib = IB()
util.startLoop()

try:
    print("Connecting to IB Gateway on port 4001...")
    ib.connect('127.0.0.1', 4001, clientId=1)
    print("SUCCESS! Connected to IBKR Gateway")
    print(f"Connected: {ib.isConnected()}")
    ib.disconnect()
    print("Disconnected successfully")
except Exception as e:
    print(f"FAILED: {e}")
    print("\nMake sure:")
    print("1. IB Gateway is running and logged in")
    print("2. Configure > API > Settings > Enable ActiveX and Socket Clients is CHECKED")
    print("3. Socket port is set to 4001")

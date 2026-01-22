#!/usr/bin/env python3
"""Test IBKR Connection on multiple ports"""
import sys
import logging
from ib_insync import IB, util

logging.basicConfig(level=logging.WARNING)  # Reduce noise

def test_port(host, port, client_id):
    """Test connection on a specific port"""
    try:
        util.startLoop()
        ib = IB()
        ib.connect(host, port, clientId=client_id, timeout=2)
        if ib.isConnected():
            print(f"SUCCESS! Connected on port {port}")
            ib.disconnect()
            return True
    except Exception as e:
        pass
    return False

print("Testing IB Gateway connection on common ports...")
print("=" * 60)

ports_to_test = [7496, 7497, 4001, 4002]  # Common IBKR ports

for port in ports_to_test:
    print(f"Testing port {port}...", end=" ")
    if test_port('127.0.0.1', port, 1):
        print(f"CONNECTED!")
        sys.exit(0)
    else:
        print(f"Failed")

print("\nNo connection found on any port.")
print("\nPlease check:")
print("1. IB Gateway is running and fully logged in")
print("2. API is enabled: Configure > API > Settings")
print("3. Socket port is set correctly in IB Gateway")
print("4. Trusted IPs includes 127.0.0.1 (or is empty for localhost)")

sys.exit(1)

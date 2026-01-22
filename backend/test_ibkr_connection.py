#!/usr/bin/env python3
"""Test IBKR Connection - Check if Gateway is accessible"""
import sys
import logging
from ib_insync import IB, util

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_connection():
    """Test connection to IB Gateway"""
    print("=" * 60)
    print("Testing IBKR Connection")
    print("=" * 60)
    
    # Connection settings
    host = '127.0.0.1'
    port = 7497  # Paper trading
    client_id = 1
    
    print(f"\nConnection Settings:")
    print(f"   Host: {host}")
    print(f"   Port: {port} (7497 = Paper Trading, 7496 = Live)")
    print(f"   Client ID: {client_id}")
    
    print(f"\nAttempting to connect...")
    
    try:
        # Start event loop (required for ib_insync)
        util.startLoop()
        
        # Create IB instance
        ib = IB()
        
        # Try to connect
        print(f"   Connecting to {host}:{port}...")
        ib.connect(host, port, clientId=client_id)
        
        if ib.isConnected():
            print(f"\nSUCCESS! Connected to IB Gateway!")
            print(f"   Connection Status: Connected")
            
            # Get account info
            try:
                accounts = ib.accountValues()
                if accounts:
                    print(f"\nAccount Information:")
                    for acc in accounts[:5]:  # Show first 5
                        print(f"   {acc.tag}: {acc.value}")
            except Exception as e:
                print(f"   (Could not fetch account info: {e})")
            
            # Disconnect
            ib.disconnect()
            print(f"\nConnection test PASSED!")
            return True
        else:
            print(f"\n❌ FAILED: Not connected after connect() call")
            return False
            
    except ConnectionRefusedError:
        print(f"\nFAILED: Connection Refused")
        print(f"\nTroubleshooting:")
        print(f"   1. Make sure IB Gateway is running")
        print(f"   2. Check that the port is correct (7497 for paper, 7496 for live)")
        print(f"   3. In IB Gateway: Configure > API > Settings")
        print(f"      - Enable 'Enable ActiveX and Socket Clients'")
        print(f"      - Set 'Socket port' to {port}")
        print(f"      - Make sure 'Read-Only API' is unchecked (if you want to trade)")
        return False
        
    except Exception as e:
        error_msg = str(e)
        print(f"\nFAILED: {error_msg}")
        
        if "event loop" in error_msg.lower():
            print(f"\nEvent Loop Error - This should be fixed with util.startLoop()")
        elif "connection" in error_msg.lower():
            print(f"\nConnection Error:")
            print(f"   1. Check IB Gateway is running")
            print(f"   2. Check API is enabled in Configure > API > Settings")
            print(f"   3. Check port number matches (7497/7496)")
        else:
            print(f"\nError Details: {error_msg}")
        
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)

import yfinance as yf
import json

try:
    print("Testing Yahoo Finance API...")
    stock = yf.Ticker('TSLA')
    info = stock.info
    
    print(f"\nTSLA Data:")
    print(f"Name: {info.get('longName', 'N/A')}")
    print(f"Price: {info.get('currentPrice', 'N/A')}")
    print(f"Change: {info.get('regularMarketChangePercent', 'N/A')}")
    print(f"Volume: {info.get('volume', 'N/A')}")
    print(f"Float: {info.get('floatShares', 'N/A')}")
    
    print("\n✅ Yahoo Finance is working!")
    
except Exception as e:
    print(f"\n❌ Yahoo Finance Error: {str(e)}")
    if "429" in str(e):
        print("🔴 RATE LIMITED - Need to wait 30-60 minutes")
    else:
        print(f"Error type: {type(e).__name__}")

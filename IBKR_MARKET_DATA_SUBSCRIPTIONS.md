# Interactive Brokers Market Data Subscriptions Guide

## Error 10089: "Requested market data requires additional subscription for API"

This error occurs because your code uses **SMART routing** (`Stock(symbol, 'SMART', 'USD')`), which requires subscriptions to **all exchanges** that SMART might route to.

## Required Subscriptions for US Stocks

### Option 1: US Securities Snapshot and Futures Value Bundle (RECOMMENDED)
- **Cost**: $10/month
- **Waived if**: Your account generates $30+ in monthly commissions
- **Includes**:
  - Real-time top-of-book quotes for NYSE, AMEX, NASDAQ stocks
  - Bonds, futures, and OTC stocks
  - This is the **easiest solution** for scanning US stocks

### Option 2: Individual Exchange Subscriptions
If you prefer to subscribe individually:

- **NYSE (Network A)**: $1.50/month
- **AMEX (Network B)**: $1.50/month  
- **NASDAQ (Network C)**: $1.50/month
- **Total**: $4.50/month for all three

### Option 3: Snapshot Mode (For Occasional Use)
- **Cost**: $0.01 per refresh request
- **Cap**: $1.50/month per exchange
- **Best for**: Testing or very light usage

## How to Subscribe

1. **Log into TWS (Trader Workstation)**
2. **Go to**: Account → Market Data Subscriptions
3. **Select**: "US Securities Snapshot and Futures Value Bundle"
4. **Or**: Subscribe to individual exchanges (NYSE, AMEX, NASDAQ)
5. **Confirm** the subscription

## Alternative: Use Specific Exchanges Instead of SMART

If you want to avoid subscription costs, you can modify the code to use specific exchanges instead of SMART routing:

```python
# Instead of:
contract = Stock(symbol, 'SMART', 'USD')

# Use specific exchanges:
# For NYSE stocks:
contract = Stock(symbol, 'NYSE', 'USD')
# For NASDAQ stocks:
contract = Stock(symbol, 'NASDAQ', 'USD')
# For AMEX stocks:
contract = Stock(symbol, 'AMEX', 'USD')
```

**Note**: This requires knowing which exchange each stock trades on, which adds complexity.

## Current Code Location

Your code uses SMART routing in these locations:
- `backend/app.py` line 949: `contract = Stock(symbol, 'SMART', 'USD')` (real-time scanner)
- `backend/app.py` line 1134: `contract = Stock(symbol, 'SMART', 'USD')` (historical data)

## Recommendation

**Subscribe to "US Securities Snapshot and Futures Value Bundle"** ($10/month, waived with $30+ commissions):
- Simplest solution
- Works with all US stocks
- No code changes needed
- If you trade regularly, the commission waiver likely applies

## Checking Your Current Subscriptions

1. In TWS: Account → Market Data Subscriptions
2. Look for active subscriptions
3. Check if "US Securities Snapshot and Futures Value Bundle" is listed

## After Subscribing

1. Restart TWS/IB Gateway
2. Reconnect your scanner
3. Error 10089 should disappear
4. Real-time data should work for all US stocks

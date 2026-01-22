# ⚠️ CORRECT Market Data Subscriptions to Add

## ❌ DO NOT Subscribe To:
- NYSE ARCA Order Imbalances
- NYSE MKT Order Imbalances  
- NYSE Order Imbalances

**These are NOT what you need!** Order Imbalances show buy/sell order imbalances at market open/close, but they **do NOT provide the actual price/quote data** needed for SMART routing.

## ✅ Subscribe To ONE of These Instead:

### Option 1: US Securities Snapshot and Futures Value Bundle (BEST)
- **Search for**: "US Securities Snapshot" or "US Securities Snapshot and Futures Value Bundle"
- **Cost**: $10/month (likely waived with your commission threshold)
- **Covers**: NYSE, AMEX, NASDAQ consolidated market data
- **Works with**: SMART routing (no code changes needed)

### Option 2: Individual Exchange Subscriptions
If you can't find the bundle, subscribe to these individually:

1. **NYSE (Network A)** - $1.50/month
   - Search for: "NYSE Network A" or "NYSE (Network A)"
   
2. **AMEX (Network B)** - $1.50/month
   - Search for: "AMEX Network B" or "AMEX (Network B)"
   
3. **NASDAQ (Network C)** - $1.50/month
   - Search for: "NASDAQ Network C" or "NASDAQ (Network C)"

**Total**: $4.50/month (likely waived with your commission threshold)

## How to Find the Correct Subscriptions

1. **Cancel** the Order Imbalances subscriptions you just selected
2. In the subscription browser/search, look for:
   - "US Securities Snapshot and Futures Value Bundle"
   - "NYSE Network A" (NOT "Order Imbalances")
   - "AMEX Network B"
   - "NASDAQ Network C"
3. Make sure the description mentions:
   - "Real-time quotes"
   - "Market data"
   - "Level 1" or "L1" data
   - NOT "Order Imbalances"

## What Each Type Does

| Subscription Type | What It Provides | Needed for Scanner? |
|------------------|------------------|---------------------|
| **Order Imbalances** | Buy/sell order imbalances at open/close | ❌ NO |
| **US Securities Snapshot Bundle** | Real-time price/quote data for NYSE/AMEX/NASDAQ | ✅ YES |
| **NYSE Network A** | Real-time price/quote data for NYSE stocks | ✅ YES |
| **AMEX Network B** | Real-time price/quote data for AMEX stocks | ✅ YES |
| **NASDAQ Network C** | Real-time price/quote data for NASDAQ stocks | ✅ YES |

## After Subscribing to the Correct Ones

1. **Restart TWS/IB Gateway** (required!)
2. **Reconnect your scanner**
3. **Test a scan** - Error 10089 should disappear
4. **Check logs** - you should see valid price data instead of NaN

## Why Order Imbalances Won't Work

Your scanner needs **real-time price and quote data** (bid, ask, last price, volume) to:
- Get current stock prices
- Calculate gains/losses
- Filter stocks by price range
- Check volume

Order Imbalances only show the **imbalance of buy vs sell orders** at market open/close - they don't provide the actual price data your scanner needs.

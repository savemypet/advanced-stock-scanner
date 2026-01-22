# How to Add Missing Market Data Subscription

## Current Status
You have "US Real-Time Non Consolidated Streaming Quotes (IBKR-PRO)" but this **does NOT** cover consolidated exchange data needed for SMART routing.

## What You Need to Add

### Option 1: US Securities Snapshot and Futures Value Bundle (BEST)
- **Cost**: $10/month (likely waived with your commission threshold)
- **Covers**: NYSE, AMEX, NASDAQ consolidated data
- **Works with**: SMART routing (no code changes needed)

### Option 2: Individual Exchange Subscriptions
- **NYSE (Network A)**: $1.50/month
- **AMEX (Network B)**: $1.50/month
- **NASDAQ (Network C)**: $1.50/month
- **Total**: $4.50/month

## Step-by-Step Instructions

### Method 1: Through TWS (Trader Workstation)
1. Open **TWS**
2. Go to: **Account** → **Market Data Subscriptions**
3. Look for one of these buttons:
   - **"Add Subscriptions"**
   - **"Browse Available Subscriptions"**
   - **"Subscribe to Additional Data"**
   - Or a **"+"** icon/button
4. In the search/filter, type: **"US Securities"** or **"NYSE"** or **"NASDAQ"**
5. Find **"US Securities Snapshot and Futures Value Bundle"**
6. Click **"Subscribe"** or **"Add"**
7. Confirm the subscription
8. **Restart TWS/IB Gateway**

### Method 2: Through Client Portal (Web)
1. Log into **IBKR Client Portal** (web.ibkr.com)
2. Go to: **Account Management** → **Market Data Subscriptions**
3. Click **"Add Subscriptions"** or **"Browse"**
4. Search for **"US Securities Snapshot and Futures Value Bundle"**
5. Subscribe
6. **Restart TWS/IB Gateway**

### Method 3: Contact IBKR Support
If you can't find the option to add subscriptions:
1. Call IBKR Support: **1-877-442-2757**
2. Or use Live Chat in Client Portal
3. Ask: "I need to subscribe to US Securities Snapshot and Futures Value Bundle for API access with SMART routing"

## After Subscribing

1. **Restart TWS/IB Gateway** (important!)
2. **Reconnect your scanner**
3. **Test with a scan** - Error 10089 should be gone
4. **Check logs** - you should see valid price data instead of NaN

## Verification

After subscribing, check:
- Your subscriptions list should show "US Securities Snapshot and Futures Value Bundle"
- Or you should see NYSE, AMEX, NASDAQ listed individually
- Your "US Equities" snapshot counter should start working

## Why This Is Needed

Your code uses SMART routing:
```python
contract = Stock(symbol, 'SMART', 'USD')
```

SMART routing requires subscriptions to **all exchanges** it might route to (NYSE, AMEX, NASDAQ). The "IBKR-PRO" subscription you have is for **non-consolidated** streaming quotes, which is different from the **consolidated** exchange data needed for SMART routing.

## Cost Note

Since you're already getting fee waivers on other subscriptions, the "US Securities Snapshot and Futures Value Bundle" will likely also be **waived** if you generate $30+ in monthly commissions (which you probably do, given your other waived subscriptions).

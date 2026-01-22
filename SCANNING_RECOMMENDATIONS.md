# Scanning Recommendations - How Many Stocks Per Minute?

## 🎯 Quick Answer

**For 10 stocks to pop up:**

### Option 1: Use Preloaded Stocks (BEST - No API Limits!)
- ✅ **Unlimited stocks** - No API calls needed
- ✅ **Instant results** - Already loaded with historical data
- ✅ **Works when market is closed**
- ✅ **Perfect for 10+ stocks**

**How to use:**
- The `preload-stocks` endpoint loads 30 popular stocks
- SimulatedScanner automatically uses these
- No rate limits - all data is pre-fetched

### Option 2: Real-time Data Only (FAST - Fewer Limits)
- ✅ **~10-20 stocks per minute** possible
- ✅ Uses `reqMktData` (real-time quotes)
- ⚠️ Limited historical data (only current price/volume)
- ✅ Good for quick screening

### Option 3: Historical Data (SLOW - Strict Limits)
- ⚠️ **Max 6 stocks per minute** (60 requests per 10 minutes)
- ⚠️ **Min 15 seconds** between identical requests
- ✅ Full historical data for AI analysis
- ✅ Complete chart data

## 📊 Recommended Scanning Strategy for 10 Stocks

### Best Approach: Hybrid Method

**Step 1: Use Preloaded Stocks (0 API calls)**
- Load 30 preloaded stocks instantly
- Filter by your preset criteria
- Get 10+ results immediately

**Step 2: Add Real-time Updates (Minimal API calls)**
- Use `reqMktData` for real-time price/volume
- ~10-20 stocks per minute possible
- Fast screening for new movers

**Step 3: Detailed Analysis (Only for promising stocks)**
- Use `reqHistoricalData` for full chart data
- Only for stocks that pass initial filters
- Respect 60 requests/10min limit

## ⚙️ Implementation for 10 Stocks Per Minute

### Current Implementation

Your scanner currently:
1. Scans from `active_symbols` list
2. Fetches data for each symbol
3. Applies preset filters
4. Returns matching stocks

**To get 10 stocks per minute:**

### Option A: Use Preloaded Stocks (Recommended)
```python
# In your scan endpoint
# 1. Get preloaded stocks (no API calls)
preloaded = get_preloaded_stocks()  # 30 stocks ready

# 2. Filter by your criteria
filtered = [s for s in preloaded if matches_criteria(s)]

# 3. Return top 10
return filtered[:10]  # Instant results!
```

### Option B: Real-time Screening
```python
# Use reqMktData for fast screening
# Can handle ~10-20 stocks per minute
for symbol in symbols[:10]:
    ticker = IBKR_INSTANCE.reqMktData(contract, '', False, False)
    IBKR_INSTANCE.sleep(0.1)  # 100ms delay = 10 stocks/second possible
    
    # Quick filter by price/volume
    if matches_quick_criteria(ticker):
        results.append(symbol)
```

### Option C: Historical Data (Slower)
```python
# Use reqHistoricalData - respect limits
# Max 6 per minute, so scan 6 stocks, wait 1 minute, scan 6 more
for i, symbol in enumerate(symbols):
    if i > 0 and i % 6 == 0:
        time.sleep(60)  # Wait 1 minute after every 6 stocks
    
    data = fetch_from_ibkr(symbol, '5m')
    if matches_criteria(data):
        results.append(data)
```

## 🚀 Recommended Configuration

### For 10 Stocks Per Minute:

**Settings:**
- **Primary Source**: Preloaded stocks (30 stocks, no limits)
- **Update Method**: Real-time `reqMktData` (10-20 stocks/min)
- **Detailed Analysis**: Historical data only for top picks (6/min max)

**Scan Flow:**
1. **Initial Load**: Use preloaded stocks → Get 10+ results instantly
2. **Real-time Updates**: Use `reqMktData` → Update prices every 10-20 seconds
3. **Detailed Charts**: Use `reqHistoricalData` → Only for stocks you're analyzing (respect 60/10min)

### Example Scan Cycle:

```
Minute 1:
  - Load preloaded stocks (0 API calls) → 10 results
  - Update prices with reqMktData (10 calls) → Fast!
  
Minute 2:
  - Continue updating prices (10 calls)
  - If new stock found, fetch historical data (1 call)
  
Minute 3-10:
  - Repeat price updates
  - Fetch historical data for new discoveries (max 6/min)
```

## 📈 Maximum Throughput

### Scenario 1: Preloaded Stocks Only
- **Stocks per minute**: Unlimited (30 preloaded)
- **API calls**: 0
- **Best for**: Initial screening, demo stocks

### Scenario 2: Real-time Only
- **Stocks per minute**: 10-20 (using reqMktData)
- **API calls**: 10-20 per minute
- **Best for**: Quick price/volume screening

### Scenario 3: Historical Data Only
- **Stocks per minute**: 6 (max 60 per 10 minutes)
- **API calls**: 6 per minute
- **Best for**: Full chart data, AI analysis

### Scenario 4: Hybrid (Recommended)
- **Initial**: 30 preloaded stocks (0 calls)
- **Updates**: 10-20 real-time (10-20 calls/min)
- **Details**: 6 historical (6 calls/min, only for new discoveries)
- **Total**: Can handle 10+ stocks easily!

## ✅ Answer to Your Question

**"Can I have 10 stocks pop up?"**

**YES! Here's how:**

1. **Use Preloaded Stocks** (Best option)
   - 30 stocks already loaded
   - Filter to get 10+ results
   - No API limits!

2. **Use Real-time Screening**
   - Can scan 10-20 stocks per minute
   - Fast price/volume checks
   - Good for quick results

3. **Use Historical Data** (Slower)
   - Max 6 stocks per minute
   - Full chart data
   - Need to wait or batch requests

**Recommended: Use preloaded stocks + real-time updates = 10+ stocks instantly!**

## 🔧 Code Changes Needed

To optimize for 10 stocks per minute, I can:

1. **Prioritize preloaded stocks** in scan results
2. **Add real-time screening mode** (reqMktData only)
3. **Implement smart batching** (preloaded first, then real-time, then historical)
4. **Add caching** to avoid duplicate requests

Would you like me to implement these optimizations?

# IBKR Scanning Limits & Preset Search Support

## 📊 IBKR API Rate Limits

### Historical Data (`reqHistoricalData`)

**Strict Pacing Restrictions:**
1. **No identical requests within 15 seconds**
   - Cannot request the same symbol/timeframe twice within 15 seconds
   - Solution: Cache results or wait 15+ seconds between identical requests

2. **No 6+ requests for same Contract/Exchange/TickType within 2 seconds**
   - If scanning same stock multiple times, space requests by 2+ seconds
   - Solution: Batch requests with delays

3. **Maximum 60 requests per 10-minute window**
   - Hard limit: 60 historical data requests every 10 minutes
   - **This means: ~6 stocks per minute maximum**
   - Solution: Implement request queuing and rate limiting

4. **Maximum 50 simultaneous open requests**
   - Cannot have more than 50 pending historical data requests
   - Solution: Process requests in batches of 50

5. **BID_ASK requests count as double**
   - If requesting bid/ask data, it counts as 2 requests
   - Solution: Use TRADES data type when possible

### Real-time Market Data (`reqMktData`)

**More Flexible:**
- **At least 100 streaming quotes** per TWS session
- **Fewest limitations** compared to historical data
- Can subscribe to many tickers quickly
- No strict rate limits like historical data

**Best Practice:** Use `reqMktData` for scanning when possible, use `reqHistoricalData` for detailed analysis.

## 🔍 Preset Search Support

### Your Current Preset Criteria

Your scanner supports these preset filters:

1. **Price Range**
   - `minPrice`: Minimum stock price (default: $1.00)
   - `maxPrice`: Maximum stock price (default: $20.00)
   - ✅ **Supported by IBKR** - Can filter after fetching data

2. **Float (Shares Outstanding)**
   - `maxFloat`: Maximum float shares (default: 1B)
   - ⚠️ **Partially Supported** - IBKR doesn't provide float directly
   - Workaround: Use market cap or other metrics

3. **Gain Percentage**
   - `minGainPercent`: Minimum % gain (default: 10%)
   - ✅ **Supported by IBKR** - Calculate from price change

4. **Volume Multiplier**
   - `volumeMultiplier`: Volume vs average (default: 2.0x)
   - ✅ **Supported by IBKR** - Calculate from volume data

### How IBKR Scanning Works

**IBKR doesn't have a built-in scanner API**, so we:

1. **Define a stock list** (your seed symbols + discovery pool)
2. **Fetch data for each stock** using `reqHistoricalData` or `reqMktData`
3. **Apply your preset filters** to the fetched data
4. **Return matching stocks**

### Recommended Scanning Strategy

Given the 60 requests/10 minutes limit:

**Option 1: Slow & Steady (Recommended)**
- Scan 6 stocks per minute
- 10-minute scan cycle = 60 stocks
- Respects all rate limits
- Safe and reliable

**Option 2: Real-time Focus**
- Use `reqMktData` for initial screening (no strict limits)
- Only use `reqHistoricalData` for stocks that pass initial filters
- Faster but requires more complex logic

**Option 3: Batch Processing**
- Pre-fetch data for popular stocks (preload-stocks endpoint)
- Scan from preloaded data (no API calls needed)
- Only fetch new data for discovered stocks
- Most efficient for large scans

## ⚙️ Implementation Recommendations

### 1. Request Queuing System

```python
# Pseudo-code for rate-limited scanning
import time
from collections import deque

request_history = deque(maxlen=60)  # Track last 60 requests
min_interval = 15  # Minimum seconds between identical requests

def can_make_request(symbol, timeframe):
    now = time.time()
    # Check if identical request within 15 seconds
    for req_time, req_symbol, req_tf in request_history:
        if req_symbol == symbol and req_tf == timeframe:
            if now - req_time < min_interval:
                return False, min_interval - (now - req_time)
    
    # Check if we've made 60 requests in last 10 minutes
    recent_requests = [r for r in request_history if now - r[0] < 600]
    if len(recent_requests) >= 60:
        return False, 600 - (now - recent_requests[0][0])
    
    return True, 0
```

### 2. Batch Processing

```python
# Process stocks in batches of 50 (max simultaneous)
def scan_stocks_batch(symbols, criteria):
    results = []
    batch_size = 50
    
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        batch_results = []
        
        # Fetch data for batch
        for symbol in batch:
            data = fetch_from_ibkr(symbol, '5m')
            if data and matches_criteria(data, criteria):
                batch_results.append(data)
        
        results.extend(batch_results)
        
        # Wait 15 seconds before next batch (if not last)
        if i + batch_size < len(symbols):
            time.sleep(15)
    
    return results
```

### 3. Smart Caching

```python
# Cache results to avoid duplicate requests
cache = {}
cache_ttl = 15  # 15 seconds

def get_cached_or_fetch(symbol, timeframe):
    cache_key = f"{symbol}_{timeframe}"
    now = time.time()
    
    if cache_key in cache:
        cached_time, cached_data = cache[cache_key]
        if now - cached_time < cache_ttl:
            return cached_data
    
    # Fetch new data
    data = fetch_from_ibkr(symbol, timeframe)
    cache[cache_key] = (now, data)
    return data
```

## 📈 Optimal Scanning Configuration

### For Your Preset Searches:

**Recommended Settings:**
- **Scan Interval**: 10 minutes (allows 60 requests)
- **Stocks Per Scan**: 50-60 stocks maximum
- **Request Delay**: 1-2 seconds between different stocks
- **Cache Duration**: 15 seconds (prevents duplicate requests)

**Example Scan Flow:**
1. Start with preloaded stocks (no API calls)
2. Scan 50-60 new stocks using `reqMktData` (fast, no limits)
3. For stocks passing initial filters, fetch historical data
4. Apply preset criteria (price, gain, volume)
5. Return matching stocks

## ⚠️ Important Notes

1. **Market Data Subscriptions Required**
   - Real-time data requires market data subscriptions
   - Historical data usually free but may have delays

2. **Connection Stability**
   - Too many rapid requests can cause disconnection
   - Implement exponential backoff on errors

3. **Paper Trading vs Live**
   - Paper trading (port 7497) has same limits as live (7496)
   - Test your scanning strategy in paper trading first

4. **Error Handling**
   - Monitor for pacing violation errors
   - Implement retry logic with delays
   - Log rate limit violations

## ✅ Summary

**Can you do your preset searches?** 
✅ **YES** - But with rate limits:
- Max 60 stocks per 10 minutes
- Need to space requests properly
- Use caching to avoid duplicates
- Consider using preloaded stocks + real-time data

**Best Approach:**
1. Use preloaded stocks for initial screening (no API calls)
2. Use `reqMktData` for real-time price/volume checks (fewer limits)
3. Only use `reqHistoricalData` for detailed analysis of promising stocks
4. Implement request queuing and caching
5. Respect 60 requests/10 minutes limit

Your preset criteria (price, gain, volume) are all supported - just need to fetch data and filter!

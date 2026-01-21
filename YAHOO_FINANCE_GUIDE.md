# Yahoo Finance API - Rate Limits & Best Practices

## 📊 Rate Limits (Unofficial)

Yahoo Finance doesn't officially document their API limits, but community testing shows:

| Limit Type | Value | Notes |
|------------|-------|-------|
| **Requests per hour** | ~2,000 | Hard limit |
| **Requests per minute** | ~33-48 | Recommended max |
| **Requests per day** | ~48,000 | Cumulative |
| **Concurrent requests** | 1-2 | Don't parallelize |

## ⚠️ What Happens When You Exceed Limits

1. **Soft Block** (most common)
   - API returns empty data or errors
   - Temporary IP throttling (15-60 minutes)
   - No permanent ban

2. **Hard Block** (rare)
   - 403 Forbidden errors
   - Can last several hours
   - Requires IP change or long wait

## 🎯 Optimal Fetch Intervals

### Formula
```
Requests/Hour = (Number of Symbols) × (3600 / Interval in Seconds)

Example:
40 symbols × (3600 / 30) = 40 × 120 = 4,800 requests/hour ❌ TOO HIGH
40 symbols × (3600 / 60) = 40 × 60 = 2,400 requests/hour ⚠️ RISKY
40 symbols × (3600 / 90) = 40 × 40 = 1,600 requests/hour ✅ SAFE
```

### Recommended Settings

| Symbols | Min Interval | Requests/Hour | Use Case |
|---------|--------------|---------------|----------|
| 10 | 15s | 2,400 | ⚠️ Active day trading |
| 15 | 30s | 1,800 | ✅ Day trading |
| 20 | 30s | 2,400 | ⚠️ Day trading |
| 30 | 45s | 2,400 | ⚠️ Day trading |
| 40 | 60s | 2,400 | ⚠️ Day trading |
| 40 | 90s | 1,600 | ✅ **Recommended** |
| 50 | 90s | 2,000 | ⚠️ Near limit |
| 100 | 3min | 2,000 | ⚠️ Near limit |
| 100 | 5min | 1,200 | ✅ Safe scanning |

## 🚀 Our Default Configuration

**Current Setup:**
- **40 symbols** (DEFAULT_SYMBOLS in app.py)
- **30-second interval** (configurable in settings)
- **~2,400 requests/hour** (⚠️ near limit but acceptable)

### Why 30 Seconds?

1. ✅ Fast enough for day trading
2. ✅ Won't trigger rate limits immediately
3. ✅ Stocks don't move significantly faster than this
4. ⚠️ Still monitor for throttling

## 🔧 How to Adjust Settings

### Option 1: In the UI (Easiest)

1. Open scanner at `http://localhost:3000`
2. Click "Settings" button
3. Scroll to "Auto Features"
4. Adjust "Update interval (seconds)"
   - **15s** = Very fast (risky with 40+ symbols)
   - **30s** = Fast (current default)
   - **60s** = Moderate (safest for 40+ symbols)
   - **90-120s** = Conservative (very safe)

### Option 2: Reduce Symbol Count

Edit `backend/app.py`:

```python
# Current: 40 symbols
DEFAULT_SYMBOLS = [
    'AAPL', 'TSLA', 'AMD', # ... 40 total
]

# Reduce to top 15 movers for 15s intervals:
DEFAULT_SYMBOLS = [
    'GME', 'AMC', 'TSLA', 'AMD', 'NVDA',
    'PLTR', 'SOFI', 'NIO', 'LCID', 'RIVN',
    'ATER', 'BBIG', 'WKHS', 'PROG', 'BBBY'
]
```

With 15 symbols @ 15s = 3,600 requests/hour (⚠️ still high but manageable)

### Option 3: Batch Processing (Advanced)

Modify `backend/app.py` to scan symbols in batches:

```python
import time

def filter_stocks(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    batch_size = 10
    
    for i in range(0, len(self.symbols), batch_size):
        batch = self.symbols[i:i + batch_size]
        
        for symbol in batch:
            stock_data = self.get_stock_data(symbol, timeframe)
            if stock_data and meets_criteria:
                results.append(stock_data)
        
        # Small delay between batches
        if i + batch_size < len(self.symbols):
            time.sleep(1)
    
    return results
```

## 📈 Best Practices by Trading Style

### Day Trader (Active)
```
Symbols: 15-20
Interval: 30-60s
Hours Active: 6.5 (market hours)
Daily Requests: ~7,800-15,600
Risk: ⚠️ Moderate
```

### Swing Trader
```
Symbols: 30-50
Interval: 2-5min
Hours Active: 6.5
Daily Requests: ~3,900-9,750
Risk: ✅ Low
```

### Scanner/Screener
```
Symbols: 50-100
Interval: 5-15min
Hours Active: 6.5
Daily Requests: ~2,600-7,800
Risk: ✅ Very Low
```

### Long-Term Monitoring
```
Symbols: 100+
Interval: 30-60min
Hours Active: 24
Daily Requests: ~2,400-4,800
Risk: ✅ Minimal
```

## 🛡️ Signs You're Being Rate Limited

Watch for these in your terminal/browser console:

1. **Empty data** - API returns no stock info
2. **Errors** - "Failed to fetch" or HTTP 429
3. **Slow responses** - Requests take >10 seconds
4. **Missing candles** - Chart data incomplete
5. **Console warnings** - "Error fetching data for X"

## 🔍 Monitoring Your Usage

Add this to `backend/app.py` to track requests:

```python
from datetime import datetime
from collections import deque

class RateLimitMonitor:
    def __init__(self):
        self.requests = deque(maxlen=100)
    
    def log_request(self):
        self.requests.append(datetime.now())
    
    def get_rate(self):
        if len(self.requests) < 2:
            return 0
        time_span = (self.requests[-1] - self.requests[0]).total_seconds()
        return len(self.requests) / time_span * 3600 if time_span > 0 else 0

monitor = RateLimitMonitor()

# In get_stock_data():
monitor.log_request()
rate = monitor.get_rate()
if rate > 2000:
    logging.warning(f"High request rate: {rate:.0f} req/hour")
```

## 💡 Alternative Data Sources

If you need faster updates or more symbols:

### Free Alternatives
1. **Alpha Vantage**
   - 5 calls/minute (free tier)
   - 500 calls/day
   - Better documentation

2. **Finnhub**
   - 60 calls/minute (free)
   - WebSocket support
   - Real-time quotes

3. **IEX Cloud**
   - 50,000 messages/month (free)
   - High-quality data
   - Pay-as-you-go

### Paid Solutions (Worth It for Serious Trading)
1. **Polygon.io** - $29-199/month
2. **Alpaca Markets** - Free with trading account
3. **TradingView** - $12-60/month
4. **TD Ameritrade API** - Free with account

## 🎯 Recommended Setup for This Scanner

**Conservative (Safest):**
```
Symbols: 40
Interval: 90 seconds
Requests/Hour: 1,600
Good for: Swing trading, learning
```

**Balanced (Current Default):**
```
Symbols: 40
Interval: 30 seconds
Requests/Hour: 2,400
Good for: Active day trading
```

**Aggressive (Riskiest):**
```
Symbols: 15
Interval: 15 seconds
Requests/Hour: 3,600
Good for: Scalping, very active trading
```

## ⚡ Pro Tips

1. **Market Hours Only** - Only run during 9:30am-4pm ET to save requests
2. **Pre-Filter** - Scan fewer symbols more frequently
3. **Cache Data** - Store recent data locally, refresh less often
4. **Tiered Scanning** - Fast updates for hot stocks, slow for others
5. **Manual Refresh** - Disable auto-updates, refresh when needed

## 🚨 Emergency: You Got Rate Limited

If you're blocked:

1. **Stop the scanner immediately**
   ```bash
   Ctrl+C (in both terminal windows)
   ```

2. **Wait 30-60 minutes**

3. **Reduce request rate:**
   - Increase interval to 60-120s
   - Reduce symbols to 20 or less

4. **Restart gradually:**
   - Start with 2-minute intervals
   - Monitor for errors
   - Gradually decrease if stable

5. **Consider alternatives:**
   - Use a different API
   - Run from different IP (mobile hotspot)
   - Switch to paid service

## 📞 Support

If you continue having issues:
- Check Yahoo Finance status
- Try different symbols (some may be delisted)
- Verify internet connection
- Consider API alternatives

---

**Remember:** Yahoo Finance is FREE but has limits. Respect them and your scanner will run smoothly! 📊

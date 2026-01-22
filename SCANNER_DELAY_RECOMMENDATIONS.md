# Scanner Delay/Interval Recommendations

## 🎯 Quick Answer

**Recommended Scanner Delay: 10-15 seconds**

This balances speed with reliability and respects IBKR rate limits.

## 📊 Current Setup

You're using **Option 2: Real-time Screening** (default)
- Real-time screening: ~0.5 seconds per stock
- Can handle: 10-20 stocks per minute
- Also fetches historical data for promising stocks (60 requests/10min limit)

## ⏱️ Recommended Intervals

### Option 1: Fast Scanning (10 seconds)
**Best for:** Active trading, quick updates
- **Interval**: 10 seconds
- **Scans per minute**: 6
- **Stocks per scan**: 10-20 (real-time)
- **Total stocks/minute**: 60-120 (real-time only)
- **Historical data**: Only for stocks that pass filters
- **Risk**: Medium (approaching rate limits if many stocks pass filters)

### Option 2: Balanced (15 seconds) ⭐ **RECOMMENDED**
**Best for:** Most users, reliable operation
- **Interval**: 15 seconds
- **Scans per minute**: 4
- **Stocks per scan**: 10-20 (real-time)
- **Total stocks/minute**: 40-80 (real-time only)
- **Historical data**: Only for stocks that pass filters
- **Risk**: Low (safe buffer for rate limits)

### Option 3: Conservative (20 seconds)
**Best for:** Long-term monitoring, avoiding rate limits
- **Interval**: 20 seconds
- **Scans per minute**: 3
- **Stocks per scan**: 10-20 (real-time)
- **Total stocks/minute**: 30-60 (real-time only)
- **Historical data**: Only for stocks that pass filters
- **Risk**: Very Low (plenty of buffer)

### Option 4: Very Fast (5 seconds) ⚠️
**Best for:** Testing, small stock lists
- **Interval**: 5 seconds
- **Scans per minute**: 12
- **Stocks per scan**: 10-20 (real-time)
- **Total stocks/minute**: 120-240 (real-time only)
- **Historical data**: Only for stocks that pass filters
- **Risk**: High (may hit rate limits if many stocks pass filters)

## 🔍 How to Calculate

### Real-time Screening (Primary)
- **Speed**: ~0.5 seconds per stock
- **10 stocks**: ~5 seconds
- **20 stocks**: ~10 seconds
- **No strict rate limits** for `reqMktData`

### Historical Data (Secondary - Only for promising stocks)
- **Limit**: 60 requests per 10 minutes
- **That's**: 6 requests per minute
- **Used when**: Stock passes price + gain filters

### Total Time Per Scan
```
Real-time screening: 10 stocks × 0.5s = 5 seconds
If 2 stocks pass filters → Fetch historical: 2 × 2s = 4 seconds
Total: ~9 seconds per scan
```

## 📈 Recommended Settings by Use Case

### Day Trading (Active)
- **Interval**: 10 seconds
- **Reason**: Fast updates, catch moves quickly
- **Watch**: Monitor for rate limit warnings

### Swing Trading (Moderate)
- **Interval**: 15 seconds ⭐
- **Reason**: Balanced speed and reliability
- **Best overall choice**

### Position Trading (Long-term)
- **Interval**: 20-30 seconds
- **Reason**: Less frequent updates needed
- **Very safe for rate limits**

### Testing/Development
- **Interval**: 5 seconds
- **Reason**: Quick iteration
- **Note**: May hit limits with many stocks

## ⚙️ Current Configuration

### Backend
- **Recommended Interval**: 3 seconds (very aggressive)
- **Mode**: Real-time screening
- **Speed**: 10-20 stocks per minute

### Frontend
- **Auto-refresh**: 20 seconds (conservative)
- **Manual refresh**: Available anytime

## 🎯 My Recommendation

**Set scanner delay to: 15 seconds**

**Why:**
1. ✅ Fast enough for real-time updates
2. ✅ Safe buffer for rate limits
3. ✅ Allows 4 scans per minute
4. ✅ Can handle 10-20 stocks per scan
5. ✅ Historical data only fetched when needed

**Calculation:**
- 15 seconds = 4 scans per minute
- 4 scans × 10 stocks = 40 stocks/minute (real-time)
- Historical data: Only for ~2-5 stocks that pass filters
- Total historical requests: ~8-20 per minute (well under 60/10min limit)

## ⚠️ Important Notes

1. **Real-time screening is fast** - No strict limits
2. **Historical data has limits** - 60 requests per 10 minutes
3. **Smart system** - Only fetches historical for promising stocks
4. **Monitor logs** - Watch for rate limit warnings
5. **Adjust as needed** - Start conservative, increase if stable

## 🔧 How to Change

### In Frontend (Auto-refresh)
Currently set in `App.tsx`:
```typescript
// Change this value (in milliseconds)
setInterval(() => {
  performScan()
}, 15000) // 15 seconds = 15000ms
```

### In Backend (Recommended interval)
Currently set in `app.py`:
```python
'recommendedInterval': 3,  # Change to 15 for balanced
```

## 📊 Summary Table

| Interval | Scans/Min | Stocks/Min (Real-time) | Historical Risk | Best For |
|----------|-----------|------------------------|-----------------|----------|
| 5s       | 12        | 120-240                | High            | Testing  |
| 10s      | 6         | 60-120                 | Medium          | Day Trading |
| **15s**  | **4**     | **40-80**              | **Low**         | **Most Users** ⭐ |
| 20s      | 3         | 30-60                  | Very Low        | Position Trading |
| 30s      | 2         | 20-40                  | Very Low        | Long-term |

## ✅ Final Recommendation

**Set your scanner delay to 15 seconds**

This gives you:
- Fast enough updates (4 scans per minute)
- Safe from rate limits
- Can handle 10-20 stocks per scan
- Historical data only when needed
- Reliable operation

You can always adjust based on your needs!

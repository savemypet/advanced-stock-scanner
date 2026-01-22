# Yahoo Finance Float Data - Availability

## ✅ Yes, Yahoo Finance Has Float Data!

Yahoo Finance (via `yfinance` library) **does provide float data**, but with important caveats.

## 📊 How Yahoo Finance Provides Float Data

### Available Fields:
1. **`floatShares`** - Free float (shares available for trading)
2. **`sharesOutstanding`** - Total shares outstanding (includes restricted shares)

### Current Implementation:
```python
# In _fetch_from_yahoo method
info = ticker.info
float_shares = info.get('floatShares', info.get('sharesOutstanding', 1_000_000_000))
```

**Priority:**
1. First tries: `floatShares` (preferred - actual float)
2. Falls back to: `sharesOutstanding` (if floatShares not available)
3. Default: 1,000,000,000 (1B shares) if neither available

## ⚠️ Important Limitations

### 1. **IBKR-Only Mode**
- **Current Status**: You're using IBKR-only mode
- **Yahoo Finance**: Only used as fallback when IBKR is unavailable
- **Result**: Float filter won't work when IBKR is primary (which is most of the time)

### 2. **Data Availability**
- Not all stocks have float data available
- Some stocks may return `None` or missing values
- Data quality varies by stock

### 3. **Fallback Only**
- Yahoo Finance is only called when IBKR fails
- If IBKR is working, you'll never get Yahoo float data
- Float filter still won't work in normal operation

## 🔍 What This Means for Your Scanner

### Current Situation:
- **IBKR (Primary)**: ❌ No float data (always returns 0)
- **Yahoo (Fallback)**: ✅ Has float data (but rarely used)

### Float Filter Status:
- **Won't work** when IBKR is primary (normal operation)
- **Might work** when IBKR fails and Yahoo is used (rare)
- **Not reliable** for consistent filtering

## 💡 Options

### Option 1: Keep IBKR-Only (Current)
- ✅ Fast, reliable, no rate limits
- ❌ No float data
- **Recommendation**: Don't use float filter

### Option 2: Hybrid Approach (Not Recommended)
- Use Yahoo Finance for float data only
- Keep IBKR for price/volume data
- **Problem**: Adds complexity, rate limits, slower

### Option 3: Use Alternative Metrics
Instead of float, use:
- **Price range** (already working)
- **Volume multiplier** (already working)
- **Market cap** (if available)
- **Price × Volume** (liquidity indicator)

## 📋 Summary

**Question**: Does Yahoo Finance have float data?
**Answer**: ✅ **YES** - Yahoo Finance provides `floatShares` and `sharesOutstanding`

**But:**
- ❌ You're using IBKR-only mode (Yahoo is fallback only)
- ❌ Float filter won't work with IBKR (primary source)
- ⚠️ Float filter only works when IBKR fails (rare)

**Recommendation:**
- Don't rely on float filter
- Use price, volume, and gain filters instead
- Float filter status in settings correctly shows "Won't work"

## 🔧 Technical Details

### Yahoo Finance Float Data Access:
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
info = ticker.info

# Get float shares
float_shares = info.get('floatShares')  # Preferred
shares_outstanding = info.get('sharesOutstanding')  # Fallback

# Both may be None for some stocks
```

### Current Code Location:
- **File**: `backend/app.py`
- **Method**: `_fetch_from_yahoo()` (line ~1307)
- **Line**: ~1385 - Gets float from `info.get('floatShares', info.get('sharesOutstanding', 1_000_000_000))`

## ✅ Conclusion

**Yahoo Finance has float data, but:**
- It's only available as a fallback
- IBKR (your primary source) doesn't have it
- Float filter won't work in normal operation
- **The settings panel correctly shows "Won't work"** ✅

Your current setup is correct - float filter is marked as "won't work" because IBKR doesn't provide it, even though Yahoo Finance (fallback) does.

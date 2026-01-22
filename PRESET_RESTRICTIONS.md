# Preset Restrictions - What You Can't Use

## ⚠️ Presets That Cause Problems with IBKR

### 1. **Float Filter (maxFloat) - LIMITED SUPPORT** ❌
**Problem:** IBKR doesn't provide float (shares outstanding) directly

**What Happens:**
- Float is always set to `0` in IBKR data
- Float check always passes (0 <= maxFloat)
- Filter doesn't actually work

**Recommendation:**
- ❌ **Don't rely on float filter** - It won't filter anything
- ✅ Use price range and volume instead
- ✅ Use market cap if available (not provided by IBKR either)

**Workaround:**
- Remove float from your filter criteria
- Use other filters (price, gain, volume) instead

---

### 2. **Very Loose Filters - RATE LIMIT RISK** ⚠️
**Problem:** Too many stocks pass filters → Too many historical requests → Rate limit exceeded

**What Happens:**
- Many stocks match criteria
- Each matching stock needs historical data
- Exceeds 60 requests per 10 minutes
- Scanner delay auto-increases

**Problematic Settings:**
- ❌ **minGainPercent: 0-2%** (too low, many stocks pass)
- ❌ **minPrice: $0.01, maxPrice: $1000** (too wide range)
- ❌ **volumeMultiplier: 1.0x** (too low, many stocks pass)
- ❌ **displayCount: 50+** (too many stocks to process)

**Recommendation:**
- ✅ **minGainPercent: 5-10%+** (stricter, fewer stocks)
- ✅ **Price range: $1-$20** (reasonable range)
- ✅ **volumeMultiplier: 2.0x-5.0x** (stricter volume requirement)
- ✅ **displayCount: 5-10** (manageable number)

---

### 3. **Very High Display Count - PERFORMANCE ISSUE** ⚠️
**Problem:** Requesting too many stocks causes performance issues

**What Happens:**
- Scanner tries to process 50+ stocks
- Each stock needs real-time + historical data
- Takes too long, may timeout
- Rate limits hit faster

**Problematic Settings:**
- ❌ **displayCount: 50+** (too many)
- ❌ **displayCount: 100+** (way too many)

**Recommendation:**
- ✅ **displayCount: 5-10** (optimal)
- ✅ **displayCount: 10-20** (maximum recommended)

---

### 4. **Very Short Timeframes - DATA AVAILABILITY** ⚠️
**Problem:** Some very short timeframes may not have enough data

**What Happens:**
- Requesting 1m data may return limited bars
- IBKR may not have complete 1m history
- Charts may look incomplete

**Problematic Settings:**
- ⚠️ **chartTimeframe: '1m'** (may have limited data)
- ⚠️ **chartTimeframe: '2m'** (may have limited data)

**Recommendation:**
- ✅ **chartTimeframe: '5m'** (best balance)
- ✅ **chartTimeframe: '15m'** (reliable)
- ✅ **chartTimeframe: '1h'** (very reliable)

---

### 5. **Negative Gain Filter - LOGIC ISSUE** ❌
**Problem:** Setting negative minGainPercent doesn't make sense for "gainers"

**What Happens:**
- Setting minGainPercent: -10% means you're looking for losers
- Scanner will find stocks that are DOWN 10%
- Not useful for finding movers

**Problematic Settings:**
- ❌ **minGainPercent: -10%** (looking for losers, not gainers)
- ❌ **minGainPercent: -5%** (too broad)

**Recommendation:**
- ✅ **minGainPercent: 0%+** (at least flat or up)
- ✅ **minGainPercent: 5%+** (actual gainers)
- ✅ **minGainPercent: 10%+** (strong movers)

---

## ✅ Safe Preset Combinations

### Recommended: Low-Float Explosive Movers
```
minPrice: $1.00
maxPrice: $20.00
maxFloat: 10,000,000 (ignored - IBKR doesn't provide)
minGainPercent: 10%
volumeMultiplier: 5.0x
displayCount: 10
chartTimeframe: '5m'
```
**Status:** ✅ Safe (float filter ignored, but other filters work)

### Recommended: Penny Stock Movers
```
minPrice: $0.05
maxPrice: $1.00
maxFloat: 100,000,000 (ignored)
minGainPercent: 10%
volumeMultiplier: 5.0x
displayCount: 10
chartTimeframe: '5m'
```
**Status:** ✅ Safe (float filter ignored, but other filters work)

### Recommended: Balanced Scanner
```
minPrice: $1.00
maxPrice: $20.00
maxFloat: 1,000,000,000 (ignored)
minGainPercent: 5%
volumeMultiplier: 2.0x
displayCount: 5
chartTimeframe: '5m'
```
**Status:** ✅ Safe (balanced, won't hit rate limits)

---

## ❌ Presets You CAN'T Use

### 1. Float-Based Filtering
- **Can't use:** Any preset that relies on float filtering
- **Why:** IBKR doesn't provide float data
- **Workaround:** Use price, volume, and gain instead

### 2. Very Loose Filters (Rate Limit Risk)
- **Can't use:** minGainPercent < 3%, very wide price ranges, volumeMultiplier < 1.5x
- **Why:** Too many stocks pass → Too many API requests → Rate limit
- **Workaround:** Use stricter filters

### 3. Very High Display Count
- **Can't use:** displayCount > 20
- **Why:** Performance issues, rate limits
- **Workaround:** Keep displayCount at 5-10

### 4. Negative Gain Filters
- **Can't use:** minGainPercent < 0%
- **Why:** Logic doesn't make sense for finding gainers
- **Workaround:** Use 0% or higher

---

## 📊 Summary

### ✅ Safe to Use:
- Price range filters (minPrice, maxPrice)
- Gain percentage filters (minGainPercent: 5%+)
- Volume multiplier filters (volumeMultiplier: 2.0x+)
- Display count: 5-10
- Timeframes: 5m, 15m, 1h, 24h

### ❌ Can't Use:
- Float filtering (IBKR doesn't provide)
- Very loose filters (rate limit risk)
- Very high display count (performance)
- Negative gain filters (logic issue)

### ⚠️ Use with Caution:
- Very short timeframes (1m, 2m) - may have limited data
- Loose filters (minGainPercent: 0-3%) - may hit rate limits
- Display count: 15-20 - monitor for performance

---

## 🔧 Auto-Adjustment Feature

The scanner now **automatically increases delay by 1 second** when errors occur:
- Detects rate limit/pacing violations
- Increases delay from 12s → 13s → 14s, etc.
- Maximum delay: 60 seconds
- Helps prevent rate limit issues

**This means:** Even if you use problematic presets, the system will auto-adjust to prevent errors!

# Stock Search and Scanner Flow Analysis

## 🔍 Stock Search Flow (Search Bar)

### Frontend Flow:
1. **User enters symbol** in search bar → `handleSearchStock()` in `App.tsx`
2. **Calls API**: `getStock(symbol, timeframe)` from `stockApi.ts`
3. **API Request**: `GET /api/stock/{symbol}?timeframe=5m`
4. **Timeout**: 60 seconds (for IBKR data fetching)

### Backend Flow (`/api/stock/<symbol>`):
1. **Endpoint**: `get_stock()` function in `app.py` (line ~2186)
2. **Checks IBKR connection**: `IBKR_AVAILABLE` and `IBKR_CONNECTED`
3. **Fetches data**: Calls `fetch_from_ibkr(symbol, timeframe)`
4. **Returns**: Full stock data with candles, chart data, etc.

### IBKR Data Fetching (`fetch_from_ibkr()`):
1. **Function**: `fetch_from_ibkr(symbol, timeframe='5m')` (line ~1079)
2. **Creates contract**: `Stock(symbol, 'SMART', 'USD')`
3. **Requests historical data**: `reqHistoricalData()` with timeframe mapping
4. **Gets real-time ticker**: `reqMktData()` for current price
5. **Builds candles**: Converts IBKR bars to candle format
6. **Returns**: Complete stock object with price, change, candles, chartData

### Issues Found:
- ✅ Timeout is 60 seconds (good for IBKR)
- ✅ Error handling is present
- ⚠️ Can timeout if IBKR is slow (30-60s is normal)

---

## 📊 Scanner Flow (Main Scanner)

### Frontend Flow:
1. **User clicks Start/Refresh** → `performScan()` in `App.tsx` (line ~61)
2. **Calls API**: `scanStocks(settings)` from `stockApi.ts`
3. **API Request**: `POST /api/scan` with scanner criteria
4. **Timeout**: **30 seconds** → **FIXED to 120 seconds** (2 minutes)

### Backend Flow (`/api/scan`):
1. **Endpoint**: `scan_stocks()` function in `app.py` (line ~1956)
2. **Extracts criteria**: minPrice, maxPrice, maxFloat, minGainPercent, volumeMultiplier, displayCount
3. **Calls scanner**: `scanner.filter_stocks(criteria)`
4. **Returns**: Array of qualifying stocks

### Scanner Filter Flow (`filter_stocks()`):
1. **Function**: `filter_stocks()` in `StockScanner` class (line ~1731)
2. **Gets scan symbols**: From `active_symbols` set (starts with seed symbols)
3. **Limits to 5 stocks**: To prevent timeouts (recently added)
4. **For each symbol**:
   - **Step 1**: Try `fetch_realtime_ibkr(symbol)` - Fast real-time screening
   - **Step 2**: If fails, fallback to `get_stock_data(symbol, timeframe)` - Full historical data
   - **Step 3**: Apply filters (price, float, gain, volume)
   - **Step 4**: If qualifies, add to results

### Real-Time Screening (`fetch_realtime_ibkr()`):
1. **Function**: `fetch_realtime_ibkr(symbol)` (line ~931)
2. **Uses 5-minute bars**: `reqHistoricalData()` with `barSizeSetting='5 mins'`
3. **Gets latest bar**: Most recent 5-minute bar for current price
4. **Calculates change**: From previous close
5. **Returns**: Quick stock data (price, change, volume)

### Full Data Fetch (`get_stock_data()`):
1. **Function**: `get_stock_data(symbol, timeframe)` in `StockScanner` class
2. **Calls**: `fetch_from_ibkr(symbol, timeframe)` - Full historical data
3. **Gets**: Complete candles, chart data, 24h data
4. **Returns**: Full stock object

### Filter Checks:
1. **Price check**: `min_price <= currentPrice <= max_price`
2. **Float check**: `float <= max_float` (only if float data available)
3. **Gain check**: `changePercent >= min_gain`
4. **Volume check**: `currentVolume >= avgVolume * volumeMultiplier`

### Issues Found:
- ✅ **FIXED**: Frontend timeout increased to 120 seconds
- ✅ Scanner limited to 5 stocks (prevents timeouts)
- ✅ Uses 5-minute bars (Snapshot Bundle compatible)
- ⚠️ Each stock takes 3-5 seconds (5 stocks = 15-25 seconds total)
- ⚠️ If real-time fails, falls back to full data (adds more time)

---

## 🔄 Complete Flow Diagram

### Stock Search:
```
User Input → handleSearchStock()
    ↓
getStock(symbol, timeframe)
    ↓
GET /api/stock/{symbol}
    ↓
get_stock() → Checks IBKR connection
    ↓
fetch_from_ibkr(symbol, timeframe)
    ↓
reqHistoricalData() + reqMktData()
    ↓
Returns: Full stock data with candles
    ↓
Frontend: Opens StockDetailModal
```

### Scanner:
```
User Clicks Start → performScan()
    ↓
scanStocks(settings)
    ↓
POST /api/scan
    ↓
scan_stocks() → Extracts criteria
    ↓
scanner.filter_stocks(criteria)
    ↓
For each symbol (max 5):
    ├─ Try: fetch_realtime_ibkr() [Fast - 5-min bars]
    │   └─ If fails → get_stock_data() [Full data]
    ├─ Apply filters (price, float, gain, volume)
    └─ If qualifies → Add to results
    ↓
Returns: Array of qualifying stocks
    ↓
Frontend: Updates stock list, shows patterns
```

---

## ⚠️ Potential Issues & Improvements

### Issue 1: Timeout Too Short (FIXED)
- **Was**: 30 seconds
- **Now**: 120 seconds (2 minutes)
- **Why**: Scanner processes 5 stocks × 3-5s each = 15-25s minimum

### Issue 2: Real-Time Screening May Fail
- **Problem**: `fetch_realtime_ibkr()` uses 5-minute bars, may timeout
- **Fallback**: Uses full `get_stock_data()` which is slower
- **Solution**: Already has fallback, but could optimize

### Issue 3: Scanner Limited to 5 Stocks
- **Current**: Only scans first 5 symbols from `active_symbols`
- **Why**: Prevents timeouts
- **Trade-off**: Faster but scans fewer stocks

### Issue 4: IBKR Connection Check
- **Problem**: Health check shows `IBKR_CONNECTED` as empty/false
- **Need**: Verify TWS/IB Gateway is running and connected
- **Check**: `http://localhost:5000/api/health`

### Issue 5: Snapshot Bundle Compatibility
- **Current**: Uses 5-minute historical bars (works with Snapshot Bundle)
- **Good**: Avoids Error 10089 for streaming quotes
- **Note**: May be slower than streaming but more reliable

---

## ✅ Recommendations

1. **Keep timeout at 120 seconds** - Scanner needs time
2. **Monitor IBKR connection** - Ensure TWS/IB Gateway is running
3. **Consider increasing stock limit** - If scanner gets faster, can scan more
4. **Add progress indicator** - Show "Processing stock X of 5" in UI
5. **Cache results** - Don't re-scan same stocks immediately
6. **Parallel processing** - Could process multiple stocks simultaneously (advanced)

---

## 🔍 Debugging Tips

### Check if scanner is working:
```bash
# Test scanner API directly
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"minPrice":0.01,"maxPrice":1000,"maxFloat":100000000000,"minGainPercent":-50,"volumeMultiplier":0.1,"displayCount":5}'
```

### Check if search is working:
```bash
# Test search API directly
curl http://localhost:5000/api/stock/AAPL?timeframe=5m
```

### Check backend logs:
- File: `backend/backend-startup.log`
- Look for: `[SCANNER]`, `[SEARCH API]`, `[IBKR REALTIME]`
- Check for: Errors, timeouts, completion messages

### Check frontend console:
- Open browser DevTools (F12)
- Look for: `[SCANNER]`, `[SCANNER API]`, `[SEARCH]` logs
- Check for: Timeout errors, API errors

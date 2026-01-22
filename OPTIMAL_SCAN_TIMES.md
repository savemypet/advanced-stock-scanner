# Optimal Scan Times Analysis

## 📊 Scan Time Analysis

### Current Performance:
- **Average Scan Time**: ~35 seconds (for 5 stocks)
- **Per Stock Time**: ~3-5 seconds each
- **Total Processing**: 5 stocks × 3-5s = 15-25 seconds + overhead

### Recommended Scan Intervals:

#### **Option 1: Conservative (Recommended)**
- **Interval**: **60 seconds**
- **Reason**: 2x average scan time (35s × 2 = 70s, rounded to 60s)
- **Best for**: Stable operation, prevents overlapping scans
- **Current Setting**: ✅ **ACTIVE**

#### **Option 2: Aggressive**
- **Interval**: **45 seconds**
- **Reason**: 1.5x average scan time
- **Best for**: Faster updates, but may cause occasional overlaps
- **Risk**: If scan takes >45s, next scan starts before previous finishes

#### **Option 3: Very Conservative**
- **Interval**: **90 seconds**
- **Reason**: 2.5x average scan time
- **Best for**: Maximum stability, no overlap risk
- **Trade-off**: Slower updates

## ⚡ Factors Affecting Scan Time

### What Makes Scans Faster:
- ✅ **5 stocks max** (current limit)
- ✅ **5-minute bars** (Snapshot Bundle compatible)
- ✅ **Real-time screening first** (fast path)
- ✅ **IBKR connected** (no connection delays)

### What Makes Scans Slower:
- ⚠️ **More stocks** (currently limited to 5)
- ⚠️ **Full historical data fallback** (if real-time fails)
- ⚠️ **IBKR slow responses** (network latency)
- ⚠️ **24h data fetching** (for AI study)

## 📈 Current Settings

### Frontend:
- **Default Interval**: 60 seconds
- **Timeout**: 120 seconds (2 minutes)
- **Auto-refresh**: Enabled by default

### Backend:
- **Stock Limit**: 5 stocks per scan
- **Real-time Method**: 5-minute historical bars
- **Fallback**: Full historical data if real-time fails

## 🎯 Best Practices

### For Optimal Performance:
1. **Keep stock limit at 5** - Prevents timeouts
2. **Use 60-second interval** - Balanced speed/stability
3. **Monitor Connection Log** - Watch for IBKR issues
4. **Check backend logs** - Verify scan completion times

### If Scans Are Too Slow:
- Reduce `displayCount` to 3 stocks
- Increase interval to 90 seconds
- Check IBKR connection status

### If Scans Are Too Fast:
- Can reduce interval to 45 seconds
- Monitor for overlapping scans
- Watch for timeout errors

## 📝 Scan Time History

Based on recent scans:
- **Scan 1**: 34.9 seconds
- **Average**: 34.9 seconds
- **Recommended**: 60 seconds (2x average)

## 🔄 How Scanner Feeds Both Sections

### Flow:
1. **User clicks Start** → `performScan()` runs
2. **Scanner finds stocks** → Returns array of stocks
3. **Stocks set in state** → `setStocks(stocksWithPatterns)`
4. **Live Scanner** → Gets stocks directly from `stocks` state
5. **Simulated Scanner** → Gets stocks via `liveStocks={stocks}` prop
6. **Both sections update** → Same stocks appear in both!

### Code:
```typescript
// App.tsx
setStocks(stocksWithPatterns)  // Sets stocks state

// Live Scanner
<StockScanner stocks={stocks} />  // Direct access

// Simulated Scanner  
<SimulatedScanner liveStocks={stocks} />  // Via prop
```

## ✅ Verification

To verify everything works:
1. Click "Start" button
2. Wait 30-60 seconds for scan to complete
3. Check **Live Scanner** tab - should show stocks
4. Switch to **Simulated Demo** tab - should show same stocks
5. Check **Connection Log** - should show scan activity

## 📊 Monitoring

### Check Backend Logs:
- File: `backend/backend-startup.log`
- Look for: `[SCANNER] Total time: X.XXs`
- Monitor: Average should be ~30-40 seconds

### Check Frontend Console:
- Open DevTools (F12)
- Look for: `[SCANNER] Scan complete`
- Monitor: Should complete within 60 seconds

### Check Connection Log:
- Click "Log" button in app
- Watch for: IBKR connection status
- Monitor: Scanner/search activity

# Stock Scanner - Quick Reference Card

## 🚀 Start/Stop Commands

**Start Scanner:**
```bash
cd advanced-stock-scanner
start-scanner.bat
```

**Stop Scanner:**
- Press `Ctrl+C` in terminal windows

**Access UI:**
- http://localhost:3000

## ⚙️ Optimal Yahoo Finance Settings

### Safe Configuration (Recommended)
- **Update Interval:** 30-60 seconds
- **Symbols:** 40 (default)
- **Requests/Hour:** 1,600-2,400
- ✅ Won't hit rate limits

### Aggressive Configuration (Risky)
- **Update Interval:** 15-30 seconds
- **Symbols:** 15-20
- **Requests/Hour:** 2,400-3,600
- ⚠️ May hit rate limits

### Conservative Configuration (Safest)
- **Update Interval:** 90-120 seconds
- **Symbols:** 40+
- **Requests/Hour:** 1,200-1,600
- ✅ Very safe, slower updates

## 📊 How to Change Settings

### In the UI (Easy):
1. Click **Settings** button (top right)
2. Scroll to **Auto Features**
3. Adjust **Update interval (seconds)**
   - Min: 5s (very risky)
   - Recommended: 30-60s
   - Max: 300s (5 minutes)

### In Code (Advanced):

**Change symbols** (`backend/app.py` line 21):
```python
DEFAULT_SYMBOLS = ['AAPL', 'TSLA', 'AMD', ...]
```

**Change default interval** (`frontend/src/App.tsx` line 27):
```typescript
updateInterval: 30, // seconds
```

## 🎯 Recommended by Use Case

| Use Case | Symbols | Interval | Risk |
|----------|---------|----------|------|
| **Scalping** | 10-15 | 15-20s | ⚠️ High |
| **Day Trading** | 20-30 | 30-45s | ⚠️ Medium |
| **Swing Trading** | 40-50 | 60-90s | ✅ Low |
| **Monitoring** | 50+ | 2-5min | ✅ Very Low |

## ⚡ Quick Troubleshooting

**Problem: No stocks showing**
- Wait 30-60 seconds for first scan
- Check filters aren't too strict
- Verify backend is running (port 5000)

**Problem: Empty data / errors**
- You hit rate limit! 
- Stop scanner, wait 30 minutes
- Increase interval to 60-90s
- Reduce symbol count

**Problem: Slow updates**
- Normal for first scan
- Check internet connection
- Reduce symbol count
- Increase interval

## 📁 Important Files

```
advanced-stock-scanner/
├── backend/app.py          # Edit symbols here
├── frontend/src/App.tsx    # Main app logic
├── README.md               # Full documentation
├── YAHOO_FINANCE_GUIDE.md  # Rate limit details
└── start-scanner.bat       # Start script
```

## 🔥 Current Settings (Default)

- ✅ **Update Interval:** 30 seconds
- ✅ **Max Float:** 10 million shares ⚡ **LOW-FLOAT TARGETING**
- ✅ **Min Gain:** 10%
- ✅ **Volume:** 4x average 🔥 **EXPLOSIVE VOLUME**
- ✅ **Price Range:** $1-$20
- ✅ **Symbols:** 40 stocks
- ✅ **Requests/Hour:** ~2,400
- ✅ **Real-time updates:** Enabled
- ✅ **Notifications:** Enabled
- ✅ **Auto-add stocks:** Enabled

## 📞 Need Help?

1. Read `YAHOO_FINANCE_GUIDE.md` for detailed rate limit info
2. Read `README.md` for full documentation
3. Check backend terminal for error messages
4. Check browser console (F12) for frontend errors

## 💡 Pro Tips

1. **Market Hours Only** - Run 9:30am-4pm ET only
2. **Start Conservative** - Begin with 60s interval
3. **Monitor Console** - Watch for "rate limit" errors
4. **Adjust Gradually** - Decrease interval slowly
5. **Quality > Speed** - 30s updates are plenty fast
6. **Low Float = High Risk** - 10M float finds EXPLOSIVE stocks (volatile!)
7. **Use Stop Losses** - These stocks can move fast both ways
8. **Scale Out** - Take profits on the way up

---

**Remember:** Yahoo Finance is free but has limits. The 30-second default is the sweet spot! 📈

⚠️ **WARNING:** 10M float targets super low-float stocks - extreme volatility expected! See `LOW_FLOAT_STRATEGY.md` for trading guide.

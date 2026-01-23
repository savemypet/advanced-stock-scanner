# Stock Scanner - AI Quick Reference

## 🚀 Quick Start Commands

```powershell
# Start Backend
cd C:\Users\derri\advanced-stock-scanner\backend; python app.py

# Start Frontend (new terminal)
cd C:\Users\derri\advanced-stock-scanner\frontend; npm run dev

# Open App
Start-Process "http://localhost:3002"  # Check terminal for actual port
```

## 📍 Key Locations

- **Backend:** `C:\Users\derri\advanced-stock-scanner\backend\app.py`
- **Frontend:** `C:\Users\derri\advanced-stock-scanner\frontend\src\App.tsx`
- **Mobile:** `C:\Users\derri\rork-hot-stock-of-the-day-scanner\app\(tabs)\index.tsx`

## 🔌 Ports

- **Backend API:** `http://localhost:5000`
- **Frontend:** `http://localhost:3000-3002` (auto-assigned)
- **IB Gateway:** `127.0.0.1:4001`

## ✅ Health Check

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/health" | ConvertFrom-Json
```

## 🔍 Test Scanner

```powershell
$body = @{
    minPrice = 0.10
    maxPrice = 200
    minGainPercent = 0.1
    volumeMultiplier = 1.0
    displayCount = 20
    chartTimeframe = '5m'
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/scan" `
    -Method POST -Body $body -ContentType "application/json" -TimeoutSec 90
```

## ⚠️ Important Notes

- **IBKR is SLOW:** Scans take 30-90 seconds (normal!)
- **Auto-starts:** Scanner begins automatically on page load
- **Combined button:** Single "Scan Now" button (no separate Start/Refresh)
- **Cooldown:** 20 seconds after manual refresh
- **Keepalive:** Connection maintained automatically every 30s

## 🐛 Quick Troubleshooting

```powershell
# Check IB Gateway
netstat -ano | findstr ":4001"

# Check Backend
netstat -ano | findstr ":5000"

# Check Frontend
netstat -ano | findstr ":300"

# Check Processes
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"}
```

## 📊 Default Settings

```json
{
  "minPrice": 0.10,
  "maxPrice": 200,
  "minGainPercent": 0.1,
  "volumeMultiplier": 1.0,
  "displayCount": 20,
  "updateInterval": 90,
  "realTimeUpdates": true,
  "chartTimeframe": "5m"
}
```

## 🎯 Common Tasks

**Start App:**
1. Start backend → `python app.py` in `backend/`
2. Start frontend → `npm run dev` in `frontend/`
3. Open browser → `http://localhost:3002`

**Test Scanner:**
- App auto-starts scanning
- Wait 30-90 seconds
- Check browser console for logs
- Stocks appear in list

**Restart:**
- Stop processes → `Get-Process | Where-Object {...} | Stop-Process`
- Restart using commands above

---

**Full Guide:** See `AI_ASSISTANT_GUIDE.md` for complete documentation.

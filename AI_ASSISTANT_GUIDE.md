# Stock Scanner - AI Assistant Guide

This guide is designed to help AI assistants (like Ollama, Claude, GPT, etc.) understand and work with the Advanced Stock Scanner application.

## 📋 Quick Overview

**What it is:** A real-time stock scanner that fetches live stock data from Interactive Brokers (IBKR) and displays stocks matching specific criteria (price, gain %, volume).

**Architecture:**
- **Backend:** Python Flask API (`backend/app.py`) - Port 5000
- **Frontend:** React + TypeScript + Vite (`frontend/`) - Port 3000-3002 (auto-assigned)
- **Data Source:** Interactive Brokers API (IBKR) via `ib_insync` library
- **Mobile App:** React Native/Expo (`rork-hot-stock-of-the-day-scanner/`)

## 🚀 How to Start the Application

### Starting Backend (Flask API)

```powershell
# Navigate to backend directory
cd C:\Users\derri\advanced-stock-scanner\backend

# Start Flask server
python app.py
```

**Expected Output:**
- Server starts on `http://localhost:5000`
- Connects to IBKR Gateway on port 4001
- Keepalive thread starts (checks connection every 30s)

**Verification:**
```powershell
# Check if backend is running
netstat -ano | findstr ":5000"

# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET
```

### Starting Frontend (Web App)

```powershell
# Navigate to frontend directory
cd C:\Users\derri\advanced-stock-scanner\frontend

# Start Vite dev server
npm run dev
```

**Expected Output:**
- Server starts on `http://localhost:3000` (or 3001, 3002 if 3000 is busy)
- Shows: `Local: http://localhost:XXXX/`
- Auto-opens browser (or can be opened manually)

**Verification:**
```powershell
# Check if frontend is running
netstat -ano | findstr ":300"

# Test frontend
Invoke-WebRequest -Uri "http://localhost:3002" -Method GET
```

### Starting Mobile App (iOS/Android)

```powershell
# Navigate to mobile app directory
cd C:\Users\derri\rork-hot-stock-of-the-day-scanner

# Start Expo dev server
npm start
# or
npx expo start
```

## 🔌 Prerequisites

### Required Services

1. **Interactive Brokers Gateway/TWS**
   - Must be running on `127.0.0.1:4001`
   - Username: `userconti`
   - API must be enabled in Gateway settings
   - Check: `netstat -ano | findstr ":4001"`

2. **Python Environment**
   - Python 3.8+
   - Dependencies: `pip install -r backend/requirements.txt`
   - Key library: `ib_insync`

3. **Node.js Environment**
   - Node.js 18+
   - Frontend: `npm install` in `frontend/`
   - Mobile: `npm install` in `rork-hot-stock-of-the-day-scanner/`

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "ibkrAvailable": true,
  "ibkrConnected": true,
  "ibkrHost": "127.0.0.1",
  "ibkrPort": 4001,
  "ibkrUsername": "userconti",
  "connectionError": null,
  "timestamp": "2026-01-23T14:43:19"
}
```

### Scan Stocks
```http
POST /api/scan
Content-Type: application/json
```
**Request Body:**
```json
{
  "minPrice": 0.10,
  "maxPrice": 200,
  "minGainPercent": 0.1,
  "volumeMultiplier": 1.0,
  "displayCount": 20,
  "chartTimeframe": "5m",
  "autoAdd": true,
  "realTimeUpdates": true,
  "enabledTimeframes": ["5m"],
  "notificationsEnabled": true,
  "notifyOnNewStocks": true,
  "volumeActivityTimeframe": "1m"
}
```

**Response:**
```json
{
  "success": true,
  "stocks": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "currentPrice": 150.25,
      "changePercent": 2.5,
      "volume": 50000000,
      "avgVolume": 40000000,
      "float": 15000000000,
      "dayHigh": 152.00,
      "dayLow": 148.50,
      "openPrice": 149.00,
      "candles": [...],
      "chartData": {...},
      "isHot": true,
      "signal": "BUY"
    }
  ],
  "apiStatus": "ibkr",
  "scanTime": 45.2
}
```

**Important Notes:**
- Scan takes **30-90 seconds** (IBKR is slow)
- Timeout is set to 90 seconds
- Only scans **2 symbols** at a time (optimized for speed)

### Get Single Stock
```http
GET /api/stock/<SYMBOL>?timeframe=5m
```
**Example:**
```http
GET /api/stock/AAPL?timeframe=5m
```

### Connection Logs
```http
GET /api/logs
```
Returns recent connection and scan logs for debugging.

## 🎨 Frontend Features

### Main UI Components

1. **Combined Scan Button**
   - Single button replaces "Start" and "Refresh"
   - Shows: "Scan Now" / "Scanning..." / "Wait Xs"
   - Displays: Last scan time or next scan countdown
   - 20-second cooldown after manual refresh
   - Disabled during scans and cooldown

2. **Settings Panel**
   - Accessible via Settings button
   - Configurable filters: price, gain %, volume multiplier
   - Chart timeframe selection
   - Auto-refresh toggle
   - Display count setting

3. **Stock List**
   - Displays stocks matching criteria
   - Shows: symbol, name, price, gain %, volume
   - Click to open detail modal
   - Charts with candlestick patterns

4. **Connection Log Panel**
   - Accessible via "Log" button
   - Shows IBKR connection status
   - Copy logs button for troubleshooting

### Auto-Scan Behavior

- **On Mount:** Scanner automatically starts when app loads
- **Auto-Refresh:** If `realTimeUpdates: true`, scans every 90 seconds
- **Manual Refresh:** Click "Scan Now" button (20s cooldown)

## 📱 Mobile App Features

### Location
`C:\Users\derri\rork-hot-stock-of-the-day-scanner\`

### Key Features
- Same combined scan button as web app
- Copy connection logs button
- Pull-to-refresh
- Real-time stock updates
- Settings sync with web app

### Default Settings
```typescript
{
  minPrice: 0.10,
  maxPrice: 200,
  minGainPercent: 0.1,
  volumeMultiplier: 1.0,
  displayCount: 20,
  updateInterval: 90, // seconds
  realTimeUpdates: true,
  chartTimeframe: '5m'
}
```

## ⚙️ Configuration

### Backend Configuration (`.env` file)
```env
IBKR_HOST=127.0.0.1
IBKR_PORT=4001
IBKR_CLIENT_ID=1
IBKR_USERNAME=userconti
IBKR_PASSWORD=mbnadc21234
```

### Frontend Configuration
- Settings stored in browser `localStorage`
- Default settings in `frontend/src/App.tsx`
- Mobile settings in `rork-hot-stock-of-the-day-scanner/hooks/use-scanner-settings.tsx`

## 🔧 Common Tasks for AI Assistants

### Task 1: Start the Application
```powershell
# Terminal 1: Backend
cd C:\Users\derri\advanced-stock-scanner\backend
python app.py

# Terminal 2: Frontend
cd C:\Users\derri\advanced-stock-scanner\frontend
npm run dev

# Open browser
Start-Process "http://localhost:3002"
```

### Task 2: Test Scanner API
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
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -TimeoutSec 90
```

### Task 3: Check IBKR Connection
```powershell
# Check if IB Gateway is running
netstat -ano | findstr ":4001"

# Check backend health
Invoke-WebRequest -Uri "http://localhost:5000/api/health" | ConvertFrom-Json
```

### Task 4: Verify Stocks Are Showing
1. Open browser to frontend URL
2. Check browser console (F12) for logs
3. Look for "Scanning..." indicator
4. Wait 30-90 seconds for first scan
5. Stocks should appear in the list

### Task 5: Restart Services
```powershell
# Stop backend
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Where-Object {$_.Path -like "*advanced-stock-scanner*"} | Stop-Process

# Stop frontend
Get-Process | Where-Object {$_.ProcessName -eq "node"} | Where-Object {$_.Path -like "*advanced-stock-scanner*"} | Stop-Process

# Then restart using Task 1 commands
```

## 🐛 Troubleshooting

### Issue: Backend Not Responding
**Symptoms:** Health endpoint times out
**Solutions:**
1. Check if IB Gateway is running: `netstat -ano | findstr ":4001"`
2. Check backend logs for errors
3. Verify Python dependencies: `pip list | findstr ib-insync`
4. Restart backend

### Issue: No Stocks Showing
**Symptoms:** App loads but no stocks appear
**Solutions:**
1. Check browser console for errors
2. Verify backend is running: `netstat -ano | findstr ":5000"`
3. Check IBKR connection: `GET /api/health`
4. Verify settings are lenient enough (minGainPercent: 0.1, volumeMultiplier: 1.0)
5. Wait 30-90 seconds (IBKR is slow)
6. Check connection logs via "Log" button

### Issue: Client ID Already in Use
**Symptoms:** Backend logs show "Error 326: client id is already in use"
**Solutions:**
1. Close other IBKR connections
2. Change `IBKR_CLIENT_ID` in `.env` to a different number (2, 3, etc.)
3. Restart backend

### Issue: Frontend Port Conflicts
**Symptoms:** Vite tries multiple ports (3000, 3001, 3002...)
**Solutions:**
- This is normal - Vite auto-finds available port
- Use the port shown in terminal output
- Or specify port: `npm run dev -- --port 3002`

### Issue: Scanner Times Out
**Symptoms:** "Request timeout" after 90 seconds
**Solutions:**
- This is normal for IBKR (very slow API)
- Increase timeout in frontend if needed
- Reduce number of symbols scanned (currently 2)
- Check IBKR connection status

## 📊 Current Implementation Details

### Recent Changes (2026-01-23)

1. **Combined Scan Button**
   - Web and mobile apps now use single unified button
   - Shows last scan time and next scan countdown
   - 20-second cooldown after manual refresh
   - Spinning animation during scans

2. **Auto-Scan on Mount**
   - Scanner starts automatically when app loads
   - No need to click "Start" button
   - First scan begins immediately

3. **IBKR Connection Keepalive**
   - Background thread checks connection every 30 seconds
   - Automatically reconnects if connection lost
   - Prevents "kicked offline" issues

4. **Optimized Scanning**
   - Only scans 2 symbols at a time
   - Reduced sleep times in IBKR calls (0.3s instead of 1.0s)
   - 90-second update interval
   - Removed 24h data fetch during main scan

5. **Settings Synchronization**
   - Web, iOS, and Android use same default settings
   - `updateInterval: 90` seconds
   - Lenient filters to show more stocks

### File Locations

**Backend:**
- Main app: `C:\Users\derri\advanced-stock-scanner\backend\app.py`
- Requirements: `C:\Users\derri\advanced-stock-scanner\backend\requirements.txt`

**Frontend (Web):**
- Main app: `C:\Users\derri\advanced-stock-scanner\frontend\src\App.tsx`
- API client: `C:\Users\derri\advanced-stock-scanner\frontend\src\api\stockApi.ts`
- Settings: Default in `App.tsx`, stored in `localStorage`

**Mobile App:**
- Main screen: `C:\Users\derri\rork-hot-stock-of-the-day-scanner\app\(tabs)\index.tsx`
- Scanner hook: `C:\Users\derri\rork-hot-stock-of-the-day-scanner\hooks\use-stock-scanner.tsx`
- Settings hook: `C:\Users\derri\rork-hot-stock-of-the-day-scanner\hooks\use-scanner-settings.tsx`
- API client: `C:\Users\derri\rork-hot-stock-of-the-day-scanner\utils\stock-api.ts`

## 🎯 Key Points for AI Assistants

1. **IBKR is Slow:** Scans take 30-90 seconds - this is normal, not a bug
2. **Auto-Start:** Scanner starts automatically - no manual "Start" needed
3. **Combined Button:** Single button handles both start and refresh
4. **Cooldown:** 20-second cooldown prevents spam clicking
5. **Keepalive:** Connection is maintained automatically
6. **Lenient Defaults:** Settings are very lenient to show more stocks
7. **Real Stocks Only:** No mock data - only real IBKR data
8. **Multi-Platform:** Same features on web, iOS, and Android

## 📝 Example AI Assistant Workflow

When user asks to "start app and test scanner":

1. **Check Prerequisites**
   ```powershell
   netstat -ano | findstr ":4001"  # IB Gateway running?
   ```

2. **Start Backend**
   ```powershell
   cd C:\Users\derri\advanced-stock-scanner\backend
   python app.py
   ```

3. **Wait for Backend**
   ```powershell
   Start-Sleep -Seconds 5
   ```

4. **Verify Backend**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:5000/api/health"
   ```

5. **Start Frontend**
   ```powershell
   cd C:\Users\derri\advanced-stock-scanner\frontend
   npm run dev
   ```

6. **Wait for Frontend**
   ```powershell
   Start-Sleep -Seconds 5
   ```

7. **Open Browser**
   ```powershell
   Start-Process "http://localhost:3002"  # Use port from terminal output
   ```

8. **Verify Scanner**
   - Check browser console for "Scanning..." logs
   - Wait 30-90 seconds
   - Verify stocks appear in list

## 🔗 Related Documentation

- `README.md` - General project overview
- `IBKR_ONLY_MODE.md` - IBKR-specific details
- `TESTING_GUIDE.md` - Testing procedures
- `QUICK_START_WINDOWS.txt` - Quick setup guide

---

**Last Updated:** 2026-01-23  
**Version:** Advanced Stock Scanner with IBKR Integration  
**Maintained for:** AI Assistant Reference

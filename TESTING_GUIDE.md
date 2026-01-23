# Stock Scanner Testing Guide

## ✅ What's Configured

### 1. Backend Server (Port 5000)
- ✅ Running and connected to Interactive Brokers Gateway
- ✅ IB Gateway running on port 4001
- ✅ Username: `userconti`
- ✅ Real-time stock data from IBKR

### 2. Web Frontend (Port 3001)
- ✅ Running at: `http://localhost:3001`
- ✅ Configured to proxy API calls to backend
- ✅ Ready to scan real stocks

### 3. Mobile App (React Native/Expo)
- ✅ Updated to use real backend API
- ✅ API URL: `http://192.168.1.157:5000/api` (your computer's IP)
- ✅ Falls back to mock data if backend unavailable

## 🧪 Testing Steps

### Test Web Browser Interface

1. **Open Browser:**
   ```
   http://localhost:3001
   ```

2. **Check Settings:**
   - Click the Settings icon (⚙️)
   - Verify settings:
     - Min Price: $1
     - Max Price: $20
     - Max Float: 10M
     - Min Gain: 5-10%
     - Volume Multiplier: 2-4x

3. **Start Scanning:**
   - Click "▶ Start" button
   - OR click "🔄 Refresh" for one-time scan
   - Wait for stocks to appear (may take 30-60 seconds)

4. **Verify Real Stocks:**
   - Check that stocks show real prices
   - Verify charts show candlestick data
   - Check IBKR connection status in logs

### Test Mobile App (Simulator)

1. **Start Expo App:**
   ```bash
   cd C:\Users\derri\rork-hot-stock-of-the-day-scanner
   npm start
   # or
   bunx rork start -p xbi45cfy9xb7frrjwn0gz --tunnel
   ```

2. **Open in Simulator:**
   - Press `a` for Android emulator
   - Press `i` for iOS simulator
   - OR scan QR code with Expo Go app

3. **Verify Connection:**
   - App should connect to: `http://192.168.1.157:5000/api`
   - Check console logs for API calls
   - Stocks should appear from real backend

4. **Test Settings:**
   - Go to Settings tab
   - Adjust scan criteria
   - Click "Start" to scan
   - Verify real stocks appear

## 🔧 Troubleshooting

### Backend Not Responding
```bash
# Check if backend is running
netstat -ano | findstr ":5000"

# Restart backend
cd C:\Users\derri\advanced-stock-scanner\backend
python app.py
```

### IB Gateway Not Connected
```bash
# Check if IB Gateway is running
netstat -ano | findstr ":4001"

# Verify IB Gateway is logged in
# Check: Configure > API > Settings > Enable ActiveX and Socket Clients
```

### Mobile App Can't Connect
- Verify your computer's IP: `192.168.1.157`
- Make sure mobile device/simulator is on same network
- Check firewall allows port 5000
- Try using `localhost` if testing on same machine

### No Stocks Appearing
- Market may be closed (stocks only available during trading hours)
- Try more lenient criteria:
  - Min Price: $0.50
  - Max Price: $50
  - Min Gain: 1%
  - Volume Multiplier: 1.5x

## 📊 Current Settings

### Default Scanner Settings:
- **Price Range:** $1 - $20
- **Max Float:** 10,000,000 shares
- **Min Gain:** 5-10%
- **Volume Multiplier:** 2-4x average
- **Timeframe:** 5m charts
- **Display Count:** 10-20 stocks

### IBKR Connection:
- **Host:** 127.0.0.1
- **Port:** 4001 (IB Gateway)
- **Client ID:** 1
- **Username:** userconti

## 🚀 Quick Test Commands

### Test Backend API:
```powershell
# Test scan endpoint
$body = @{
    minPrice = 1
    maxPrice = 20
    maxFloat = 10000000
    minGainPercent = 5
    volumeMultiplier = 2
    chartTimeframe = "5m"
    displayCount = 5
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/scan" -Method POST -ContentType "application/json" -Body $body
```

### Check IBKR Connection:
```powershell
# Check backend status
Invoke-WebRequest -Uri "http://localhost:5000/api/scan" -Method POST -ContentType "application/json" -Body '{"minPrice":1,"maxPrice":20,"maxFloat":10000000,"minGainPercent":1,"volumeMultiplier":1.5,"chartTimeframe":"5m","displayCount":1}' | Select-Object -ExpandProperty Content
```

## ✅ Success Indicators

- ✅ Backend shows: `ibkrConnected: true` in API response
- ✅ Web browser shows stock cards with real prices
- ✅ Mobile app shows stocks from backend (not mock data)
- ✅ Charts display candlestick data
- ✅ Settings panel allows adjusting criteria

## 📝 Notes

- Stocks only available during market hours (9:30 AM - 4:00 PM ET)
- First scan may take 30-60 seconds (IBKR data fetching)
- Subsequent scans are faster (cached data)
- If no stocks meet criteria, try more lenient settings

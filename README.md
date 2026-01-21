# Advanced Stock Scanner

A real-time stock scanner that identifies low-float, high-volume stocks with significant price gains. Built with Python Flask backend and React TypeScript frontend.

## Features

### Core Functionality
- ✅ **Real-time Stock Data** - Live data from Yahoo Finance API
- ✅ **Advanced Filtering** - Filter by price, float, gain %, and volume
- ✅ **Auto-Discovery** - Automatically adds stocks that meet your criteria
- ✅ **Live Updates** - Refreshes every 30 seconds (configurable)
- ✅ **Smart Notifications** - Alerts for new qualifying stocks
- ✅ **Mobile Support** - 📱 Works on iOS & Android (PWA)

### Filtering Criteria
- **Price Range** - Set minimum and maximum price limits ($1-$20 default)
- **Max Float** - Filter by shares outstanding (10M default) - Now with K/M formatting! 📊⚡
- **Minimum Gain** - Only show stocks with X% or more gain (10% default) 🔥
- **Volume Multiplier** - Current volume vs average (5x default) 💥

### Display Features
- **Professional Charts** - 🎨 Beautiful green/red candlesticks with 3 moving averages (MA20/MA50/MA200) and buy/sell volume indicators
- **Multiple Timeframes** - 1m, 3m, 5m, 15m, 30m, 1h, 24h candlestick charts
- **Interactive Detail View** - 📊 Click any stock to open large modal with instant timeframe switching (1m/5m/1h/24h) - all data pre-loaded, zero extra API calls!
- **Real-time Stats** - Volume, float, day high/low, open/close prices
- **Signal Indicators** - BUY/SELL/HOLD signals based on momentum
- **Hot Stock Badges** - Highlights exceptional volume activity
- **Countdown Timer** - Shows seconds until next scan ⏱️
- **Scanning Indicators** - Visual feedback when fetching data
- **Play/Pause Control** - Toggle auto-refresh on/off from main page ⏯️
- **Manual Start Mode** - Scanner waits for you to click Start or choose a preset (no auto-scan on load) 🎮
- **Quick Presets** - One-click switching between Penny Stocks ($0.05-$1) and Explosive Mode ($1-$20) 💰
- **Ready Time Indicator** - RED banner when rate limited (with countdown), GREEN banner when ready to scan ⏰🔴🟢
- **Persistent Rate Lock** - 🔒 Rate limit persists across refreshes! Scanner stays locked until 45-min countdown completes (saved in localStorage)
- **Comprehensive FAQ** - 📚 Built-in Help & FAQ section (26 questions) covering charts, features, trading tips, and technical details - accessible from Settings panel

## Quick Start

### Windows (Easiest)
1. **Double-click** `setup-windows.bat` to install dependencies
2. **Double-click** `start-scanner.bat` to start the app
3. Open browser: http://localhost:3000

### Manual Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**📖 See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed Windows instructions**

## Tech Stack

### Backend
- Python 3.8+
- Flask (REST API)
- yfinance (Real-time stock data)
- pandas (Data processing)

### Frontend
- React 18
- TypeScript
- Vite (Build tool)
- Tailwind CSS (Styling)
- Recharts (Charting)
- Sonner (Notifications)

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Mobile Access

Access from iPhone/Android on the same Wi-Fi network:

1. Find your PC's IP address:
   ```bash
   # Windows
   ipconfig
   
   # Look for IPv4 Address (e.g., 192.168.1.157)
   ```

2. On your mobile device, open browser and go to:
   ```
   http://YOUR_PC_IP:3000
   ```

3. **Install as App:**
   - **iOS**: Tap Share → "Add to Home Screen"
   - **Android**: Tap Menu → "Install app"

See `MOBILE_SETUP_GUIDE.md` for detailed instructions.

## Quick Start Scripts

### Windows

Run both backend and frontend:
```bash
start-scanner.bat
```

### Manual Start

**Terminal 1 (Backend):**
```bash
cd backend
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## Usage

1. **Open the App** - Navigate to `http://localhost:3001`
2. **Start Scanning** - Scanner is paused on startup. Choose how to begin:
   - Click **"▶ Start"** button to begin with current settings
   - Click **"🔄 Refresh"** for a one-time scan
   - OR Choose a preset in Settings first (recommended):
     - **💰 Penny Stocks** - Scan $0.05-$1.00 stocks (ultra-cheap, massive % gains)
     - **🔥 Explosive Mode** - Scan $1-$20 stocks (quality setups, high liquidity)
3. **Control Auto-Refresh** - Use the Play/Pause button to turn auto-scanning on/off ⏯️
4. **Monitor Updates** - Watch for new stock alerts and price changes
5. **Analyze Charts** - Review candlestick charts for each qualifying stock

### 📊 Easy Float Formatting (NEW!)

The **Max Float** setting now supports **K** (thousands) and **M** (millions) formatting:

```
Quick Examples:
10M    = 10,000,000 shares (10 million)
500K   = 500,000 shares (500 thousand)
2.5M   = 2,500,000 shares (2.5 million)
100M   = 100,000,000 shares (100 million)
```

**Benefits:**
- ✅ Easier to read - "10M" vs "10000000"
- ✅ Faster to type - Just 3 characters!
- ✅ Instant understanding - No counting zeros

**How to use:**
1. Open Settings
2. In "Max Float (shares)", type: `10M` or `500K` or `2.5M`
3. Press Apply Settings
4. Done! ✅

See `FLOAT_FORMATTING.md` for complete guide and examples.

### Recommended Settings for Day Trading

**PENNY STOCK MODE:** 💰🚀
- Min Price: **$0.05**
- Max Price: **$1.00**
- Max Float: **100M** (penny stocks have higher float)
- Min Gain: **10%** EXPLOSIVE
- Volume Multiplier: **5x** MASSIVE VOLUME
- Update Interval: 20s ⚡
- One-click preset in Settings!

**EXPLOSIVE MODE (Current Default):** 🔥⚡💥
- Min Price: $1
- Max Price: $20
- Max Float: **10M** LOW-FLOAT
- Min Gain: **10%** 🚀 EXPLOSIVE
- Volume Multiplier: **5x** 💥 MASSIVE VOLUME
- Update Interval: 20s ⚡

**EXTREME MODE (Highest Risk/Reward):**
- Min Price: $1
- Max Price: $20
- Max Float: **5M** ⚡ ULTRA LOW-FLOAT
- Min Gain: 15%+
- Volume Multiplier: 10x+ 🔥 PARABOLIC VOLUME

**Aggressive (High Risk/Reward):**
- Min Price: $1
- Max Price: $10
- Max Float: **50M**
- Min Gain: 10%
- Volume Multiplier: 3-4x

**Moderate (Balanced):**
- Min Price: $1
- Max Price: $20
- Max Float: **100M** 📊
- Min Gain: 5%
- Volume Multiplier: 2x
- Update Interval: 20s

**Conservative (Lower Risk):**
- Min Price: $5
- Max Price: $20
- Max Float: **500M**
- Min Gain: 2%
- Volume Multiplier: 1.5x

## API Endpoints

### `POST /api/scan`
Scan stocks with criteria
```json
{
  "minPrice": 1,
  "maxPrice": 20,
  "maxFloat": 1000000000,
  "minGainPercent": 10,
  "volumeMultiplier": 2,
  "chartTimeframe": "5m",
  "displayCount": 5
}
```

### `GET /api/stock/<symbol>`
Get detailed stock data
```
GET /api/stock/AAPL?timeframe=5m
```

### `GET /api/symbols`
Get list of tracked symbols

### `POST /api/symbols`
Add a new symbol to track
```json
{
  "symbol": "GME"
}
```

## Customization

### Adding More Symbols

Edit `backend/app.py` and add symbols to the `DEFAULT_SYMBOLS` list:

```python
DEFAULT_SYMBOLS = [
    'AAPL', 'TSLA', 'AMD', 'NVDA',
    # Add your symbols here
    'YOUR_SYMBOL'
]
```

### Adjusting Update Frequency

In `frontend/src/App.tsx`, change the interval (default 5000ms = 5 seconds):

```typescript
intervalRef.current = setInterval(() => {
  performScan()
}, 5000) // Change this value
```

## Performance Tips

1. **Limit Display Count** - Showing fewer stocks improves performance
2. **Reduce Update Frequency** - Increase interval if experiencing lag
3. **Filter Symbols** - Start with a smaller list of symbols
4. **Use Longer Timeframes** - 15m/30m charts load faster than 1m

## Troubleshooting

### Backend Issues

**Port Already in Use:**
```bash
# Change port in backend/app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Yahoo Finance Rate Limits:**
- Reduce update frequency
- Add delays between requests
- Consider using a premium API

### Frontend Issues

**CORS Errors:**
- Ensure Flask-CORS is installed
- Check backend is running on port 5000

**Build Errors:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## License

MIT License - feel free to use and modify for your needs.

## Disclaimer

⚠️ **IMPORTANT**: This tool is for educational purposes only. It does not provide financial advice. Always do your own research before making investment decisions. Trading stocks carries risk and you can lose money.

## Support

For issues or questions, please create an issue on GitHub or contact the developer.

---

**Happy Trading! 📈**

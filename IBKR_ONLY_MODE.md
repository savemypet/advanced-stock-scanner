# Interactive Brokers Only Mode

## ✅ Configuration Complete

The application is now configured to use **ONLY Interactive Brokers API**. All other APIs (Yahoo Finance, Massive.com, AlphaVantage, SerpAPI) have been disabled.

## 🔌 Setup Requirements

### 1. Install TWS or IB Gateway
- Download from: https://www.interactivebrokers.com/en/index.php?f=16042
- Install and log in with credentials: `userconti` / `mbnadc21234`

### 2. Enable API Connection
1. Open TWS or IB Gateway
2. Go to: **Configure > API > Settings**
3. Enable: **"Enable ActiveX and Socket Clients"**
4. Set port: **7497** (paper trading) or **7496** (live trading)
5. Add trusted IP: **127.0.0.1**

### 3. Start TWS/IB Gateway
- Log in with your credentials
- Keep it running while using the app
- The app will automatically connect on startup

## 📊 Features

### Real 24h Data for AI Study
- All stocks automatically fetch 24-hour historical data
- Data is used for AI pattern detection and study
- Includes both requested timeframe AND 24h data

### IBKR Connection
- Host: `127.0.0.1` (localhost)
- Port: `7497` (paper) or `7496` (live)
- Client ID: `1`
- Username: `userconti`

## ⚠️ Important Notes

1. **No Fallbacks**: If IBKR is unavailable, the app will return errors (no automatic fallback to other APIs)

2. **TWS Must Be Running**: The app requires TWS or IB Gateway to be running and logged in

3. **24h Data Always Included**: Every stock fetch includes 24h data for AI study, regardless of requested timeframe

4. **Connection Status**: Check logs for connection status messages

## 🚀 Usage

1. Start TWS/IB Gateway and log in
2. Run the app: `start-scanner.bat`
3. The app will automatically connect to IBKR
4. All stock data comes from Interactive Brokers

## 🔍 Testing

Test the connection:
```bash
curl http://localhost:5000/api/stock/AAPL?timeframe=24h
```

Expected response:
- `source: "Interactive Brokers (Real Data)"`
- `candles: [array of 24h candles]`
- `chartData.24h: [24h data for AI study]`

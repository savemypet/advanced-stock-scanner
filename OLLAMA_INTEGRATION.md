# Ollama AI Integration Guide

## Overview

The stock scanner now includes Ollama AI integration for:
1. **Candlestick Pattern Analysis** - AI reads and analyzes candlestick charts
2. **Trading Decisions** - AI provides BUY/SELL/HOLD signals with confidence levels
3. **Pattern Teaching** - Teach Ollama new candlestick patterns
4. **Future Trading** - Framework ready for automated buy/sell execution

## Prerequisites

1. **Install Ollama**
   ```bash
   # Download from https://ollama.ai
   # Or use: winget install Ollama.Ollama (Windows)
   ```

2. **Pull a Model**
   ```bash
   ollama pull llama3.2
   # Or use: llama3.1, mistral, codellama, etc.
   ```

3. **Start Ollama**
   ```bash
   ollama serve
   # Runs on http://localhost:11434 by default
   ```

## Backend Integration

### Files Created

1. **`backend/ollama_service.py`**
   - Main Ollama service module
   - Handles API communication
   - Contains candlestick teaching prompts
   - Provides analysis functions

2. **`backend/app.py`** (Updated)
   - Added Ollama endpoints:
     - `GET /api/ollama/status` - Check connection
     - `POST /api/ollama/analyze` - Analyze candlesticks
     - `POST /api/ollama/teach` - Teach new patterns
     - `POST /api/ollama/trade-decision` - Get trading decision

### Configuration

Edit `backend/ollama_service.py` to customize:
```python
OLLAMA_BASE_URL = "http://localhost:11434"  # Change if Ollama runs elsewhere
OLLAMA_MODEL = "llama3.2"  # Change to your preferred model
OLLAMA_TIMEOUT = 30  # Adjust timeout as needed
```

## Frontend Integration

### Files Created

1. **`frontend/src/api/ollamaApi.ts`**
   - API client for Ollama endpoints
   - TypeScript interfaces
   - Error handling

2. **`frontend/src/components/OllamaAnalysis.tsx`**
   - React component for AI analysis
   - Displays analysis results
   - Shows trading recommendations
   - Integrated into StockDetailModal

### Usage

The OllamaAnalysis component is automatically shown in the stock detail modal when you click on a stock. It:
- Checks Ollama connection status
- Analyzes candlestick patterns
- Provides BUY/SELL/HOLD signals
- Shows confidence levels
- Displays entry/stop/target prices (when available)

## API Endpoints

### Check Status
```http
GET /api/ollama/status
```

**Response:**
```json
{
  "available": true,
  "models": ["llama3.2", "mistral"],
  "baseUrl": "http://localhost:11434"
}
```

### Analyze Candlesticks
```http
POST /api/ollama/analyze
Content-Type: application/json

{
  "symbol": "AAPL",
  "candles": [...],
  "currentPrice": 150.25,
  "volume": 50000000,
  "avgVolume": 40000000
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "pattern": "BULLISH_ENGULFING",
    "signal": "BUY",
    "confidence": "HIGH",
    "reasoning": "Strong bullish engulfing pattern with high volume...",
    "entryPrice": 150.50,
    "stopLoss": 148.00,
    "takeProfit": 155.00,
    "timestamp": "2026-01-23T14:43:19",
    "model": "llama3.2",
    "candleCount": 20,
    "volumeRatio": 1.25
  }
}
```

### Get Trading Decision
```http
POST /api/ollama/trade-decision
Content-Type: application/json

{
  "symbol": "AAPL",
  "candles": [...],
  "currentPrice": 150.25,
  "volume": 50000000,
  "avgVolume": 40000000,
  "accountBalance": 10000,
  "riskTolerance": "MEDIUM"
}
```

**Response:**
```json
{
  "success": true,
  "decision": {
    "symbol": "AAPL",
    "action": "BUY",
    "confidence": "HIGH",
    "reasoning": "...",
    "entryPrice": 150.50,
    "stopLoss": 148.00,
    "takeProfit": 155.00,
    "pattern": "BULLISH_ENGULFING",
    "timestamp": "2026-01-23T14:43:19",
    "readyToExecute": true,
    "recommendedQuantity": 13
  }
}
```

### Teach Pattern
```http
POST /api/ollama/teach
Content-Type: application/json

{
  "patternName": "CUSTOM_PATTERN",
  "description": "Three consecutive green candles with increasing volume",
  "examples": [
    {
      "candles": [
        {"open": 100, "high": 102, "low": 99, "close": 101},
        {"open": 101, "high": 103, "low": 100, "close": 102},
        {"open": 102, "high": 104, "low": 101, "close": 103}
      ],
      "signal": "BUY",
      "confidence": "HIGH"
    }
  ]
}
```

## Candlestick Patterns Taught

The system includes comprehensive teaching for:

### Bullish Patterns
- HAMMER
- BULLISH_ENGULFING
- MORNING_STAR
- PIERCING_LINE
- THREE_WHITE_SOLDIERS

### Bearish Patterns
- SHOOTING_STAR
- BEARISH_ENGULFING
- EVENING_STAR
- DARK_CLOUD_COVER
- THREE_BLACK_CROWS

### Neutral Patterns
- DOJI
- SPINNING_TOP

## Future: Buy/Sell Integration

The framework is ready for automated trading. When you implement buy/sell:

1. **Use Trade Decision Endpoint**
   - Get AI decision with `readyToExecute: true`
   - Check `recommendedQuantity` for position sizing

2. **Execute Trade**
   - Use IBKR API to place order
   - Set stop loss and take profit from AI recommendations
   - Log trade execution

3. **Example Flow**
   ```python
   # Get AI decision
   decision = get_trade_decision(symbol, candles, ...)
   
   if decision['readyToExecute'] and decision['action'] == 'BUY':
       # Place buy order via IBKR
       place_order(
           symbol=symbol,
           quantity=decision['recommendedQuantity'],
           order_type='MKT',
           stop_loss=decision['stopLoss'],
           take_profit=decision['takeProfit']
       )
   ```

## Testing

1. **Start Ollama**
   ```bash
   ollama serve
   ```

2. **Start Backend**
   ```bash
   cd backend
   python app.py
   ```

3. **Test Connection**
   ```bash
   curl http://localhost:5000/api/ollama/status
   ```

4. **Test Analysis**
   - Open app in browser
   - Click on a stock
   - Click "Analyze" in AI Analysis section
   - Wait 10-30 seconds for analysis

## Troubleshooting

### Ollama Not Available
- Check if Ollama is running: `curl http://localhost:11434/api/tags`
- Verify model is installed: `ollama list`
- Check backend logs for connection errors

### Analysis Takes Too Long
- Use smaller model (llama3.2 instead of llama3.1)
- Reduce number of candles analyzed
- Increase timeout in `ollama_service.py`

### Poor Analysis Quality
- Try different model (mistral, codellama)
- Adjust temperature in `ollama_service.py` (lower = more consistent)
- Teach Ollama more patterns using `/api/ollama/teach`

## Customization

### Change Model
Edit `backend/ollama_service.py`:
```python
OLLAMA_MODEL = "mistral"  # or "codellama", "llama3.1", etc.
```

### Adjust Analysis Parameters
```python
"options": {
    "temperature": 0.3,  # Lower = more consistent, Higher = more creative
    "top_p": 0.9,        # Nucleus sampling
}
```

### Add Custom Patterns
Use the `/api/ollama/teach` endpoint to teach Ollama your own patterns.

## Next Steps

1. ✅ **Candlestick Analysis** - Complete
2. ✅ **Trading Decisions** - Complete (framework ready)
3. ⏳ **Buy/Sell Execution** - To be implemented
4. ⏳ **Position Management** - To be implemented
5. ⏳ **Risk Management** - To be implemented
6. ⏳ **Backtesting** - To be implemented

---

**Last Updated:** 2026-01-23  
**Status:** Ready for buy/sell integration

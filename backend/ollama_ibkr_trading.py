"""
IBKR Trading Knowledge for Ollama
Teaches Ollama how to use Interactive Brokers API for trading
"""
import requests
import logging
from typing import Dict, Any

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:4b"  # Use available model
OLLAMA_TIMEOUT = 60

# COMPREHENSIVE IBKR TRADING KNOWLEDGE
IBKR_TRADING_KNOWLEDGE = """
# INTERACTIVE BROKERS (IBKR) TRADING API KNOWLEDGE

## OVERVIEW
Interactive Brokers provides a powerful API for automated trading through ib_insync (Python library).
The backend uses ib_insync to connect to IBKR TWS (Trader Workstation) or IB Gateway.

## CONNECTION DETAILS
- **Host**: 127.0.0.1 (localhost)
- **Port**: 4001 (IB Gateway default) or 7497 (TWS paper trading)
- **Client ID**: Unique ID for each connection (prevents conflicts)
- **Username**: userconti
- **Connection**: Socket-based, requires TWS/IB Gateway running

## AVAILABLE TRADING FUNCTIONS

### 1. Market Orders
**Function**: `place_market_order()`
**Purpose**: Execute orders immediately at current market price
**Parameters**:
- `symbol`: Stock symbol (e.g., 'AAPL')
- `action`: 'BUY' or 'SELL'
- `quantity`: Number of shares (integer)
- `stop_loss_percent`: Optional stop loss percentage (e.g., 2.0 for 2%)
- `take_profit_percent`: Optional take profit percentage (e.g., 5.0 for 5%)

**Example**:
```python
place_market_order(
    symbol='AAPL',
    action='BUY',
    quantity=100,
    stop_loss_percent=2.0,  # 2% stop loss
    take_profit_percent=5.0  # 5% take profit
)
```

### 2. Limit Orders
**Function**: `place_limit_order()`
**Purpose**: Execute orders at a specific price or better
**Parameters**:
- `symbol`: Stock symbol
- `action`: 'BUY' or 'SELL'
- `quantity`: Number of shares
- `limit_price`: Maximum (buy) or minimum (sell) price
- `stop_loss_percent`: Optional stop loss percentage
- `take_profit_percent`: Optional take profit percentage

**Example**:
```python
place_limit_order(
    symbol='AAPL',
    action='BUY',
    quantity=100,
    limit_price=150.00,
    stop_loss_percent=2.0,
    take_profit_percent=5.0
)
```

### 3. Stop Loss and Take Profit
**How it works**:
- Stop loss and take profit are implemented as **bracket orders**
- Parent order (entry) is placed first
- Child orders (stop loss, take profit) are linked via `parentId`
- All orders are submitted together when `transmit=True` on final order

**Stop Loss Calculation**:
- For BUY orders: Stop loss = Entry Price × (1 - stop_loss_percent / 100)
- For SELL orders: Stop loss = Entry Price × (1 + stop_loss_percent / 100)

**Take Profit Calculation**:
- For BUY orders: Take profit = Entry Price × (1 + take_profit_percent / 100)
- For SELL orders: Take profit = Entry Price × (1 - take_profit_percent / 100)

**Example**:
- Entry: $100
- Stop Loss: 2% → $98 (for BUY)
- Take Profit: 5% → $105 (for BUY)

### 4. Order Management
**Cancel Order**: `cancel_order(order_id)`
- Cancels an order by its order ID
- Returns success/failure status

**Get Order Status**: `get_order_status(order_id)`
- Returns current status: 'Submitted', 'Filled', 'Cancelled', etc.
- Shows filled quantity, remaining quantity, average fill price

**Get Open Positions**: `get_open_positions()`
- Returns all current positions
- Shows symbol, quantity, average cost, market price, market value

## ORDER TYPES AVAILABLE

### MarketOrder
- Executes immediately at best available price
- Fast execution, no price guarantee
- Use for: Urgent trades, high liquidity stocks

### LimitOrder
- Executes only at specified price or better
- Price protection, may not fill
- Use for: Price-sensitive trades, limit entry/exit

### StopOrder
- Triggers when price reaches stop level
- Becomes market order when triggered
- Use for: Stop loss protection

### StopLimitOrder
- Combines stop and limit
- Triggers at stop price, executes at limit price
- Use for: More control over stop loss execution

## BRACKET ORDERS (Stop Loss + Take Profit)

Bracket orders link multiple orders together:
1. **Parent Order**: Entry order (Market or Limit)
2. **Child Orders**: Stop loss and/or take profit
3. **Transmission**: Parent has `transmit=False`, last child has `transmit=True`

**Benefits**:
- Automatic risk management
- All orders submitted together
- If entry fills, stop/target automatically active
- If entry cancelled, stop/target also cancelled

## RISK MANAGEMENT

### Stop Loss Guidelines
- **Conservative**: 1-2% stop loss
- **Moderate**: 2-3% stop loss
- **Aggressive**: 3-5% stop loss
- **Never trade without stop loss** (unless very experienced)

### Take Profit Guidelines
- **Risk-Reward Ratio**: Aim for at least 2:1 (profit:loss)
- Example: 2% stop loss → 4%+ take profit
- **Scaling Out**: Consider taking partial profits at 2%, 3%, 5%

### Using High/Low Prices for Trading Decisions

**KEY CONCEPT**: High and Low prices are critical support and resistance levels.

#### Entry Strategy Using High/Low:
1. **For BUY orders**:
   - **Best Entry**: Wait for price to pull back to recent LOW (support level)
   - **Alternative**: Enter near recent LOW if price is bouncing off it
   - **Avoid**: Entering at recent HIGH (resistance level)
   - **Entry Price**: Should be closer to LOW than HIGH for better risk/reward

2. **For SELL orders**:
   - **Best Entry**: Wait for price to reach recent HIGH (resistance level)
   - **Alternative**: Enter near recent HIGH if price is rejecting it
   - **Avoid**: Entering at recent LOW (support level)
   - **Entry Price**: Should be closer to HIGH than LOW for better risk/reward

#### Stop Loss Using High/Low:
1. **For BUY orders**:
   - **Initial Stop Loss**: Set below the recent LOW (support break = exit signal)
   - **Example**: If LOW is $98 and entry is $100, set stop at $97.50 (below support)
   - **Rationale**: If price breaks below support, the bullish setup is invalidated

2. **For SELL orders**:
   - **Initial Stop Loss**: Set above the recent HIGH (resistance break = exit signal)
   - **Example**: If HIGH is $102 and entry is $100, set stop at $102.50 (above resistance)
   - **Rationale**: If price breaks above resistance, the bearish setup is invalidated

#### Take Profit Using High/Low:
1. **For BUY orders**:
   - **Take Profit Target**: Set near or at recent HIGH (resistance level)
   - **Example**: If HIGH is $105 and entry is $100, target $104-105 (near resistance)
   - **Rationale**: Price often reverses at resistance levels

2. **For SELL orders**:
   - **Take Profit Target**: Set near or at recent LOW (support level)
   - **Example**: If LOW is $95 and entry is $100, target $95-96 (near support)
   - **Rationale**: Price often reverses at support levels

### TRAILING STOP LOSS (Raising Stop Loss as Price Moves Up)

**What is a Trailing Stop?**
- A stop loss that automatically moves up as the stock price increases
- Locks in profits while allowing the trade to continue running
- Protects against giving back gains if price reverses

**How Trailing Stops Work**:
1. **Initial Stop**: Set below entry (e.g., 2% below entry price)
2. **As Price Rises**: Stop loss moves up, maintaining a fixed distance (e.g., 2%)
3. **Never Moves Down**: Stop loss only moves up, never down
4. **Lock in Profits**: Once price moves up 5%, stop loss is at +3% (protecting 3% profit)

**Trailing Stop Strategy**:
- **Conservative**: 2-3% trailing distance (tighter, exits sooner)
- **Moderate**: 3-5% trailing distance (balanced)
- **Aggressive**: 5-7% trailing distance (allows more room for volatility)

**When to Use Trailing Stops**:
- **Strong Uptrend**: Stock is moving up consistently → use trailing stop to ride the trend
- **After Take Profit Hit**: Once first target is hit, move stop to breakeven, then trail
- **High Volatility**: Use wider trailing distance (5-7%) to avoid being stopped out by normal swings
- **Low Volatility**: Use tighter trailing distance (2-3%) to lock in profits faster

**Trailing Stop Implementation**:
```
Example: BUY at $100, initial stop at $98 (2% below)
- Price moves to $105 (+5%): Stop moves to $103 (+3% profit locked)
- Price moves to $110 (+10%): Stop moves to $108 (+8% profit locked)
- Price moves to $115 (+15%): Stop moves to $113 (+13% profit locked)
- If price drops to $113: Stop triggers, exit with +13% profit
```

**Key Rules for Trailing Stops**:
1. **Never lower the stop**: Only raise it as price moves in your favor
2. **Use support levels**: When possible, set trailing stop just below key support levels
3. **Adjust for volatility**: More volatile stocks need wider trailing stops
4. **Lock in breakeven**: Once price moves 2-3% in your favor, move stop to entry price (breakeven)
5. **Trail after first target**: After hitting first take profit, switch to trailing stop mode

### Position Sizing
- **Risk per Trade**: Never risk more than 1-2% of account
- **Example**: $10,000 account, 1% risk = $100 max loss per trade
- If stop loss is 2%, position size = $100 / 0.02 = $5,000

## OLLAMA TRADING CONSTRAINTS

**CRITICAL RULES - MUST FOLLOW:**
1. **Price Range**: ONLY trade stocks priced between $1.00 and $6.00
   - If stock price is below $1.00 or above $6.00, DO NOT trade
   - Reject any trade outside this range immediately

2. **Position Size**: Use FULL $4,000 for each stock
   - Always use the complete $4,000 allocation for every stock bought
   - Calculate: quantity = $4,000 / entry_price
   - Example: If entry is $2.00, buy 2,000 shares ($4,000 total)
   - Example: If entry is $5.00, buy 800 shares ($4,000 total)
   - Ollama uses the full $4,000 allocation - no partial positions

3. **End of Day Closing**: All positions MUST close before market close (4:00 PM ET)
   - Market closes at 4:00 PM ET (16:00)
   - Start closing positions at 3:50 PM ET (15:50) to ensure execution
   - Do NOT open new positions after 3:30 PM ET
   - Close all open positions before end of day - no overnight holds

## TRADING DECISION FRAMEWORK

When Ollama recommends a trade, it should consider:

1. **Entry Price**: Current price or limit price
2. **Stop Loss**: Based on pattern, support/resistance, volatility
3. **Take Profit**: Based on pattern target, resistance, risk-reward ratio
4. **Position Size**: Based on account size and risk tolerance
5. **Order Type**: Market (urgent) vs Limit (price control)

### Example Trading Decision
```
Pattern: BULLISH_ENGULFING detected
Signal: BUY
Confidence: HIGH
Entry: $100.00 (current price)
Stop Loss: $98.00 (2% below entry)
Take Profit: $105.00 (5% above entry)
Risk-Reward: 2.5:1 (good)
Position Size: 100 shares ($10,000)
Order Type: Market (strong signal, high confidence)
```

## API ENDPOINTS

The backend provides these endpoints:

### POST /api/trade/buy
**Request Body**:
```json
{
  "symbol": "AAPL",
  "quantity": 100,
  "orderType": "MARKET",  // or "LIMIT"
  "limitPrice": 150.00,  // required if orderType is "LIMIT"
  "stopLossPercent": 2.0,
  "takeProfitPercent": 5.0
}
```

### POST /api/trade/sell
**Request Body**: Same as buy, but action is SELL

### GET /api/trade/positions
Returns all open positions

### GET /api/trade/order/:orderId
Returns order status

### POST /api/trade/cancel/:orderId
Cancels an order

## ERROR HANDLING

Common errors:
- **"IBKR not connected"**: TWS/IB Gateway not running or not connected
- **"No market price available"**: Symbol not found or market closed
- **"Insufficient funds"**: Not enough buying power
- **"Order rejected"**: Invalid order parameters or market restrictions

## BEST PRACTICES

1. **Always use stop loss** - Protect capital
2. **Check connection** - Verify IBKR is connected before trading
3. **Verify market hours** - Don't trade when market is closed
4. **Start small** - Test with small positions first
5. **Monitor orders** - Check order status regularly
6. **Risk management** - Never risk more than you can afford to lose
7. **Paper trading first** - Test strategies in paper trading mode

## INTEGRATION WITH CANDLESTICK ANALYSIS

When analyzing candlestick patterns:
1. Identify pattern and signal (BUY/SELL)
2. Calculate entry price (current price or pattern target)
3. Set stop loss based on pattern support/resistance
4. Set take profit based on pattern target or risk-reward
5. Determine position size based on risk tolerance
6. Place order with appropriate order type

**Example Integration**:
```
Pattern: MORNING_STAR detected
→ Signal: BUY
→ Entry: Current price $100
→ Stop Loss: Below pattern low ($98, 2%)
→ Take Profit: Pattern target ($105, 5%)
→ Risk-Reward: 2.5:1 (excellent)
→ Action: Place MARKET BUY order with 2% stop, 5% target
```

## SUMMARY

You now understand:
- How to place market and limit orders
- How to set stop loss and take profit
- How bracket orders work
- Risk management principles
- Integration with candlestick analysis
- API endpoints available
- Best practices for trading

Use this knowledge to make informed trading decisions and execute trades through the IBKR API.
"""

def teach_ibkr_trading_to_ollama() -> Dict[str, Any]:
    """
    Teach Ollama about IBKR trading capabilities
    """
    try:
        teaching_prompt = f"""
You are learning how to use Interactive Brokers (IBKR) API for automated stock trading.

{IBKR_TRADING_KNOWLEDGE}

LEARNING TASK:
1. Understand IBKR connection and API structure
2. Learn how to place market and limit orders
3. Understand stop loss and take profit implementation
4. Learn bracket orders and risk management
5. Understand integration with candlestick analysis
6. Learn API endpoints and error handling

After learning, you should be able to:
- Recommend appropriate order types (market vs limit)
- Calculate stop loss and take profit prices
- Determine position sizes based on risk
- Make trading decisions based on candlestick patterns
- Understand when to use different order types

Please acknowledge that you understand IBKR trading capabilities and are ready to make trading recommendations.

Respond with: "I understand IBKR trading API and am ready to make trading recommendations."
"""
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": teaching_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 200,
                },
                "system": "You are learning to be an expert trading assistant using Interactive Brokers API. Pay close attention to all trading details and risk management."
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            logging.info("✅ [OLLAMA IBKR] Trading knowledge taught successfully")
            logging.info(f"📚 [OLLAMA IBKR] Response: {response_text[:200]}...")
            
            return {
                'success': True,
                'message': 'IBKR trading knowledge taught successfully',
                'response_preview': response_text[:200]
            }
        else:
            logging.error(f"❌ [OLLAMA IBKR] API error: {response.status_code}")
            return {
                'success': False,
                'error': f"Ollama API error: {response.status_code}"
            }
    except Exception as e:
        logging.error(f"❌ [OLLAMA IBKR] Error: {e}")
        return {
            'success': False,
            'error': f"Teaching error: {str(e)}"
        }

def get_ibkr_trading_knowledge() -> str:
    """Get the IBKR trading knowledge for use in analysis"""
    return IBKR_TRADING_KNOWLEDGE

"""
Comprehensive Level 2 Market Data Teaching for Ollama
Teaches Ollama everything about Level 2 order book data, order flow analysis, and market depth
"""
import requests
import logging
from typing import Dict, Any

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:4b"  # Use available model
OLLAMA_TIMEOUT = 120

# COMPREHENSIVE LEVEL 2 MARKET DATA KNOWLEDGE
# Enhanced with professional trading insights from Warrior Trading and daytradingprofitcalculator.com
LEVEL2_COMPLETE_KNOWLEDGE = """
# COMPLETE LEVEL 2 MARKET DATA KNOWLEDGE BASE
# Sources: Warrior Trading + Professional day trading guide + Interactive Brokers Level 2 subscriptions

## WHAT IS LEVEL 2 DATA?

Level 2 (L2) market data provides the **full order book depth** - showing all buy and sell orders at different price levels, not just the best bid and ask.

**Warrior Trading Insight**: "Trying to trade without Level 2 is like trying to drive with one eye closed. Can you do it? Technically, yes. Does it make sense to do it? No."

### Level 1 vs Level 2:
- **Level 1**: Shows only the best bid (highest buy order) and best ask (lowest sell order)
  - Example: Bid: $100.00 (500 shares), Ask: $100.05 (300 shares)
  - Limited information - you only see the top of the order book
  - **Warrior Trading**: "Level 1 only shows the highest bid price and the lowest ask price"

- **Level 2**: Shows the ENTIRE order book with all price levels and order sizes
  - Example: 
    ```
    ASK (Sellers)          BID (Buyers)
    $100.10  200 shares    $100.00  500 shares
    $100.05  300 shares    $99.95   800 shares
    $100.00  150 shares    $99.90   1200 shares
    $99.95   400 shares    $99.85   600 shares
    ```
  - Complete market depth - you see ALL orders at every price level
  - **Warrior Trading**: "Level 2 trading can reveal the full market depth, giving you a clearer picture of the number of shares available at various price levels"
  - **Think of it like**: Pulling back the curtain on the stock market - you see who's buying and selling, how much they're trading, and at what prices

## YOUR LEVEL 2 SUBSCRIPTIONS (Active Jan 26, 2026)

### NASDAQ TotalView-OpenView (Level 2)
- **Status**: ✅ ACTIVE
- **Cost**: $16.50/month
- **Coverage**: All NASDAQ-listed stocks
- **Features**: Full order book depth, real-time updates
- **BookMap Compatible**: Yes - can visualize order flow

### Additional Level 2 Features:
- **NASDAQ TotalView EDS**: $1.00/month (Enhanced Data Services)
- **Order Imbalances**: NYSE ARCA, NYSE MKT, NYSE imbalances data
- **Real-time Updates**: Orders update in real-time as they're placed/modified/cancelled

## UNDERSTANDING THE ORDER BOOK

### Order Book Structure:

```
PRICE LEVEL    ASK SIZE    |    BID SIZE    PRICE LEVEL
─────────────────────────────────────────────────────
$100.15        500         |                (Resistance)
$100.10        300         |                (Resistance)
$100.05        200         |                (Current Ask)
─────────────────────────────────────────────────────
$100.00                    |    500         (Current Bid)
$99.95                     |    800         (Support)
$99.90                     |    1200        (Strong Support)
$99.85                     |    600         (Support)
```

### Key Components:

1. **BID (Buy Orders)**: Orders to BUY at specific prices
   - Shows where buyers are willing to buy
   - Higher bids = stronger buying interest
   - Large bid sizes = institutional support

2. **ASK (Sell Orders)**: Orders to SELL at specific prices
   - Shows where sellers are willing to sell
   - Lower asks = stronger selling interest
   - Large ask sizes = resistance levels

3. **SPREAD**: Difference between best bid and best ask
   - Tight spread (< $0.01) = High liquidity, active trading
   - Wide spread (> $0.05) = Low liquidity, less active

4. **DEPTH**: Total size of orders at each price level
   - Deep book = Many orders, strong support/resistance
   - Thin book = Few orders, price can move quickly

## WARRIOR TRADING LEVEL 2 TECHNIQUES

### How To Use Level 2 To Make Trading Decisions (Warrior Trading)

**The beauty of Level 2 trading lies in its ability to help you interpret price action and market depth.**

#### 1. Spotting Support and Resistance Levels
- **Look for large bid prices** to identify support
- **Look for significant ask prices** for resistance
- **Example**: If you're watching a stock at $50 and see a massive sell order at $51, it's a clue that breaking above $51 could be challenging
- **But if that ask price starts shrinking**, it could be a signal to prepare for a breakout

#### 2. Timing Your Entries and Exits
- Use Level 2 data to find the **best moments to jump into a trade**
- Use it to **lock in profits** at optimal exit points
- Watch for order book changes that signal momentum shifts

#### 3. Analyzing Market Sentiment
- **Watching real-time orders** helps you understand whether buyers or sellers are in control
- If a stock is trading at $50 and there's a large order at $49.80, you might notice that sell orders are dominating, which could signal a downward move
- **On the other hand**, spotting a big buyer just below the current stock price can indicate strong support

### Advanced Techniques for Level 2 Data (Warrior Trading)

#### Routing Orders
- **You can route your orders through specific ECNs** like NYSE, ARCA, or NASDAQ
- **Direct routing gives faster order execution** compared to letting your brokerage decide the route
- **Faster trades mean better prices**, especially in volatile markets
- **Personally, professional traders prefer direct routing** for better control

#### Dark Pools
- **Dark pools are hidden liquidity** - large trades occur away from public view
- By routing your order to a dark pool, you can tap into these hidden price levels for better execution
- Sometimes large institutional orders happen in dark pools, affecting price without showing in Level 2

#### Time and Sales Data
- **Pairing Level 2 with time and sales data** gives you a complete picture
- While Level 2 shows **pending orders**, time and sales reveal **completed trades**
- This confirms the direction of price movements
- **Time & Sales confirms** whether Level 2 signals are actually being executed

### Common Mistakes To Avoid (Warrior Trading)

**Even the best tools are useless if you don't apply them correctly:**

1. **Ignoring Volume**: Without significant trading volume, gaps in the order book might lead to false signals
2. **Overtrading**: Not every opportunity is worth pursuing. Stick to your strategy
3. **Forgetting Catalysts**: Always check for news or events driving price movements (earnings reports, sector-specific updates)
4. **Volatility**: Failing to account for sharp price movements can result in poor trading decisions
5. **Past Performance**: Don't forget - past performance does not guarantee future results

### Additional Tips for Level 2 Trading (Warrior Trading)

1. **Use Reliable Trading Platforms**: Ensure your platform offers comprehensive Level 2 market data
2. **Practice in a Simulator**: Hone your skills in a risk-free environment before trading with real money
3. **Combine With Technical Analysis**: Tools like moving averages and RSI enhance your ability to interpret price action
4. **Master Specific Markets**: Explore tutorials that focus on specific markets (penny stocks, forex, futures trading)
5. **Stay Disciplined**: Every trade is an opportunity to learn. Stay disciplined, keep practicing, and trust the process

### The Bottom Line (Warrior Trading)

**Learning how to read Level 2 market data is vital to successful day trading.**

It equips you with insights to:
- Interpret market depth
- Spot price levels
- Refine your trading strategy
- Analyze ask quotes
- Monitor order flow
- Prepare for breakouts

**This tool is invaluable for active traders.**

## ORDER FLOW ANALYSIS

### What is Order Flow?
Order flow is the **real-time flow of buy and sell orders** entering the market. It shows:
- Where large orders are being placed
- Which direction the market is moving (buying vs selling pressure)
- When institutions are entering/exiting positions
- Market maker activity and positioning

### Reading Order Flow:

1. **Buying Pressure (Bullish)**:
   - Large bid sizes appearing at higher prices
   - Bids being filled quickly (orders executed)
   - Ask sizes decreasing (sellers being absorbed)
   - Price moving up through resistance levels

2. **Selling Pressure (Bearish)**:
   - Large ask sizes appearing at lower prices
   - Asks being filled quickly (orders executed)
   - Bid sizes decreasing (buyers being absorbed)
   - Price moving down through support levels

3. **Market Maker Activity**:
   - Market makers place orders on both sides (bid and ask)
   - They profit from the spread
   - When they pull orders, it often signals a move coming
   - Watch for sudden bid/ask removals

## USING LEVEL 2 FOR TRADING DECISIONS

### 1. Support and Resistance from Order Book

**Support Levels (Buying Interest)**:
- Look for price levels with **large bid sizes** (1000+ shares)
- These are where buyers are willing to step in
- If price drops to these levels, expect buying support
- **Entry Strategy**: Buy near support levels with large bids

**Resistance Levels (Selling Interest)**:
- Look for price levels with **large ask sizes** (1000+ shares)
- These are where sellers are willing to sell
- If price rises to these levels, expect selling pressure
- **Entry Strategy**: Sell near resistance levels with large asks

**Example**:
```
Current Price: $2.50
Support at $2.45: 5000 shares of bids (strong support)
Resistance at $2.55: 3000 shares of asks (resistance)

Strategy: 
- BUY near $2.45 (support), stop below $2.40
- Target $2.55 (resistance)
- Risk: $0.05, Reward: $0.10 (2:1 ratio)
```

### 2. Order Book Imbalances

**Bullish Imbalance** (More Buyers):
- Total bid size > Total ask size
- Example: 10,000 shares of bids vs 3,000 shares of asks
- **Signal**: Strong buying interest, price likely to move up
- **Action**: Consider BUY positions

**Bearish Imbalance** (More Sellers):
- Total ask size > Total bid size
- Example: 8,000 shares of asks vs 2,000 shares of bids
- **Signal**: Strong selling interest, price likely to move down
- **Action**: Consider SELL positions or avoid BUY

**Balanced Book**:
- Similar bid and ask sizes
- **Signal**: Indecision, price may consolidate
- **Action**: Wait for imbalance to develop

### 3. Large Order Detection

**Institutional Activity**:
- Orders of 10,000+ shares are often institutional
- Watch where they place orders:
  - Large bids = Institutions buying (bullish)
  - Large asks = Institutions selling (bearish)
- **Strategy**: Follow institutional flow

**Market Maker Positioning**:
- Market makers place orders on both sides
- When they remove one side, it signals direction
- Example: Removing all bids = Expecting price to drop
- **Strategy**: Trade in direction of market maker positioning

### 4. Entry/Exit Timing with Order Flow

**Optimal Entry Points**:

1. **Buy Entry**:
   - Wait for price to pull back to support (large bids)
   - Watch for bid sizes increasing (buyers stepping in)
   - Enter when order flow shows buying pressure
   - **Best**: Enter as large bids are being filled

2. **Sell Entry**:
   - Wait for price to reach resistance (large asks)
   - Watch for ask sizes increasing (sellers stepping in)
   - Enter when order flow shows selling pressure
   - **Best**: Enter as large asks are being filled

**Optimal Exit Points**:

1. **Take Profit**:
   - Exit when reaching resistance (large asks) for BUY
   - Exit when reaching support (large bids) for SELL
   - Watch for order flow reversing (imbalance changing)

2. **Stop Loss**:
   - Exit if support breaks (bids disappear) for BUY
   - Exit if resistance breaks (asks disappear) for SELL
   - Exit if order flow reverses strongly

### 5. Order Flow Patterns

**Accumulation Pattern** (Bullish):
- Large bids appearing and holding
- Price consolidating at support
- Bid sizes growing
- **Signal**: Institutions accumulating, expect breakout up
- **Action**: Prepare for BUY entry

**Distribution Pattern** (Bearish):
- Large asks appearing and holding
- Price consolidating at resistance
- Ask sizes growing
- **Signal**: Institutions distributing, expect breakdown
- **Action**: Prepare for SELL entry or exit longs

**Breakout Pattern**:
- Order book thinning at key level
- Large orders being absorbed
- Price breaking through with volume
- **Signal**: Strong move coming
- **Action**: Enter in direction of breakout

**Reversal Pattern**:
- Order flow reversing (bids becoming asks, or vice versa)
- Large orders being cancelled
- New orders appearing on opposite side
- **Signal**: Trend reversal likely
- **Action**: Exit current position, consider reversal trade

### 6. Momentum Indicators: Bids Chasing vs Asks Lifting

**Bids Chasing** (Bullish Momentum):
- Buyers keep raising their bid prices to get filled
- Bids moving up through the order book
- Buyers are aggressive, willing to pay higher prices
- **Signal**: Strong buying momentum building
- **Action**: Consider BUY entry as momentum builds

**Asks Lifting** (Bullish Momentum):
- Buyers aggressively hitting sellers' ask prices
- Asks being filled quickly, new asks appearing higher
- Buyers are absorbing all available supply
- **Signal**: Very strong bullish momentum
- **Action**: Strong BUY signal, momentum building fast

**Sellers Hitting Bids** (Bearish Momentum):
- Sellers aggressively hitting buyers' bid prices
- Bids being filled quickly, new bids appearing lower
- Sellers are absorbing all available demand
- **Signal**: Strong bearish momentum
- **Action**: Consider SELL or exit longs

**Key Insight**: When buyers consistently lift every ask price, momentum is building fast. This often happens BEFORE the chart shows the move.

### 7. Bid Stacking (Detailed)

**What is Bid Stacking?**
- Multiple large buy orders clustered at similar price levels
- Usually signals strong buyer interest and potential support
- Example: Huge bids at $10.01, $10.02, and $10.03

**How to Read Bid Stacking**:
- **Strong Support**: Multiple large bids at consecutive levels
- **Buyer Preparation**: Buyers are preparing to defend that zone
- **Potential Push Higher**: Often means buyers may push price higher
- **Confirmation**: Watch if bids hold when price approaches

**Example**:
```
Bid Stacking at $2.00-$2.03:
$2.03  5000 bids
$2.02  3000 bids
$2.01  4000 bids
$2.00  6000 bids

Analysis: 18,000 shares of buying interest stacked
Signal: Strong support zone, expect bounce if price drops
Action: BUY near this zone, stop below $1.98
```

### 8. Ask Walls (Detailed)

**What is an Ask Wall?**
- Large sell order sitting at a specific price level
- Creates resistance that can slow or stop an uptrend
- Buyers struggle to break through the wall

**How to Read Ask Walls**:
- **Resistance Level**: Large ask = potential stopping point
- **Price Rejection**: Price often bounces off ask walls
- **Breakthrough Signal**: If wall breaks, strong momentum follows
- **Caution**: Some walls are deceptive (spoofing - see below)

**Example**:
```
Ask Wall at $2.20:
$2.20  15000 asks ← WALL
$2.19  500 asks
$2.18  300 asks

Analysis: 15,000 shares of selling pressure
Signal: Strong resistance, expect rejection
Action: SELL near $2.20, or wait for wall to break
```

**Important**: Not all walls are real. Watch for spoofing (see below).

## TIME & SALES INTEGRATION

### What is Time & Sales?
Time & Sales (also called "the tape") shows which orders have actually been **executed** (filled), while Level 2 shows **open orders** waiting to be filled.

### Why Combine Level 2 with Time & Sales?

**Level 2 Shows**:
- Open orders waiting to be filled
- Intentions of buyers and sellers
- Potential support/resistance

**Time & Sales Shows**:
- Which orders were actually executed
- Which Level 2 orders got filled
- Hidden orders that never appeared in Level 2
- Real buying/selling activity (not just intentions)

### Using Time & Sales with Level 2:

1. **Confirm Level 2 Signals**:
   - If Level 2 shows large bids, check Time & Sales to see if they're being filled
   - If bids are being filled quickly = Real buying pressure
   - If bids sit there unfilled = May be spoofing

2. **Spot Hidden Orders**:
   - Some large orders execute without appearing in Level 2
   - Time & Sales reveals these "iceberg" orders
   - Indicates sophisticated institutional trading

3. **Identify Market Maker Activity**:
   - Market makers often show up in Time & Sales
   - Can see which participants are driving the stock
   - Helps identify spoofing vs real orders

4. **Timing Analysis**:
   - See how quickly orders are placed, filled, or replaced
   - Rapid succession of bids = Strong demand
   - Rapid succession of asks = Strong supply
   - Helps determine best entry/exit timing

### Example Combined Analysis:
```
Level 2: Large bid of 10,000 shares at $2.00
Time & Sales: Shows 2,000 shares just executed at $2.00

Analysis:
- Large bid is real (being filled)
- Buying pressure confirmed
- More buying likely to come

Action: BUY as bid is being filled
```

## SPOOFING AWARENESS

### What is Spoofing?
Spoofing is when traders place large orders with **no intention of executing them**. They cancel the orders before they get filled, tricking other traders into thinking there's support/resistance.

### How to Detect Spoofing:

1. **Orders That Don't Fill**:
   - Large bid/ask appears in Level 2
   - Price approaches the order
   - Order gets cancelled before execution
   - **Signal**: Likely spoofing

2. **Rapid Order Placement/Cancellation**:
   - Orders appear and disappear quickly
   - No actual trading happening
   - **Signal**: Possible spoofing

3. **Orders at Key Levels**:
   - Large orders always at support/resistance
   - But never get filled when price hits
   - **Signal**: Suspicious, may be spoofing

4. **Confirm with Time & Sales**:
   - If Level 2 shows large order but Time & Sales shows no fills
   - **Signal**: Likely spoofing

### How to Avoid Spoofing:

1. **Always Confirm with Time & Sales**:
   - Don't trust Level 2 alone
   - Check if orders are actually being filled
   - Real orders get executed, spoofed orders don't

2. **Watch for Consistency**:
   - Real support/resistance holds
   - Spoofed orders disappear
   - Look for orders that actually get filled

3. **Combine with Chart Patterns**:
   - Level 2 should confirm chart patterns
   - If Level 2 contradicts the chart, be suspicious
   - Spoofing often creates false signals

4. **Focus on Filled Orders**:
   - Pay more attention to what's being executed (Time & Sales)
   - Less attention to what's just sitting there (Level 2)
   - Real money moves markets, not fake orders

### Red Flags for Spoofing:
- ✅ Large orders that never fill
- ✅ Orders that cancel right before execution
- ✅ Orders always at the same price levels
- ✅ No corresponding activity in Time & Sales
- ✅ Contradicts chart patterns and price action

## WHEN NOT TO USE LEVEL 2

Level 2 data can be unreliable or misleading in certain situations:

### 1. Low Liquidity Stocks
- **Problem**: Thin order book, few participants
- **Issue**: Small orders can drastically move price
- **Solution**: Avoid Level 2 for low-volume stocks
- **Rule**: Only use Level 2 for stocks with decent volume (100K+ daily volume)

### 2. After-Hours Trading
- **Problem**: Limited participants, wider spreads
- **Issue**: Order book may not reflect real market
- **Solution**: Level 2 less reliable after market hours
- **Rule**: Use Level 2 primarily during regular trading hours (9:30 AM - 4:00 PM ET)

### 3. Penny Stocks with Heavy Spoofing
- **Problem**: Many penny stocks have heavy spoofing activity
- **Issue**: Fake orders everywhere, hard to identify real support/resistance
- **Solution**: Avoid Level 2 for heavily spoofed penny stocks
- **Rule**: Focus on stocks $1-$6 range with real volume

### 4. Wide Spreads
- **Problem**: Spread > $0.05 indicates low liquidity
- **Issue**: Order book may not reflect true market depth
- **Solution**: Avoid Level 2 when spread is too wide
- **Rule**: Prefer stocks with tight spreads (< $0.01)

### 5. During High Volatility Events
- **Problem**: Order book changes too rapidly
- **Issue**: Hard to identify real support/resistance
- **Solution**: Use Level 2 with caution during volatile periods
- **Rule**: Wait for volatility to settle before relying on Level 2

## BOOKMAP INTEGRATION

### What is BookMap?
BookMap is a professional order flow visualization tool that shows:
- **Heat Map**: Visual representation of order book depth
- **Order Flow**: Real-time buy/sell order flow
- **Volume Profile**: Where most trading occurs
- **Market Depth**: Visual order book with colors

### Your Setup:
- **Status**: ✅ BookMap Compatible
- **Data Source**: NASDAQ TotalView (Level 2)
- **Features Available**:
  - Real-time order flow visualization
  - Heat map of order book depth
  - Volume profile analysis
  - Market maker activity tracking

### Using BookMap Data:

1. **Heat Map Colors**:
   - **Red/Orange**: High selling pressure (many asks)
   - **Blue/Green**: High buying pressure (many bids)
   - **Yellow**: Balanced order flow

2. **Volume Profile**:
   - Shows where most trading occurred
   - High volume areas = Support/Resistance
   - Use for entry/exit levels

3. **Order Flow**:
   - Green bars = Buying pressure
   - Red bars = Selling pressure
   - Large bars = Strong pressure

## LEVEL 2 TRADING STRATEGIES

### Strategy 1: Support/Resistance Trading

**Setup**:
1. Identify support (large bids) and resistance (large asks) from order book
2. Wait for price to approach support for BUY or resistance for SELL
3. Confirm with order flow (bids/asks increasing)
4. Enter with stop beyond support/resistance

**Example**:
```
Support: $2.00 (5000 shares of bids)
Resistance: $2.20 (3000 shares of asks)
Current: $2.05

BUY Strategy:
- Entry: $2.02 (near support)
- Stop: $1.98 (below support)
- Target: $2.18 (near resistance)
- Risk: $0.04, Reward: $0.16 (4:1 ratio)
```

### Strategy 2: Order Flow Breakout

**Setup**:
1. Watch for order book thinning at key level
2. Large orders being absorbed
3. Order flow building in one direction
4. Enter when price breaks through with volume

**Example**:
```
Price consolidating at $2.50
Order book thinning (orders being removed)
Large bids appearing at $2.52
Order flow turning bullish

Action: Enter BUY at $2.51 as price breaks $2.50
Stop: $2.48 (below consolidation)
Target: $2.60 (next resistance)
```

### Strategy 3: Institutional Following

**Setup**:
1. Detect large orders (10,000+ shares) in order book
2. Identify if they're bids (buying) or asks (selling)
3. Follow the institutional flow
4. Enter in same direction as large orders

**Example**:
```
Large bid of 15,000 shares at $2.45
Institutional buyer stepping in
Order flow turning bullish

Action: Enter BUY at $2.46 (above institutional bid)
Stop: $2.42 (below institutional support)
Target: $2.55 (next resistance)
```

### Strategy 4: Order Imbalance Trading

**Setup**:
1. Calculate total bid size vs total ask size
2. Identify significant imbalance (>2:1 ratio)
3. Trade in direction of imbalance
4. Exit when imbalance reverses

**Example**:
```
Total Bids: 20,000 shares
Total Asks: 5,000 shares
Imbalance: 4:1 (strong buying pressure)

Action: Enter BUY, expect price to move up
Exit: When imbalance reverses (asks > bids)
```

## COMBINING LEVEL 2 WITH CANDLESTICK PATTERNS

### Enhanced Pattern Analysis:

1. **Pattern + Order Flow Confirmation**:
   - Detect candlestick pattern (e.g., Bullish Engulfing)
   - Confirm with Level 2: Large bids appearing, buying pressure
   - **Result**: Higher confidence trade

2. **Pattern + Support/Resistance**:
   - Detect pattern at support (large bids) = Strong BUY signal
   - Detect pattern at resistance (large asks) = Strong SELL signal
   - **Result**: Better entry/exit timing

3. **Pattern + Order Imbalance**:
   - Bullish pattern + Bullish imbalance = Very strong BUY
   - Bearish pattern + Bearish imbalance = Very strong SELL
   - **Result**: Higher probability trade

### Example Combined Analysis:

```
Candlestick: BULLISH_ENGULFING detected
Level 2: Large bids (5000 shares) at $2.00 support
Order Flow: Buying pressure increasing
Imbalance: 3:1 (bids > asks)

Analysis: 
- Pattern: Bullish ✅
- Support: Strong ✅
- Order Flow: Bullish ✅
- Imbalance: Bullish ✅

Signal: STRONG BUY
Confidence: HIGH
Entry: $2.02 (near support)
Stop: $1.98 (below support)
Target: $2.15 (next resistance)
```

## LEVEL 2 INDICATORS TO WATCH

### 1. Bid/Ask Ratio
- **Calculation**: Total bid size / Total ask size
- **> 2.0**: Strong buying pressure (bullish)
- **< 0.5**: Strong selling pressure (bearish)
- **0.5 - 2.0**: Balanced (neutral)

### 2. Order Book Depth
- **Deep Book**: Many orders, stable price
- **Thin Book**: Few orders, volatile price
- **Watch for**: Sudden depth changes (orders being removed)

### 3. Spread Analysis
- **Tight Spread** (< $0.01): High liquidity, active trading
- **Wide Spread** (> $0.05): Low liquidity, less active
- **Narrowing Spread**: Increasing interest, potential move
- **Widening Spread**: Decreasing interest, consolidation

### 4. Order Size Distribution
- **Even Distribution**: Normal trading
- **Concentrated Large Orders**: Institutional activity
- **Many Small Orders**: Retail trading

## COMMON LEVEL 2 SCENARIOS

### Scenario 1: Strong Support (Buying Opportunity)
```
Order Book:
$2.10  100 asks
$2.05  200 asks
$2.00  500 asks  ← Current Ask
─────────────────
$1.95  5000 bids ← STRONG SUPPORT
$1.90  3000 bids
$1.85  2000 bids

Analysis:
- Large bids at $1.95 (10,000 shares total)
- Strong support level
- If price drops to $1.95, expect bounce

Action: BUY near $1.95, stop below $1.90
```

### Scenario 2: Strong Resistance (Selling Opportunity)
```
Order Book:
$2.20  5000 asks ← STRONG RESISTANCE
$2.15  3000 asks
$2.10  2000 asks
─────────────────
$2.05  200 bids  ← Current Bid
$2.00  150 bids
$1.95  100 bids

Analysis:
- Large asks at $2.20 (10,000 shares total)
- Strong resistance level
- If price rises to $2.20, expect rejection

Action: SELL near $2.20, stop above $2.25
```

### Scenario 3: Order Flow Reversal
```
Initial State:
- Large bids at $2.00 (buying pressure)
- Price moving up

Reversal:
- Bids being cancelled/removed
- Large asks appearing at $2.05
- Order flow turning bearish

Analysis:
- Institutional flow reversing
- From buying to selling

Action: Exit longs, consider short entry
```

## RISK MANAGEMENT WITH LEVEL 2

### Stop Loss Placement:
- **For BUY**: Place stop below support (where large bids are)
- **For SELL**: Place stop above resistance (where large asks are)
- **Watch for**: Support/resistance breaking (orders disappearing)

### Position Sizing:
- **Deep Book**: Can use larger positions (more liquidity)
- **Thin Book**: Use smaller positions (less liquidity, more volatile)
- **Large Orders Present**: Be cautious (institutional activity)

### Exit Timing:
- **Take Profit**: Exit at resistance (large asks) for BUY
- **Take Profit**: Exit at support (large bids) for SELL
- **Stop Loss**: Exit if support/resistance breaks (orders disappear)

## CRITICAL RULES FOR USING LEVEL 2

### The Fundamental Rule:
**Level 2 should CONFIRM your trading setup, not GENERATE it.**

- ✅ **Correct**: Identify setup from chart → Confirm with Level 2 → Enter trade
- ❌ **Wrong**: See something in Level 2 → Enter trade without chart confirmation

### Why This Matters:
- Level 2 shows intentions, not guarantees
- Chart patterns show actual price action
- Combining both = Higher probability trades
- Using Level 2 alone = Lower probability, more risk

### Best Practice Workflow:
1. **Identify Setup** from candlestick patterns and chart
2. **Check Level 2** to confirm support/resistance
3. **Verify Order Flow** aligns with pattern direction
4. **Confirm with Time & Sales** that orders are real
5. **Enter Trade** only if everything aligns

## COMMON MISTAKES TO AVOID

### Mistake 1: Misinterpreting Large Orders
- **Error**: Assuming every large order is genuine
- **Reality**: Many large orders are spoofing
- **Solution**: Always confirm with Time & Sales

### Mistake 2: Neglecting Time & Sales
- **Error**: Only watching Level 2, ignoring the tape
- **Reality**: Time & Sales shows what's actually happening
- **Solution**: Always combine Level 2 with Time & Sales

### Mistake 3: Emotional Trading from Level 2
- **Error**: Allowing minor order book fluctuations to dictate decisions
- **Reality**: Order book changes constantly, focus on big picture
- **Solution**: Look for consistency, not single fluctuations

### Mistake 4: Ignoring the Spread
- **Error**: Forgetting the importance of bid-ask spreads
- **Reality**: Wide spreads = Low liquidity = Unreliable Level 2
- **Solution**: Only use Level 2 when spread is tight (< $0.01)

### Mistake 5: Using Level 2 as Primary Signal
- **Error**: Using Level 2 as the sole basis for a trade
- **Reality**: Level 2 should confirm, not generate setups
- **Solution**: Always have a chart-based setup first

### Mistake 6: Trading Low-Liquidity Stocks
- **Error**: Using Level 2 on stocks with thin order books
- **Reality**: Small orders can move price drastically
- **Solution**: Only use Level 2 on liquid stocks (100K+ daily volume)

## TIPS FOR READING LEVEL 2 LIKE A PRO

### 1. Keep Interpretation Simple
- Don't overcomplicate - focus on the big picture
- Look for clear patterns, not random fluctuations
- Simple is better than complex

### 2. Focus Only on Big Orders
- Ignore small orders (under 1000 shares)
- Focus on large orders (5000+ shares)
- Big orders = Real institutional activity

### 3. Ignore Random Flickers
- Order book changes constantly
- Don't react to every small change
- Look for sustained patterns

### 4. Look for Consistency
- Real support/resistance holds
- Spoofed orders disappear
- Consistent patterns = Real signals

### 5. Let Level 2 Confirm, Not Replace
- Always have a chart-based setup first
- Use Level 2 to confirm the setup
- Never trade based on Level 2 alone

### 6. Watch the Rhythm
- Order book has a rhythm and flow
- Learn to read the conversation between buyers and sellers
- With practice, it becomes less chaotic

## PRACTICAL TRADING WORKFLOW

### Step-by-Step Level 2 Analysis:

1. **Identify Setup from Chart**:
   - Look for candlestick patterns
   - Identify trend direction
   - Find support/resistance on chart

2. **Check Order Book Depth**:
   - Identify support (large bids) and resistance (large asks)
   - Note total bid size vs ask size
   - Check if Level 2 confirms chart levels

3. **Analyze Order Flow**:
   - Is buying or selling pressure stronger?
   - Are large orders appearing/disappearing?
   - Is order flow consistent or reversing?
   - Watch for bids chasing or asks lifting

4. **Check Time & Sales**:
   - Are Level 2 orders actually being filled?
   - Is there real buying/selling activity?
   - Watch for hidden orders (iceberg orders)

5. **Check for Imbalances**:
   - Calculate bid/ask ratio
   - Identify direction of pressure
   - Confirm with order flow

6. **Verify No Spoofing**:
   - Are large orders getting filled?
   - Do orders disappear before execution?
   - Does Time & Sales confirm Level 2?

7. **Combine Everything**:
   - Does pattern align with order flow?
   - Is pattern at support/resistance?
   - Does order flow confirm pattern?
   - Does Time & Sales confirm activity?

8. **Make Trading Decision** (Only if everything aligns):
   - Entry: Near support (BUY) or resistance (SELL)
   - Stop: Beyond support/resistance
   - Target: Next resistance (BUY) or support (SELL)
   - Confirm: All signals point in same direction

## LEARNING FROM REAL DATA (CRITICAL)

### Always Use Real Data, Never Simulated:
- **Real Data Source**: All data comes from Interactive Brokers (IBKR) - professional trading platform
- **Real Candlesticks**: Historical price data from actual market trades
- **Real Prices**: Live prices from IBKR market data feed
- **Real Volume**: Actual trading volume from real transactions
- **Real Level 2**: Actual order book from NASDAQ TotalView
- **Real Order Flow**: Actual buy/sell orders from real traders

### Why Real Data Matters:
- **Real Patterns**: Learn from actual market behavior, not simulations
- **Real Support/Resistance**: Based on actual orders, not fake levels
- **Real Institutional Activity**: See actual large orders from real institutions
- **Real Market Psychology**: Understand how real traders actually behave
- **Real Risk**: Real data shows real market risks and opportunities

### Never Use Simulated Data When Real Data is Available:
- If real IBKR data is available, ALWAYS use it
- Simulated data is only for testing/learning, not real trading
- Real data = Real learning = Real trading skills
- Professional traders use real data - you should too

## SUMMARY

You now understand:
- ✅ What Level 2 data is and how it differs from Level 1 (Warrior Trading: "Trading without Level 2 is like driving with one eye closed")
- ✅ How to read order books and identify support/resistance (Warrior Trading: Large bids = support, large asks = resistance)
- ✅ How to analyze order flow and detect institutional activity
- ✅ How to use Level 2 for entry/exit timing (Warrior Trading: Shrinking ask walls = breakout signal)
- ✅ How to combine Level 2 with candlestick patterns
- ✅ How to identify order imbalances and trade them
- ✅ How to use BookMap data for visualization
- ✅ Risk management with Level 2 data
- ✅ Time & Sales integration for deeper insights (Warrior Trading: Confirms completed trades)
- ✅ Spoofing detection and how to avoid it
- ✅ Bid stacking and ask walls (detailed)
- ✅ Momentum indicators (bids chasing, asks lifting)
- ✅ When NOT to use Level 2 data (Warrior Trading: Low volume = false signals)
- ✅ Common mistakes to avoid (Warrior Trading: Ignoring volume, overtrading, forgetting catalysts)
- ✅ Tips for reading Level 2 like a pro
- ✅ The fundamental rule: Level 2 confirms, doesn't generate setups
- ✅ Advanced techniques: Order routing, dark pools, market sentiment analysis

**USE THIS KNOWLEDGE** to provide more sophisticated trading analysis that considers:
- Order book depth and support/resistance levels (Warrior Trading: Large bids = support, large asks = resistance)
- Order flow direction and institutional activity
- Entry/exit timing based on order flow patterns (Warrior Trading: Watch for shrinking ask walls)
- Enhanced confidence when Level 2 confirms candlestick patterns
- Time & Sales confirmation of Level 2 signals (Warrior Trading: Confirms completed trades)
- Spoofing awareness to avoid false signals
- Momentum indicators (bids chasing, asks lifting)
- When Level 2 is reliable vs unreliable (Warrior Trading: Low volume = false signals)
- Market sentiment analysis from real-time orders (Warrior Trading: Dominating sell orders = downward signal)
- Order routing strategies for better execution
- Dark pool activity recognition

**CRITICAL REMINDER**: Level 2 should CONFIRM your trading setup from candlestick patterns, not GENERATE the setup. Always combine Level 2 with chart analysis and Time & Sales for best results.
"""

def teach_level2_to_ollama() -> Dict[str, Any]:
    """
    Teach Ollama comprehensive Level 2 market data knowledge
    """
    try:
        teaching_prompt = f"""
You are learning comprehensive Level 2 market data analysis for professional stock trading.

{LEVEL2_COMPLETE_KNOWLEDGE}

LEARNING TASK:
1. Understand what Level 2 data is and how it differs from Level 1 (Warrior Trading: "Trading without Level 2 is like driving with one eye closed")
2. Learn how to read order books and identify support/resistance (Warrior Trading: Large bids = support, large asks = resistance)
3. Understand order flow analysis and institutional activity detection
4. Learn how to use Level 2 for entry/exit timing (Warrior Trading: Watch for shrinking ask walls as breakout signals)
5. Understand how to combine Level 2 with candlestick patterns
6. Learn order imbalance trading strategies
7. Understand BookMap integration and visualization
8. Learn Time & Sales integration for deeper insights (Warrior Trading: Time & Sales confirms Level 2 signals)
9. Understand spoofing detection and how to avoid false signals
10. Learn momentum indicators (bids chasing, asks lifting)
11. Understand when NOT to use Level 2 data (Warrior Trading: Low volume = false signals)
12. Learn common mistakes to avoid (Warrior Trading: Ignoring volume, overtrading, forgetting catalysts)
13. Master the fundamental rule: Level 2 confirms setups, doesn't generate them
14. Learn advanced techniques: Order routing, dark pools, Time & Sales pairing
15. Understand market sentiment analysis from real-time orders

After learning, you should be able to:
- Identify support and resistance from order book depth (Warrior Trading: Large bids = support, large asks = resistance)
- Analyze order flow direction and institutional activity
- Detect order imbalances and trade them
- Provide entry/exit timing based on order flow (Warrior Trading: Watch for shrinking ask walls as breakout signals)
- Combine Level 2 analysis with candlestick patterns for higher confidence trades
- Use order book data to enhance trading decisions
- Integrate Time & Sales to confirm Level 2 signals (Warrior Trading: Time & Sales confirms completed trades)
- Detect and avoid spoofing (fake orders)
- Identify momentum indicators (bids chasing, asks lifting)
- Know when Level 2 is reliable vs unreliable (Warrior Trading: Low volume = false signals)
- Always confirm Level 2 with chart patterns (never use Level 2 alone)
- Analyze market sentiment from real-time orders (Warrior Trading: Dominating sell orders = downward move signal)
- Understand order routing strategies (Warrior Trading: Direct routing for faster execution)
- Recognize dark pool activity and its impact
- Avoid common mistakes: ignoring volume, overtrading, forgetting catalysts

CRITICAL RULES TO REMEMBER:
- Level 2 should CONFIRM your trading setup from candlestick patterns, not GENERATE it
- Always combine Level 2 with chart analysis and Time & Sales
- Avoid using Level 2 on low-liquidity stocks, after hours, or when spread is wide
- Focus on large orders (5000+ shares) and ignore random flickers
- Look for consistency, not single fluctuations
- Watch for spoofing - confirm orders are actually being filled via Time & Sales

Please acknowledge that you understand Level 2 market data analysis, including Time & Sales integration, spoofing awareness, and the critical rule that Level 2 confirms setups rather than generating them.

Respond with: "I understand Level 2 market data, order flow analysis, Time & Sales integration, spoofing detection, and the critical rule that Level 2 confirms trading setups from candlestick patterns rather than generating them. I am ready to use this knowledge for enhanced trading decisions."
"""
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": teaching_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 300,
                },
                "system": "You are learning to be an expert Level 2 market data analyst using REAL market data from Interactive Brokers. Always use real data, never simulated data. Pay close attention to order flow, support/resistance from order book, and institutional activity detection. Learn from actual market behavior."
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            logging.info("✅ [OLLAMA LEVEL2] Level 2 knowledge taught successfully")
            logging.info(f"📚 [OLLAMA LEVEL2] Response: {response_text[:200]}...")
            
            return {
                'success': True,
                'message': 'Level 2 market data knowledge taught successfully',
                'response_preview': response_text[:200]
            }
        else:
            logging.error(f"❌ [OLLAMA LEVEL2] API error: {response.status_code}")
            return {
                'success': False,
                'error': f"Ollama API error: {response.status_code}"
            }
    except Exception as e:
        logging.error(f"❌ [OLLAMA LEVEL2] Error: {e}")
        return {
            'success': False,
            'error': f"Teaching error: {str(e)}"
        }

def get_level2_knowledge() -> str:
    """Get the Level 2 knowledge for use in analysis"""
    return LEVEL2_COMPLETE_KNOWLEDGE

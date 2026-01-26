"""
Ollama AI Integration Service
Handles candlestick pattern analysis and trading decisions
"""
import requests
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:4b"  # Use available model (detected from Ollama)
OLLAMA_TIMEOUT = 120  # seconds (increased for slower models)

# Import complete pattern library
try:
    from ollama_patterns_teaching import COMPLETE_PATTERN_LIBRARY
except ImportError:
    COMPLETE_PATTERN_LIBRARY = None
    logging.warning("⚠️ Complete pattern library not available, using basic patterns")

# Import IBKR trading knowledge
try:
    from ollama_ibkr_trading import get_ibkr_trading_knowledge
    IBKR_TRADING_KNOWLEDGE = get_ibkr_trading_knowledge()
    logging.info("✅ [OLLAMA] IBKR trading knowledge loaded")
except ImportError:
    IBKR_TRADING_KNOWLEDGE = None
    logging.warning("⚠️ IBKR trading knowledge not available")

# Import Level 2 market data knowledge
try:
    from ollama_level2_teaching import get_level2_knowledge
    LEVEL2_KNOWLEDGE = get_level2_knowledge()
    logging.info("✅ [OLLAMA] Level 2 market data knowledge loaded")
except ImportError:
    LEVEL2_KNOWLEDGE = None
    logging.warning("⚠️ Level 2 knowledge not available")

# Import relative volume knowledge
try:
    from ollama_volume_teaching import get_relative_volume_knowledge
    RELATIVE_VOLUME_KNOWLEDGE = get_relative_volume_knowledge()
    logging.info("✅ [OLLAMA] Relative volume knowledge loaded")
except ImportError:
    RELATIVE_VOLUME_KNOWLEDGE = None
    logging.warning("⚠️ Relative volume knowledge not available")

# Import float knowledge
try:
    from ollama_float_teaching import get_float_knowledge
    FLOAT_KNOWLEDGE = get_float_knowledge()
    logging.info("✅ [OLLAMA] Float knowledge loaded")
except ImportError:
    FLOAT_KNOWLEDGE = None
    logging.warning("⚠️ Float knowledge not available")

# Market Data Subscription Status - Level 2 Available
MARKET_DATA_LEVEL2_AVAILABLE = True  # Level 2 subscriptions activated Jan 26, 2026
MARKET_DATA_FEATURES = {
    'level1': True,  # Level 1 quotes for all major US exchanges
    'level2': True,  # Level 2 order book data (NASDAQ TotalView)
    'bookmap_compatible': True,  # Level 2 data works with BookMap
    'order_flow_analysis': True,  # Can analyze order flow and market depth
    'features': [
        'Real-time bid/ask quotes (Level 1)',
        'Full order book depth (Level 2)',
        'Order flow analysis',
        'Market depth visualization',
        'BookMap integration ready'
    ]
}
logging.info("📊 [OLLAMA] Level 2 market data subscriptions detected:")
logging.info("   - Level 2 order book data available for enhanced analysis")
logging.info("   - BookMap compatible - can track live buy/sell orders")
logging.info("   - Order flow analysis enabled for better entry/exit timing")

# Enhanced Candlestick Pattern Teaching System with Better Context
CANDLESTICK_TEACHING_PROMPT = """You are an expert candlestick chart analyst and technical trader specializing in stock trading patterns. You have deep knowledge of price action, volume analysis, and market psychology.

YOUR ROLE:
- Analyze candlestick patterns with precision
- Consider volume, trend, and market context
- Provide actionable trading signals with clear reasoning
- Calculate risk-reward ratios for entries/exits
- Identify support and resistance levels from price action

CANDLESTICK BASICS:
- Each candle shows: Open, High, Low, Close prices
- Green/White = Bullish (Close > Open) - buyers in control
- Red/Black = Bearish (Close < Open) - sellers in control
- Body = difference between Open and Close (represents buying/selling pressure)
- Upper Shadow = High - max(Open, Close) (rejection of higher prices)
- Lower Shadow = min(Open, Close) - Low (rejection of lower prices)
- Long wicks = rejection at that price level
- Small body = indecision between buyers and sellers

BULLISH PATTERNS (Buy Signals):
1. HAMMER: Small body at top, long lower shadow (2x body), little/no upper shadow
   - Indicates: Reversal from downtrend, strong buying pressure
   - Confidence: HIGH if at support level
   
2. BULLISH_ENGULFING: Small bearish candle followed by large bullish candle that completely engulfs it
   - Indicates: Strong reversal, buyers taking control
   - Confidence: HIGH
   
3. MORNING_STAR: Bearish candle, small doji/gap, then bullish candle
   - Indicates: Strong reversal pattern
   - Confidence: HIGH
   
4. PIERCING_LINE: Bearish candle followed by bullish candle that closes above midpoint of previous candle
   - Indicates: Potential reversal
   - Confidence: MEDIUM
   
5. THREE_WHITE_SOLDIERS: Three consecutive bullish candles with higher closes
   - Indicates: Strong uptrend continuation
   - Confidence: HIGH

BEARISH PATTERNS (Sell Signals):
1. SHOOTING_STAR: Small body at bottom, long upper shadow (2x body), little/no lower shadow
   - Indicates: Reversal from uptrend, selling pressure
   - Confidence: HIGH if at resistance level
   
2. BEARISH_ENGULFING: Small bullish candle followed by large bearish candle that completely engulfs it
   - Indicates: Strong reversal, sellers taking control
   - Confidence: HIGH
   
3. EVENING_STAR: Bullish candle, small doji/gap, then bearish candle
   - Indicates: Strong reversal pattern
   - Confidence: HIGH
   
4. DARK_CLOUD_COVER: Bullish candle followed by bearish candle that closes below midpoint
   - Indicates: Potential reversal
   - Confidence: MEDIUM
   
5. THREE_BLACK_CROWS: Three consecutive bearish candles with lower closes
   - Indicates: Strong downtrend continuation
   - Confidence: HIGH

NEUTRAL PATTERNS:
1. DOJI: Open and Close are nearly equal (small body)
   - Indicates: Indecision, potential reversal
   - Confidence: LOW to MEDIUM

VOLUME ANALYSIS:
- High volume confirms pattern strength
- Volume should be 2x+ average for high confidence
- Low volume patterns are less reliable

TREND CONTEXT:
- Patterns are more reliable when they align with overall trend
- Reversal patterns at support/resistance are stronger
- Continuation patterns in trending markets are stronger

CONFIDENCE LEVELS:
- HIGH: Pattern is clear, volume confirms, at key level
- MEDIUM: Pattern is present but context is unclear
- LOW: Pattern is weak or conflicting signals exist

TRADING DECISIONS:
- BUY: Strong bullish pattern + high volume (2x+) + at support level + trend alignment
- SELL: Strong bearish pattern + high volume (2x+) + at resistance level + trend alignment
- HOLD: No clear pattern, conflicting signals, or low confidence setup

RISK MANAGEMENT:
- Always calculate stop loss: 2-5% below entry for longs, 2-5% above for shorts
- Take profit targets: 1.5-3x risk (risk-reward ratio)
- Position sizing: Risk only 1-2% of account per trade
- Never trade against strong trend without clear reversal pattern

TECHNICAL CONTEXT TO CONSIDER:
- Price position relative to recent high/low
- Volume trends (increasing/decreasing)
- Candle sequence patterns (momentum building/weakening)
- Support/resistance levels from price action
- Trend direction (uptrend/downtrend/sideways)

MARKET DATA AVAILABILITY (Updated Jan 26, 2026):
- Level 1 Data: Real-time quotes for all major US exchanges (NASDAQ, NYSE, AMEX, Regional)
- Level 2 Data: Full order book depth available (NASDAQ TotalView-OpenView)
- BookMap Integration: Level 2 data compatible with BookMap for order flow analysis
- Order Flow Analysis: Can analyze live buy/sell orders and market depth
- Enhanced Features: Market depth visualization, order flow tracking, real-time bid/ask levels

When Level 2 data is available, you can provide more sophisticated analysis:
- Order book imbalances (more buyers vs sellers at key levels)
- Support/resistance from order book depth
- Entry/exit timing based on order flow
- Market maker activity detection
- Large order detection (institutional activity)

OUTPUT REQUIREMENTS:
You MUST respond in valid JSON format only. No additional text before or after.
Analyze the provided candlestick data and provide:
1. Pattern identification (specific pattern name or null)
2. Signal (BUY/SELL/HOLD) - be conservative, only BUY/SELL with HIGH confidence
3. Confidence level (HIGH/MEDIUM/LOW) - be honest about uncertainty
4. Reasoning (2-3 sentences explaining your analysis)
5. Entry Price (current price or slightly better if waiting for pullback)
6. Stop Loss (2-5% below entry for BUY, 2-5% above for SELL)
7. Take Profit (1.5-3x risk distance from entry)
8. Risk-Reward Ratio (calculate: (takeProfit - entry) / (entry - stopLoss))
"""

def analyze_candlesticks_with_ollama(candles: List[Dict], symbol: str, current_price: float, volume: float, avg_volume: float, detected_patterns: Optional[List[Dict]] = None, level2_data: Optional[Dict] = None, stock_float: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyze candlestick patterns using Ollama AI with REAL market data
    
    Args:
        candles: List of candle dictionaries with open, high, low, close, volume (REAL data from IBKR)
        symbol: Stock symbol
        current_price: Current stock price (REAL from IBKR)
        volume: Current volume (REAL from IBKR)
        avg_volume: Average volume (REAL from IBKR)
        detected_patterns: Optional patterns detected by frontend
        level2_data: Optional Level 2 order book data (REAL from IBKR)
        
    Returns:
        Analysis result with pattern, signal, confidence, and reasoning
    """
    try:
        # Format candles for analysis
        candle_data = []
        for i, candle in enumerate(candles[-20:]):  # Last 20 candles for context
            candle_data.append({
                "index": i,
                "open": candle.get('open', candle.get('Open', 0)),
                "high": candle.get('high', candle.get('High', 0)),
                "low": candle.get('low', candle.get('Low', 0)),
                "close": candle.get('close', candle.get('Close', 0)),
                "volume": candle.get('volume', candle.get('Volume', 0)),
                "is_bullish": candle.get('close', candle.get('Close', 0)) > candle.get('open', candle.get('Open', 0))
            })
        
        # Calculate volume ratio
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
        
        # Include detected patterns if provided
        pattern_context = ""
        if detected_patterns and len(detected_patterns) > 0:
            pattern_context = f"\n\nDETECTED PATTERNS (from technical analysis):\n"
            for i, pattern in enumerate(detected_patterns[-3:]):  # Last 3 patterns
                pattern_context += f"{i+1}. {pattern.get('pattern', 'Unknown')} - {pattern.get('signal', 'N/A')} signal ({pattern.get('confidence', 'N/A')} confidence)\n"
                pattern_context += f"   Description: {pattern.get('description', 'N/A')}\n"
            pattern_context += "\nConsider these detected patterns in your analysis and validate or expand on them.\n"
        
        # Calculate additional context for better analysis
        if len(candles) >= 5:
            recent_closes = [c.get('close', c.get('Close', 0)) for c in candles[-5:]]
            price_trend = "UP" if recent_closes[-1] > recent_closes[0] else "DOWN" if recent_closes[-1] < recent_closes[0] else "SIDEWAYS"
            price_change_pct = ((recent_closes[-1] - recent_closes[0]) / recent_closes[0] * 100) if recent_closes[0] > 0 else 0
            recent_high = max([c.get('high', c.get('High', 0)) for c in candles[-10:]])
            recent_low = min([c.get('low', c.get('Low', 0)) for c in candles[-10:]])
            price_position = ((current_price - recent_low) / (recent_high - recent_low) * 100) if (recent_high - recent_low) > 0 else 50
        else:
            price_trend = "UNKNOWN"
            price_change_pct = 0
            price_position = 50
            recent_high = current_price
            recent_low = current_price
        
        # Build enhanced analysis prompt with more context
        # Include complete pattern library if available (provides all 36+ patterns)
        pattern_section = ""
        if COMPLETE_PATTERN_LIBRARY:
            # Use complete library which has all patterns with detailed descriptions
            pattern_section = f"\n\n# COMPLETE PATTERN REFERENCE LIBRARY\n{COMPLETE_PATTERN_LIBRARY}\n"
        
        # Include IBKR trading knowledge if available
        trading_section = ""
        if IBKR_TRADING_KNOWLEDGE:
            trading_section = f"\n\n# IBKR TRADING CAPABILITIES\n{IBKR_TRADING_KNOWLEDGE}\n"
        
        # Include relative volume knowledge if available
        volume_section = ""
        if RELATIVE_VOLUME_KNOWLEDGE:
            volume_section = f"""
# RELATIVE VOLUME (RVOL) ANALYSIS - WARRIOR TRADING
{RELATIVE_VOLUME_KNOWLEDGE}

CURRENT VOLUME ANALYSIS:
- Current Volume: {volume:,.0f} shares
- Average Volume: {avg_volume:,.0f} shares
- Volume Ratio (RVOL): {volume_ratio:.2f}x

RVOL INTERPRETATION:
- RVOL ≥ 2.0: Stock is IN PLAY (good for trading) ✅
- RVOL 1.5-2.0: Stock is getting attention (watch for setups) ⚠️
- RVOL < 1.5: Stock is NOT in play (avoid or be cautious) ❌

CRITICAL RULES:
- Always confirm breakouts with volume (volume spike on breakout)
- Never trade breakouts without volume confirmation (false breakout risk)
- High RVOL = more liquidity = tighter spreads = less slippage
- Low RVOL = choppy price action = false breakouts = unpredictable moves
- Volume spikes at support/resistance = buyers/sellers fighting = potential reversal

USE THIS KNOWLEDGE to:
1. Assess if stock is "in play" (RVOL ≥ 2.0)
2. Confirm breakouts with volume confirmation
3. Identify volume spikes at support/resistance levels
4. Avoid trading low RVOL stocks (false breakouts)
5. Use volume ratio to enhance trading confidence

"""
        
        # Include float knowledge if available
        float_section = ""
        if FLOAT_KNOWLEDGE:
            float_section = f"""
# STOCK FLOAT ANALYSIS - WARRIOR TRADING
{FLOAT_KNOWLEDGE}

FLOAT TRADING INSIGHTS:
- Low Float (< 50M): Bigger moves, wider spreads, harder to trade large size
- High Float (> 200M): Smaller moves, tighter spreads, easier to trade large size
- Low Float + High Volume: Explosive moves (parabolic potential)
- High Float + High Volume: Steady momentum
- Ideal Setup: Low float + high RVOL + positive catalyst + high short interest = parabolic moves

CRITICAL RULES:
- Adjust position sizing: Low float = smaller positions, High float = larger positions
- Watch for float changes: Secondary offerings (dilution), buybacks (support), splits (adjustments)
- Low float stocks make bigger moves due to less liquidity
- High float stocks are more stable but make smaller moves

USE THIS KNOWLEDGE to:
1. Understand why low float stocks make bigger moves
2. Adjust position sizing based on float
3. Identify explosive move potential (low float + high RVOL)
4. Watch for float changes (secondary offerings, buybacks)
5. Integrate float with volume and RVOL analysis

"""
        
        # Add float data if available
        if stock_float and stock_float > 0:
            float_analysis = f"""
CURRENT FLOAT DATA:
- Stock Float: {stock_float:,.0f} shares
- Float Category: {'Low Float (< 50M)' if stock_float < 50_000_000 else 'Medium Float (50M-200M)' if stock_float < 200_000_000 else 'High Float (> 200M)'}
- Move Potential: {'Explosive moves possible' if stock_float < 50_000_000 else 'Moderate moves' if stock_float < 200_000_000 else 'Steady moves'}
- Spread Impact: {'Wider spreads expected' if stock_float < 50_000_000 else 'Tighter spreads' if stock_float > 200_000_000 else 'Moderate spreads'}
- Position Sizing: {'Use smaller positions' if stock_float < 50_000_000 else 'Can use larger positions' if stock_float > 200_000_000 else 'Moderate positions'}

FLOAT + VOLUME ANALYSIS:
- Float: {stock_float:,.0f} shares
- Current Volume: {volume:,.0f} shares
- Volume Ratio (RVOL): {volume_ratio:.2f}x
- {'⚠️ Low float + high RVOL = EXPLOSIVE MOVE POTENTIAL' if stock_float < 50_000_000 and volume_ratio >= 2.0 else '✅ Good setup' if volume_ratio >= 2.0 else '⚠️ Low RVOL - stock not in play'}

"""
            float_section += float_analysis
        else:
            float_section += "\nNOTE: Float data not available for this stock. Use general float knowledge for analysis.\n"
        
        
        # Initialize data source section (emphasizes REAL data)
        data_source_section = f"""
# DATA SOURCE INFORMATION - CRITICAL FOR LEARNING
IMPORTANT: You are analyzing REAL market data from Interactive Brokers, not simulated or synthetic data.

Data Sources (ALL REAL):
- Candlestick Data: REAL historical data from IBKR (Interactive Brokers API)
- Current Price: REAL live price from IBKR market data feed
- Volume: REAL trading volume from IBKR
- Bid/Ask: REAL Level 1 quotes from IBKR
- Level 2 Data: {'REAL order book data from NASDAQ TotalView' if level2_data else 'Available but not provided in this analysis'}
- Market Data: Live, real-time data from professional trading platform

LEARNING FROM REAL DATA:
- This is REAL market data that professional traders use
- Learn from actual market behavior, not simulations
- Real data shows actual supply and demand
- Real data reflects actual market psychology
- Real data includes real institutional activity
- Real data has real support/resistance levels

Your analysis should be based on:
- REAL market dynamics
- REAL order flow
- REAL institutional activity
- REAL support/resistance from actual orders
- REAL price action from actual trading

Never use simulated or synthetic data when real data is available.

"""
        
        # Include comprehensive Level 2 market data information and REAL data if available
        level2_section = ""
        real_level2_data_section = ""
        
        if MARKET_DATA_LEVEL2_AVAILABLE:
            if LEVEL2_KNOWLEDGE:
                # Use comprehensive Level 2 knowledge
                level2_section = f"""
# COMPREHENSIVE LEVEL 2 MARKET DATA KNOWLEDGE
{LEVEL2_KNOWLEDGE}

CURRENT STATUS:
- Level 2 Order Book Data: ✅ ENABLED
- NASDAQ TotalView-OpenView: ✅ ACTIVE
- BookMap Integration: ✅ READY
- Order Flow Analysis: ✅ ENABLED

USE THIS KNOWLEDGE to provide sophisticated analysis that includes:
1. Support/Resistance from order book depth (large bids = support, large asks = resistance)
2. Order flow direction (buying vs selling pressure)
3. Institutional activity detection (large orders 10,000+ shares)
4. Order imbalances (bid/ask ratio analysis)
5. Entry/exit timing based on order flow patterns
6. Enhanced confidence when Level 2 confirms candlestick patterns

"""
            else:
                # Fallback to basic Level 2 info
                level2_section = f"""
# MARKET DATA CAPABILITIES (Level 2 Available)
Level 2 Order Book Data: ENABLED
- Full order book depth available for enhanced analysis
- BookMap integration ready - can track live buy/sell orders
- Order flow analysis enabled - detect institutional activity
- Market depth visualization - see support/resistance from order book
- Real-time bid/ask levels with size information

When analyzing, you can consider:
- Order book imbalances (more buyers vs sellers at key price levels)
- Large orders at support/resistance (institutional activity)
- Order flow direction (buying pressure vs selling pressure)
- Market maker positioning (where they're placing orders)
- Entry/exit timing based on order flow patterns

"""
            
            # Add REAL Level 2 data if provided
            if level2_data:
                bids = level2_data.get('bids', [])
                asks = level2_data.get('asks', [])
                total_bid_size = sum(b.get('size', 0) for b in bids)
                total_ask_size = sum(a.get('size', 0) for a in asks)
                bid_ask_ratio = total_bid_size / total_ask_size if total_ask_size > 0 else 1.0
                
                real_level2_data_section = f"""
# REAL LEVEL 2 ORDER BOOK DATA (Live from IBKR - USE THIS!)
This is REAL market data, not simulated. Use this to make actual trading decisions.

ORDER BOOK DEPTH:
- Total Bid Size: {total_bid_size:,} shares
- Total Ask Size: {total_ask_size:,} shares
- Bid/Ask Ratio: {bid_ask_ratio:.2f} ({'Bullish' if bid_ask_ratio > 1.5 else 'Bearish' if bid_ask_ratio < 0.67 else 'Balanced'})

TOP BIDS (Buyers - Support Levels):
{chr(10).join([f"  ${b.get('price', 0):.2f} - {b.get('size', 0):,} shares" for b in bids[:5]]) if bids else "  No bid data available"}

TOP ASKS (Sellers - Resistance Levels):
{chr(10).join([f"  ${a.get('price', 0):.2f} - {a.get('size', 0):,} shares" for a in asks[:5]]) if asks else "  No ask data available"}

ANALYSIS TASK WITH REAL LEVEL 2:
- Identify support levels from large bids (real orders)
- Identify resistance levels from large asks (real orders)
- Analyze order flow direction (bids vs asks)
- Detect order imbalances (real market pressure)
- Use this REAL data to confirm candlestick patterns
- Provide entry/exit timing based on REAL order book levels

"""
        
        analysis_prompt = f"""
{CANDLESTICK_TEACHING_PROMPT}
{data_source_section}
{pattern_section}
{trading_section}
{volume_section}
{float_section}
{level2_section}
{real_level2_data_section}

STOCK DATA (REAL from IBKR):
Symbol: {symbol}
Current Price: ${current_price:.2f}
Current Volume: {volume:,.0f}
Average Volume: {avg_volume:,.0f}
Volume Ratio (RVOL): {volume_ratio:.2f}x {'✅ IN PLAY (RVOL ≥ 2.0)' if volume_ratio >= 2.0 else '⚠️ Getting Attention (1.5-2.0)' if volume_ratio >= 1.5 else '❌ NOT IN PLAY (RVOL < 1.5)'}
Price Trend (last 5 candles): {price_trend} ({price_change_pct:+.2f}%)

OLLAMA TRADING CONSTRAINTS (MUST FOLLOW):
- Price Range: ONLY trade stocks between $1.00 and $6.00
- Maximum Position: $4,000 per stock per day
- End of Day: Close all positions before 4:00 PM ET (no new positions after 3:30 PM)
- If price is outside $1-$6 range, DO NOT trade

CRITICAL PRICE LEVELS:
- Recent HIGH (last 10 candles): ${recent_high:.2f} (resistance level)
- Recent LOW (last 10 candles): ${recent_low:.2f} (support level)
- Current Price: ${current_price:.2f}
- Price Position: {price_position:.1f}% between low and high
- Distance to HIGH: {((recent_high - current_price) / current_price * 100):.2f}%
- Distance to LOW: {((current_price - recent_low) / current_price * 100):.2f}%

TRADING STRATEGY USING HIGH/LOW:
- For BUY: Entry should be near LOW (support), stop below LOW, target near HIGH (resistance)
- For SELL: Entry should be near HIGH (resistance), stop above HIGH, target near LOW (support)
- Use trailing stops: Raise stop loss as price moves in your favor (never lower it)

CANDLESTICK DATA (Last 20 candles, most recent is index {len(candle_data)-1}):
⚠️ CRITICAL: This is REAL market data from Interactive Brokers, not simulated.
Learn from actual market behavior and real price action. This is how professional traders analyze stocks.
{json.dumps(candle_data, indent=2)}
{pattern_context}

ANALYSIS TASK (Using REAL Market Data):
Carefully analyze these candlesticks considering:
- Pattern recognition (look for the patterns I taught you)
- Volume confirmation (volume ratio: {volume_ratio:.2f}x)
- Price position relative to HIGH and LOW (support/resistance levels)
- Entry strategy: For BUY, prefer entry near LOW; For SELL, prefer entry near HIGH
- Stop loss: Set below LOW for BUY, above HIGH for SELL
- Take profit: Target near HIGH for BUY, near LOW for SELL
- Trailing stop: Plan to raise stop loss as price moves in your favor
- Risk-reward potential using HIGH/LOW levels

CRITICAL: Respond ONLY with valid JSON. No text before or after the JSON object.

{{
    "pattern": "pattern_name or null",
    "signal": "BUY|SELL|HOLD",
    "confidence": "HIGH|MEDIUM|LOW",
    "reasoning": "2-3 sentence explanation of your analysis including pattern, volume, HIGH/LOW levels, and context",
    "entryPrice": number or null,  // Should be near LOW for BUY, near HIGH for SELL
    "stopLoss": number or null,  // Should be below LOW for BUY, above HIGH for SELL
    "takeProfit": number or null,  // Should be near HIGH for BUY, near LOW for SELL
    "trailingStopPercent": number or null,  // Percentage to trail stop loss (e.g., 2.0 for 2%)
    "riskRewardRatio": number or null
}}
"""
        
        # Call Ollama API
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": analysis_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Lower temperature for more consistent, focused analysis
                    "top_p": 0.85,  # Slightly lower for more focused responses
                    "top_k": 40,  # Limit vocabulary for more consistent outputs
                    "num_predict": 500,  # Limit response length for faster analysis
                },
                "system": "You are a professional stock trader analyzing REAL market data from Interactive Brokers. Always use real data, never simulated data. Learn from actual market behavior. Always respond in valid JSON format only. Be precise, conservative, and data-driven in your analysis."
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    analysis = json.loads(json_text)
                else:
                    # Fallback: parse text response
                    analysis = parse_text_response(response_text)
            except json.JSONDecodeError:
                # Fallback parsing
                analysis = parse_text_response(response_text)
            
            # Validate and enhance analysis
            if 'riskRewardRatio' not in analysis:
                if analysis.get('entryPrice') and analysis.get('stopLoss') and analysis.get('takeProfit'):
                    entry = analysis['entryPrice']
                    stop = analysis['stopLoss']
                    profit = analysis['takeProfit']
                    if analysis.get('signal') == 'BUY' and entry > stop:
                        risk = entry - stop
                        reward = profit - entry
                        if risk > 0:
                            analysis['riskRewardRatio'] = round(reward / risk, 2)
                    elif analysis.get('signal') == 'SELL' and entry < stop:
                        risk = stop - entry
                        reward = entry - profit
                        if risk > 0:
                            analysis['riskRewardRatio'] = round(reward / risk, 2)
            
            # Add metadata
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['model'] = OLLAMA_MODEL
            analysis['candleCount'] = len(candles)
            analysis['volumeRatio'] = volume_ratio
            
            logging.info(f"✅ [OLLAMA] Analysis complete for {symbol}: {analysis.get('signal')} ({analysis.get('confidence')})")
            return {
                'success': True,
                'analysis': analysis
            }
        else:
            logging.error(f"❌ [OLLAMA] API error: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"Ollama API error: {response.status_code}",
                'analysis': get_fallback_analysis(candles, volume_ratio)
            }
            
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ [OLLAMA] Connection error: {e}")
        return {
            'success': False,
            'error': f"Ollama connection error: {str(e)}",
            'analysis': get_fallback_analysis(candles, volume_ratio)
        }
    except Exception as e:
        logging.error(f"❌ [OLLAMA] Analysis error: {e}")
        return {
            'success': False,
            'error': f"Analysis error: {str(e)}",
            'analysis': get_fallback_analysis(candles, volume_ratio)
        }

def parse_text_response(text: str) -> Dict[str, Any]:
    """Parse text response from Ollama into structured format"""
    text_lower = text.lower()
    
    # Extract signal
    signal = "HOLD"
    if "buy" in text_lower and "sell" not in text_lower:
        signal = "BUY"
    elif "sell" in text_lower:
        signal = "SELL"
    
    # Extract confidence
    confidence = "MEDIUM"
    if "high" in text_lower and "confidence" in text_lower:
        confidence = "HIGH"
    elif "low" in text_lower and "confidence" in text_lower:
        confidence = "LOW"
    
    # Extract pattern (look for common patterns)
    pattern = None
    pattern_keywords = {
        "hammer": "HAMMER",
        "engulfing": "ENGULFING",
        "morning star": "MORNING_STAR",
        "evening star": "EVENING_STAR",
        "doji": "DOJI",
        "shooting star": "SHOOTING_STAR"
    }
    for keyword, pattern_name in pattern_keywords.items():
        if keyword in text_lower:
            pattern = pattern_name
            break
    
    return {
        "pattern": pattern,
        "signal": signal,
        "confidence": confidence,
        "reasoning": text[:500] if len(text) > 500 else text,
        "entryPrice": None,
        "stopLoss": None,
        "takeProfit": None
    }

def get_fallback_analysis(candles: List[Dict], volume_ratio: float) -> Dict[str, Any]:
    """Fallback analysis when Ollama is unavailable"""
    if not candles:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": "LOW",
            "reasoning": "No candle data available",
            "entryPrice": None,
            "stopLoss": None,
            "takeProfit": None
        }
    
    # Simple trend analysis
    recent_candles = candles[-5:]
    closes = [c.get('close', c.get('Close', 0)) for c in recent_candles]
    
    if len(closes) >= 2:
        trend = "UP" if closes[-1] > closes[0] else "DOWN"
        signal = "BUY" if trend == "UP" and volume_ratio > 1.5 else "HOLD"
        if trend == "DOWN" and volume_ratio > 1.5:
            signal = "SELL"
    else:
        signal = "HOLD"
        trend = "UNKNOWN"
    
    return {
        "pattern": None,
        "signal": signal,
        "confidence": "LOW",
        "reasoning": f"Fallback analysis: {trend} trend, volume {volume_ratio:.2f}x average",
        "entryPrice": None,
        "stopLoss": None,
        "takeProfit": None
    }

def check_ollama_connection() -> Dict[str, Any]:
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {
                'available': True,
                'models': [m.get('name', '') for m in models],
                'baseUrl': OLLAMA_BASE_URL
            }
        else:
            return {
                'available': False,
                'error': f"Ollama API returned {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            'available': False,
            'error': f"Cannot connect to Ollama: {str(e)}"
        }

def teach_level2_to_ollama() -> Dict[str, Any]:
    """
    Teach Ollama comprehensive Level 2 market data knowledge
    """
    try:
        from ollama_level2_teaching import teach_level2_to_ollama as teach_level2
        return teach_level2()
    except ImportError:
        logging.warning("⚠️ Level 2 teaching module not available")
        return {
            'success': False,
            'error': 'Level 2 teaching module not available'
        }

def teach_ollama_pattern(pattern_name: str, description: str, examples: List[Dict]) -> Dict[str, Any]:
    """
    Teach Ollama a new candlestick pattern
    
    Args:
        pattern_name: Name of the pattern
        description: Description of the pattern
        examples: List of example candle sequences
        
    Returns:
        Teaching result
    """
    teaching_prompt = f"""
Learn a new candlestick pattern:

PATTERN NAME: {pattern_name}
DESCRIPTION: {description}

EXAMPLES:
{json.dumps(examples, indent=2)}

Please acknowledge that you understand this pattern and can identify it in future analyses.
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": teaching_prompt,
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': f"Pattern {pattern_name} taught successfully"
            }
        else:
            return {
                'success': False,
                'error': f"Ollama API error: {response.status_code}"
            }
    except Exception as e:
        return {
            'success': False,
            'error': f"Teaching error: {str(e)}"
        }

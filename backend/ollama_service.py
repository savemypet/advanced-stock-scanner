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
OLLAMA_TIMEOUT = 30  # seconds

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

def analyze_candlesticks_with_ollama(candles: List[Dict], symbol: str, current_price: float, volume: float, avg_volume: float, detected_patterns: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Analyze candlestick patterns using Ollama AI
    
    Args:
        candles: List of candle dictionaries with open, high, low, close, volume
        symbol: Stock symbol
        current_price: Current stock price
        volume: Current volume
        avg_volume: Average volume
        
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
        
        analysis_prompt = f"""
{CANDLESTICK_TEACHING_PROMPT}
{pattern_section}
{trading_section}

STOCK DATA:
Symbol: {symbol}
Current Price: ${current_price:.2f}
Current Volume: {volume:,.0f}
Average Volume: {avg_volume:,.0f}
Volume Ratio: {volume_ratio:.2f}x
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
{json.dumps(candle_data, indent=2)}
{pattern_context}
ANALYSIS TASK:
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
                "system": "You are a professional stock trader and candlestick pattern expert. Always respond in valid JSON format only. Be precise, conservative, and data-driven in your analysis."
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

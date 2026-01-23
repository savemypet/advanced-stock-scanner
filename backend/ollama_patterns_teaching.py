"""
Comprehensive Candlestick Pattern Teaching for Ollama
Contains ALL patterns from the codebase with detailed descriptions
"""
import requests
import logging
import json
from typing import Dict, Any

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"
OLLAMA_TIMEOUT = 60  # Longer timeout for teaching

# COMPREHENSIVE CANDLESTICK PATTERN LIBRARY
# This includes ALL patterns from candlestickPatterns.ts

COMPLETE_PATTERN_LIBRARY = """
# COMPLETE CANDLESTICK PATTERN LIBRARY

## CANDLESTICK BASICS

### Candle Components:
- **Open**: Opening price of the period
- **High**: Highest price reached
- **Low**: Lowest price reached  
- **Close**: Closing price of the period
- **Body**: |Close - Open| (represents buying/selling pressure)
- **Upper Shadow/Wick**: High - max(Open, Close) (rejection of higher prices)
- **Lower Shadow/Wick**: min(Open, Close) - Low (rejection of lower prices)

### Candle Types:
- **Bullish (Green/White)**: Close > Open (buyers won)
- **Bearish (Red/Black)**: Close < Open (sellers won)
- **Doji**: Open ≈ Close (indecision, small body < 10% of range)

---

## NEUTRAL PATTERNS (Context-Dependent)

### 1. DOJI
**Visual**: Open and Close are nearly equal, small body (< 10% of total range)
**Characteristics**: 
- Body is very small relative to total range
- Shows market indecision
- Can have long wicks on either side
**Signal**: Depends on context
- After uptrend: Potential bearish reversal (SELL)
- After downtrend: Potential bullish reversal (BUY)
**Confidence**: LOW to MEDIUM
**Context**: More significant at support/resistance levels

### 2. SPINNING_TOP
**Visual**: Small body (< 30% of range), long upper AND lower shadows
**Characteristics**:
- Body < 30% of total range
- Upper shadow > body
- Lower shadow > body
- Shows strong indecision
**Signal**: Depends on context
- After uptrend: Potential bearish reversal (SELL)
- After downtrend: Potential bullish reversal (BUY)
**Confidence**: LOW
**Context**: Indicates market uncertainty

### 3. MARUBOZU
**Visual**: Very large body (> 95% of range), minimal or no shadows
**Characteristics**:
- Body > 95% of total range
- Upper shadow < 2.5% of range
- Lower shadow < 2.5% of range
- Shows strong directional momentum
**Signal**: 
- Bullish Marubozu: BUY (strong buying pressure)
- Bearish Marubozu: SELL (strong selling pressure)
**Confidence**: MEDIUM to HIGH
**Context**: Strong momentum indicator

### 4. STAR
**Visual**: Small body (< 20% of range), can appear in star patterns
**Characteristics**:
- Body < 20% of total range
- Body > 0 (not a doji)
- Often part of reversal patterns (Morning/Evening Star)
**Signal**: Depends on context (usually part of larger pattern)
**Confidence**: LOW (unless part of star pattern)
**Context**: Component of multi-candle patterns

---

## BULLISH SINGLE CANDLE PATTERNS

### 5. HAMMER
**Visual**: Small body at top, long lower shadow (2x+ body), little/no upper shadow
**Characteristics**:
- Lower shadow > body × 2
- Upper shadow < body × 0.3
- Body is bullish (close > open)
- Body > 0
**Signal**: BUY
**Confidence**: MEDIUM to HIGH
**Context**: 
- More reliable at support levels
- After downtrend: Strong reversal signal
- Volume confirmation increases confidence
**Description**: Shows rejection of lower prices, buyers stepping in

### 6. INVERTED_HAMMER
**Visual**: Small body at bottom, long upper shadow (2x+ body), little/no lower shadow
**Characteristics**:
- Upper shadow > body × 2
- Lower shadow < body × 0.3
- Body > 0
**Signal**: BUY
**Confidence**: MEDIUM
**Context**:
- Potential reversal signal
- Needs confirmation (next candle should be bullish)
- More reliable at support
**Description**: Shows buyers trying to push price up, but sellers rejected

### 7. DRAGONFLY_DOJI
**Visual**: Doji with very long lower shadow, minimal upper shadow
**Characteristics**:
- Is a Doji (body < 10% of range)
- Lower shadow > 60% of total range
- Upper shadow < 10% of total range
**Signal**: BUY
**Confidence**: MEDIUM
**Context**:
- Strong bullish reversal signal
- Shows rejection of lower prices
- More reliable at support
**Description**: Strong rejection of lower prices, potential reversal

### 8. BULLISH_SPINNING_TOP
**Visual**: Spinning top with bullish body
**Characteristics**:
- Small body (< 30% of range)
- Long upper and lower shadows
- Body is bullish
**Signal**: BUY (weak)
**Confidence**: LOW
**Context**: Indecision, but slightly bullish

---

## BEARISH SINGLE CANDLE PATTERNS

### 9. SHOOTING_STAR
**Visual**: Small body at bottom, long upper shadow (2x+ body), little/no lower shadow
**Characteristics**:
- Upper shadow > body × 2
- Lower shadow < body × 0.3
- Body is bearish (close < open)
- Body > 0
**Signal**: SELL
**Confidence**: MEDIUM to HIGH
**Context**:
- More reliable at resistance levels
- After uptrend: Strong reversal signal
- Volume confirmation increases confidence
**Description**: Shows rejection of higher prices, sellers stepping in

### 10. HANGING_MAN
**Visual**: Small body at top, long lower shadow (2x+ body), little/no upper shadow
**Characteristics**:
- Lower shadow > body × 2
- Upper shadow < body × 0.3
- Body is bearish (close < open)
- Body > 0
**Signal**: SELL
**Confidence**: MEDIUM
**Context**:
- After uptrend: Potential reversal
- At resistance: More reliable
- Needs confirmation
**Description**: Shows potential weakness after uptrend

### 11. GRAVESTONE_DOJI
**Visual**: Doji with very long upper shadow, minimal lower shadow
**Characteristics**:
- Is a Doji (body < 10% of range)
- Upper shadow > 60% of total range
- Lower shadow < 10% of total range
**Signal**: SELL
**Confidence**: MEDIUM
**Context**:
- Strong bearish reversal signal
- Shows rejection of higher prices
- More reliable at resistance
**Description**: Strong rejection of higher prices, potential reversal

### 12. BEARISH_SPINNING_TOP
**Visual**: Spinning top with bearish body
**Characteristics**:
- Small body (< 30% of range)
- Long upper and lower shadows
- Body is bearish
**Signal**: SELL (weak)
**Confidence**: LOW
**Context**: Indecision, but slightly bearish

---

## BULLISH DOUBLE CANDLE PATTERNS

### 13. BULLISH_ENGULFING
**Visual**: Small bearish candle followed by large bullish candle that completely engulfs it
**Characteristics**:
- Previous candle: Bearish
- Current candle: Bullish
- Current open < previous close
- Current close > previous open
- Current body completely covers previous body
**Signal**: BUY
**Confidence**: HIGH
**Context**:
- Strong reversal signal
- After downtrend: Very reliable
- Volume confirmation: 2x+ average
**Description**: Buyers completely overwhelm sellers, strong reversal

### 14. BULLISH_HARAMI
**Visual**: Large bearish candle followed by small bullish candle inside it
**Characteristics**:
- Previous candle: Bearish
- Current candle: Bullish
- Current open > previous close
- Current close < previous open
- Current body < previous body × 0.5
**Signal**: BUY
**Confidence**: MEDIUM
**Context**:
- Potential reversal (weaker than engulfing)
- Needs confirmation
- After downtrend: More reliable
**Description**: Selling pressure weakening, potential reversal

### 15. PIERCING_LINE
**Visual**: Bearish candle followed by bullish candle that pierces its midpoint
**Characteristics**:
- Previous candle: Bearish
- Current candle: Bullish
- Current open < previous low
- Current close > (previous open + previous close) / 2
- Current close < previous open
**Signal**: BUY
**Confidence**: MEDIUM
**Context**:
- Bullish reversal signal
- After downtrend: More reliable
- Volume confirmation helps
**Description**: Buyers push price up through bearish candle's midpoint

### 16. BULLISH_KICKER
**Visual**: Bearish candle followed by bullish candle with gap up
**Characteristics**:
- Previous candle: Bearish, large body (> 70% of range)
- Current candle: Bullish, large body (> 70% of range)
- Current open > previous close (gap up)
**Signal**: BUY
**Confidence**: HIGH
**Context**:
- Extremely strong reversal
- Gap shows strong buying pressure
- Very reliable signal
**Description**: Powerful bullish reversal with gap

### 17. TWEEZER_BOTTOM
**Visual**: Two candles with nearly identical lows
**Characteristics**:
- Previous and current candles have lows within 0.2% of each other
- Current candle is bullish
- Shows support level
**Signal**: BUY
**Confidence**: MEDIUM
**Context**:
- Support level identified
- Reversal at support
- More reliable with volume
**Description**: Support level, buyers defending price

---

## BEARISH DOUBLE CANDLE PATTERNS

### 18. BEARISH_ENGULFING
**Visual**: Small bullish candle followed by large bearish candle that completely engulfs it
**Characteristics**:
- Previous candle: Bullish
- Current candle: Bearish
- Current open > previous close
- Current close < previous open
- Current body completely covers previous body
**Signal**: SELL
**Confidence**: HIGH
**Context**:
- Strong reversal signal
- After uptrend: Very reliable
- Volume confirmation: 2x+ average
**Description**: Sellers completely overwhelm buyers, strong reversal

### 19. BEARISH_HARAMI
**Visual**: Large bullish candle followed by small bearish candle inside it
**Characteristics**:
- Previous candle: Bullish
- Current candle: Bearish
- Current open < previous close
- Current close > previous open
- Current body < previous body × 0.5
**Signal**: SELL
**Confidence**: MEDIUM
**Context**:
- Potential reversal (weaker than engulfing)
- Needs confirmation
- After uptrend: More reliable
**Description**: Buying pressure weakening, potential reversal

### 20. DARK_CLOUD_COVER
**Visual**: Bullish candle followed by bearish candle that closes below midpoint
**Characteristics**:
- Previous candle: Bullish
- Current candle: Bearish
- Current open > previous high
- Current close < (previous open + previous close) / 2
- Current close > previous open
**Signal**: SELL
**Confidence**: MEDIUM
**Context**:
- Bearish reversal signal
- After uptrend: More reliable
- Volume confirmation helps
**Description**: Sellers push price down through bullish candle's midpoint

### 21. BEARISH_KICKER
**Visual**: Bullish candle followed by bearish candle with gap down
**Characteristics**:
- Previous candle: Bullish, large body (> 70% of range)
- Current candle: Bearish, large body (> 70% of range)
- Current open < previous close (gap down)
**Signal**: SELL
**Confidence**: HIGH
**Context**:
- Extremely strong reversal
- Gap shows strong selling pressure
- Very reliable signal
**Description**: Powerful bearish reversal with gap

### 22. TWEEZER_TOP
**Visual**: Two candles with nearly identical highs
**Characteristics**:
- Previous and current candles have highs within 0.2% of each other
- Current candle is bearish
- Shows resistance level
**Signal**: SELL
**Confidence**: MEDIUM
**Context**:
- Resistance level identified
- Reversal at resistance
- More reliable with volume
**Description**: Resistance level, sellers defending price

---

## BULLISH TRIPLE CANDLE PATTERNS

### 23. MORNING_STAR
**Visual**: Bearish candle, small doji/gap, then bullish candle
**Characteristics**:
- First candle: Bearish
- Second candle: Small body (< 30% of first candle's body), can be doji
- Third candle: Bullish
- Third close > (first open + first close) / 2
**Signal**: BUY
**Confidence**: HIGH
**Context**:
- Strong bullish reversal
- After downtrend: Very reliable
- Volume confirmation: 2x+ on third candle
**Description**: Strong three-candle reversal pattern

### 24. MORNING_DOJI_STAR
**Visual**: Bearish candle, doji with gap, then bullish candle
**Characteristics**:
- First candle: Bearish
- Second candle: Doji, high < first close
- Third candle: Bullish
- Third close > (first open + first close) / 2
**Signal**: BUY
**Confidence**: HIGH
**Context**:
- Even stronger than Morning Star
- Doji shows indecision before reversal
- Very reliable signal
**Description**: Strong reversal with doji confirmation

### 25. BULLISH_ABANDONED_BABY
**Visual**: Bearish candle, doji with gap down, then bullish candle with gap up
**Characteristics**:
- First candle: Bearish
- Second candle: Doji, high < first low (gap down)
- Third candle: Bullish, open > second high (gap up)
- Third close > first close
**Signal**: BUY
**Confidence**: HIGH
**Context**:
- Extremely rare and powerful
- Gaps show strong reversal
- Very reliable signal
**Description**: Rare but very strong reversal pattern

### 26. THREE_WHITE_SOLDIERS
**Visual**: Three consecutive bullish candles with higher closes
**Characteristics**:
- All three candles: Bullish
- Second close > first close
- Third close > second close
- Second open > first open, second open < first close
- Third open > second open, third open < second close
**Signal**: BUY
**Confidence**: HIGH
**Context**:
- Strong uptrend continuation
- In uptrend: Very reliable
- Volume should increase
**Description**: Strong bullish momentum, uptrend continuation

### 27. THREE_INSIDE_UP
**Visual**: Bullish Harami followed by bullish confirmation
**Characteristics**:
- First and second: Bullish Harami pattern
- Third candle: Bullish
- Third close > second close
**Signal**: BUY
**Confidence**: HIGH
**Context**:
- Confirmation of reversal
- After downtrend: Very reliable
**Description**: Harami pattern confirmed by bullish candle

### 28. THREE_OUTSIDE_UP
**Visual**: Bullish Engulfing followed by bullish confirmation
**Characteristics**:
- First and second: Bullish Engulfing pattern
- Third candle: Bullish
- Third close > second close
**Signal**: BUY
**Confidence**: HIGH
**Context**:
- Strong bullish signal
- After downtrend: Very reliable
**Description**: Engulfing pattern confirmed by bullish candle

### 29. BULLISH_THREE_LINE_STRIKE
**Visual**: Three bullish candles followed by bearish candle that engulfs all three
**Characteristics**:
- First three candles: Bullish, each higher than previous
- Fourth candle: Bearish
- Fourth open > third close
- Fourth close < first open
**Signal**: BUY (counter-intuitive - continuation)
**Confidence**: HIGH
**Context**:
- Powerful continuation pattern
- The bearish candle is a "fake out"
- Very reliable continuation signal
**Description**: Strong continuation despite bearish candle

---

## BEARISH TRIPLE CANDLE PATTERNS

### 30. EVENING_STAR
**Visual**: Bullish candle, small doji/gap, then bearish candle
**Characteristics**:
- First candle: Bullish
- Second candle: Small body (< 30% of first candle's body), can be doji
- Third candle: Bearish
- Third close < (first open + first close) / 2
**Signal**: SELL
**Confidence**: HIGH
**Context**:
- Strong bearish reversal
- After uptrend: Very reliable
- Volume confirmation: 2x+ on third candle
**Description**: Strong three-candle reversal pattern

### 31. EVENING_DOJI_STAR
**Visual**: Bullish candle, doji with gap, then bearish candle
**Characteristics**:
- First candle: Bullish
- Second candle: Doji, low > first close
- Third candle: Bearish
- Third close < (first open + first close) / 2
**Signal**: SELL
**Confidence**: HIGH
**Context**:
- Even stronger than Evening Star
- Doji shows indecision before reversal
- Very reliable signal
**Description**: Strong reversal with doji confirmation

### 32. BEARISH_ABANDONED_BABY
**Visual**: Bullish candle, doji with gap up, then bearish candle with gap down
**Characteristics**:
- First candle: Bullish
- Second candle: Doji, low > first high (gap up)
- Third candle: Bearish, open < second low (gap down)
- Third close < first close
**Signal**: SELL
**Confidence**: HIGH
**Context**:
- Extremely rare and powerful
- Gaps show strong reversal
- Very reliable signal
**Description**: Rare but very strong reversal pattern

### 33. THREE_BLACK_CROWS
**Visual**: Three consecutive bearish candles with lower closes
**Characteristics**:
- All three candles: Bearish
- Second close < first close
- Third close < second close
- Second open < first open, second open > first close
- Third open < second open, third open > second close
**Signal**: SELL
**Confidence**: HIGH
**Context**:
- Strong downtrend continuation
- In downtrend: Very reliable
- Volume should increase
**Description**: Strong bearish momentum, downtrend continuation

### 34. THREE_INSIDE_DOWN
**Visual**: Bearish Harami followed by bearish confirmation
**Characteristics**:
- First and second: Bearish Harami pattern
- Third candle: Bearish
- Third close < second close
**Signal**: SELL
**Confidence**: HIGH
**Context**:
- Confirmation of reversal
- After uptrend: Very reliable
**Description**: Harami pattern confirmed by bearish candle

### 35. THREE_OUTSIDE_DOWN
**Visual**: Bearish Engulfing followed by bearish confirmation
**Characteristics**:
- First and second: Bearish Engulfing pattern
- Third candle: Bearish
- Third close < second close
**Signal**: SELL
**Confidence**: HIGH
**Context**:
- Strong bearish signal
- After uptrend: Very reliable
**Description**: Engulfing pattern confirmed by bearish candle

### 36. BEARISH_THREE_LINE_STRIKE
**Visual**: Three bearish candles followed by bullish candle that engulfs all three
**Characteristics**:
- First three candles: Bearish, each lower than previous
- Fourth candle: Bullish
- Fourth open < third close
- Fourth close > first open
**Signal**: SELL (counter-intuitive - continuation)
**Confidence**: HIGH
**Context**:
- Powerful continuation pattern
- The bullish candle is a "fake out"
- Very reliable continuation signal
**Description**: Strong continuation despite bullish candle

---

## PATTERN PRIORITY & RELIABILITY

### HIGH CONFIDENCE PATTERNS (Most Reliable):
1. BULLISH/BEARISH_ABANDONED_BABY - Extremely rare, very strong
2. BULLISH/BEARISH_KICKER - Strong gap reversals
3. MORNING/EVENING_DOJI_STAR - Strong with doji confirmation
4. THREE_WHITE_SOLDIERS / THREE_BLACK_CROWS - Strong momentum
5. BULLISH/BEARISH_ENGULFING - Strong reversals
6. THREE_LINE_STRIKE - Powerful continuation

### MEDIUM CONFIDENCE PATTERNS:
1. MORNING/EVENING_STAR - Good reversals
2. HAMMER/SHOOTING_STAR - Reliable at support/resistance
3. PIERCING_LINE/DARK_CLOUD_COVER - Moderate reversals
4. TWEEZER_BOTTOM/TOP - Support/resistance levels
5. HARAMI patterns - Weaker reversals, need confirmation

### LOW CONFIDENCE PATTERNS:
1. DOJI - Indecision, context-dependent
2. SPINNING_TOP - Indecision
3. STAR - Component of larger patterns
4. Single candle patterns without context

---

## VOLUME CONFIRMATION RULES

- **HIGH Confidence**: Volume 2x+ average volume
- **MEDIUM Confidence**: Volume 1.5-2x average volume
- **LOW Confidence**: Volume < 1.5x average volume

Patterns with high volume are MUCH more reliable.

---

## TREND CONTEXT RULES

1. **Reversal Patterns** (Hammer, Engulfing, Star patterns):
   - More reliable when they occur at support/resistance
   - After strong trends: More reliable
   - At key levels: Higher confidence

2. **Continuation Patterns** (Three Soldiers, Three Crows):
   - More reliable in trending markets
   - Less reliable in choppy/sideways markets
   - Volume confirmation is critical

3. **Context Matters**:
   - Same pattern in uptrend vs downtrend can mean different things
   - Always consider overall trend direction
   - Support/resistance levels increase reliability

---

## TRADING DECISION FRAMEWORK

When analyzing candlesticks:

1. **Identify Pattern**: Look for clear pattern matches
2. **Check Volume**: Volume should confirm (2x+ for high confidence)
3. **Check Context**: Is it at support/resistance? What's the trend?
4. **Check Confidence**: HIGH patterns are more reliable
5. **Calculate Risk-Reward**: Entry, stop, target prices
6. **Make Decision**: BUY/SELL/HOLD based on all factors

**BUY Signal**: Strong bullish pattern + High volume (2x+) + At support + HIGH confidence
**SELL Signal**: Strong bearish pattern + High volume (2x+) + At resistance + HIGH confidence
**HOLD Signal**: No clear pattern, conflicting signals, or LOW confidence

---

## IMPORTANT NOTES

1. **No pattern is 100% reliable** - Always use stop losses
2. **Volume is critical** - Patterns without volume confirmation are weaker
3. **Context matters** - Same pattern in different contexts can mean different things
4. **Multiple confirmations** - Look for multiple patterns or indicators aligning
5. **Risk management** - Always calculate risk-reward before trading
6. **Trend alignment** - Patterns aligned with trend are more reliable

You now have complete knowledge of all candlestick patterns. Use this knowledge to analyze candlestick data accurately and provide precise trading signals.
"""

def teach_all_patterns_to_ollama() -> Dict[str, Any]:
    """
    Teach Ollama ALL candlestick patterns from the codebase
    This is a comprehensive teaching session
    """
    try:
        teaching_prompt = f"""
You are now learning the COMPLETE candlestick pattern library for stock trading analysis.

{COMPLETE_PATTERN_LIBRARY}

LEARNING TASK:
1. Study each pattern carefully
2. Understand the visual characteristics
3. Learn when each pattern is most reliable
4. Understand confidence levels
5. Learn volume and context requirements

After learning, you should be able to:
- Identify any of these 36+ patterns in candlestick data
- Determine appropriate confidence levels
- Consider volume and context
- Provide accurate BUY/SELL/HOLD signals
- Calculate risk-reward ratios

Please acknowledge that you understand all these patterns and are ready to analyze candlestick charts using this knowledge.

Respond with: "I understand all candlestick patterns and am ready to analyze charts."
"""
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": teaching_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Very low for learning
                    "num_predict": 200,
                },
                "system": "You are learning to be an expert candlestick pattern analyst. Pay close attention to all pattern details."
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            logging.info("✅ [OLLAMA TEACHING] All patterns taught successfully")
            logging.info(f"📚 [OLLAMA TEACHING] Response: {response_text[:200]}...")
            
            return {
                'success': True,
                'message': 'All candlestick patterns taught successfully',
                'patterns_taught': 36,
                'response_preview': response_text[:200]
            }
        else:
            logging.error(f"❌ [OLLAMA TEACHING] API error: {response.status_code}")
            return {
                'success': False,
                'error': f"Ollama API error: {response.status_code}"
            }
    except Exception as e:
        logging.error(f"❌ [OLLAMA TEACHING] Error: {e}")
        return {
            'success': False,
            'error': f"Teaching error: {str(e)}"
        }

def get_complete_teaching_prompt() -> str:
    """Get the complete teaching prompt for use in analysis"""
    return COMPLETE_PATTERN_LIBRARY

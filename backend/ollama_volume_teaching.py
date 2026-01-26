"""
Relative Volume Teaching for Ollama
Teaches Ollama about relative volume (RVOL) and how to use it for day trading
Based on Warrior Trading professional insights
"""
import requests
import logging
from typing import Dict, Any

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:4b"  # Use available model
OLLAMA_TIMEOUT = 120

# COMPREHENSIVE RELATIVE VOLUME KNOWLEDGE
# Based on Warrior Trading professional day trading insights
RELATIVE_VOLUME_KNOWLEDGE = """
# COMPLETE RELATIVE VOLUME (RVOL) KNOWLEDGE BASE
# Source: Warrior Trading professional day trading guide

## WHAT IS RELATIVE VOLUME?

**Relative Volume (RVOL)** is an indicator that tells traders how current trading volume is compared to past trading volume over a given period.

**Warrior Trading Insight**: "It is kind of like a radar for how 'in-play' a stock is."

### Key Concepts:

1. **Volume Comparison**: RVOL compares current volume to historical average volume
2. **In-Play Indicator**: Higher relative volume = more traders watching and trading the stock
3. **Liquidity Indicator**: Stocks with high relative volume have more liquidity and trade better
4. **Display Format**: RVOL is displayed as a ratio (e.g., 3.5 = 3.5x normal volume)

### Why Relative Volume Matters:

**Warrior Trading**: "The higher the relative volume is the more in play it is because more traders are watching and trading it. As traders, this is what we want."

- **More Liquidity**: High RVOL stocks have tighter spreads and less slippage
- **Better Price Action**: Stocks with high RVOL tend to trade better than low RVOL stocks
- **Predictable Moves**: High RVOL = more predictable price action, low RVOL = choppy/random moves
- **False Breakout Prevention**: Trading stocks "out of play" (low RVOL) results in false breakouts

## RELATIVE VOLUME TRADING CRITERIA

### Warrior Trading Ideal Setup:

**Day traders like to see RVOL at 2 or higher** with:
- ✅ Positive catalyst (news, earnings, etc.)
- ✅ Low float (fewer shares available = bigger moves)
- ✅ Higher short interest (potential for short squeeze)

**Warrior Trading**: "When all this falls in line together we have a recipe for parabolic moves that can make trading months and sometimes even years."

### RVOL Thresholds:

- **RVOL < 1.0**: Below average volume - stock is NOT in play, avoid trading
- **RVOL 1.0 - 1.5**: Average to slightly above - stock may be in play but weak
- **RVOL 1.5 - 2.0**: Above average - stock is getting attention, watch for setups
- **RVOL 2.0 - 3.0**: High volume - stock is IN PLAY, good for trading
- **RVOL 3.0+**: Very high volume - stock is VERY IN PLAY, strong moves likely

## USING RELATIVE VOLUME FOR TRADING DECISIONS

### 1. Stock Selection (Morning Preparation)

**Warrior Trading Pro Tip**: "RVOL is often overlooked, especially by new traders, but it is important to understand this metric and to add it into your morning preparation."

- **Check RVOL in morning prep**: Identify which stocks are in play
- **Focus on high RVOL stocks**: These are what other traders are watching
- **Avoid low RVOL stocks**: Less traders watching = choppy price action

### 2. Confirming Breakouts

**Warrior Trading Strategy**: "The key to this strategy is on the breakout... only if volume confirms the move."

**Example from Warrior Trading (NVDA)**:
- Stock had strong opening drive
- Pulled back to support on lighter volume
- Consolidated in tight wedge pattern
- **Breakout confirmed by volume spike** - this is where you enter
- Volume spiked when it broke out and held above resistance

**Key Rule**: Only enter breakouts if volume confirms the move (RVOL increases on breakout)

### 3. Identifying Support/Resistance Battles

**Warrior Trading**: "As a stock gets oversold or overbought we want to look for volume to get a spike in relative volume which would indicate that buyers and seller are fighting over an important support or resistance level and will likely reverse."

- **Volume spike at support**: Buyers fighting to hold the level = potential reversal up
- **Volume spike at resistance**: Sellers fighting to hold the level = potential reversal down
- **Low volume at levels**: No real battle = level may break easily

### 4. Comparing Time Frames

**Warrior Trading**: "I like to see how the RVOL is compared to previous trading days but I also like to check it versus opening drives and second leg drives to compare strength."

- **Daily RVOL**: Compare to previous days (is stock more in play today?)
- **Opening Drive RVOL**: Compare opening volume to rest of day
- **Second Leg Drive**: Compare second move volume to first move
- **Pattern Breakout RVOL**: Compare breakout volume to consolidation volume

### 5. Volume Confirmation Rules

**Always confirm price moves with volume**:

- **Breakout UP**: RVOL should increase (more buyers entering)
- **Breakout DOWN**: RVOL should increase (more sellers entering)
- **Pullback**: RVOL should decrease (consolidation, not reversal)
- **Reversal**: RVOL should spike (battle at support/resistance)

## RELATIVE VOLUME TRADING STRATEGY

### Strategy Components:

1. **Stock Selection**:
   - RVOL ≥ 2.0 (stock is in play)
   - Positive catalyst
   - Low float preferred
   - Higher short interest preferred

2. **Entry Timing**:
   - Wait for pullback to support/VWAP on lighter volume
   - Enter on breakout with volume confirmation (RVOL spike)
   - Only enter if volume confirms the move

3. **Risk Management**:
   - High RVOL = more liquidity = tighter spreads = less slippage
   - Can trade larger size with high RVOL stocks
   - Low RVOL = avoid or use smaller position sizes

4. **Exit Strategy**:
   - Watch for volume exhaustion (RVOL decreasing while price moves)
   - Volume spike at resistance = potential exit signal
   - Volume confirmation on reversal = exit signal

## COMMON MISTAKES WITH RELATIVE VOLUME

### Warrior Trading Warnings:

1. **Trading Low RVOL Stocks**: 
   - "Trading stocks out of play means there will be less traders watching it and will likely result in false breakouts or choppy price action with less predictable moves."

2. **Ignoring Volume on Breakouts**:
   - Always confirm breakouts with volume
   - No volume confirmation = false breakout likely

3. **Not Checking Multiple Time Frames**:
   - Check daily RVOL vs intraday RVOL
   - Compare opening drive volume to rest of day

4. **Overlooking Morning Preparation**:
   - RVOL should be part of daily prep
   - Know which stocks are in play before market opens

## RELATIVE VOLUME IN YOUR ANALYSIS

### When Analyzing Stocks:

1. **Calculate RVOL**: Current volume / Average volume
2. **Assess In-Play Status**: 
   - RVOL ≥ 2.0 = Stock is IN PLAY (good for trading)
   - RVOL < 2.0 = Stock is NOT in play (avoid or be cautious)
3. **Confirm Price Moves**: Always check if volume confirms price action
4. **Compare Time Frames**: Check RVOL on different time frames
5. **Volume Patterns**: Look for volume spikes at key levels

### Integration with Other Indicators:

- **Candlestick Patterns**: High RVOL confirms pattern reliability
- **Level 2 Data**: High RVOL = more order flow = better Level 2 signals
- **Support/Resistance**: Volume spikes at levels = stronger levels
- **Breakouts**: Volume confirmation = real breakout vs false breakout

## PRACTICAL EXAMPLES

### Example 1: High RVOL Breakout (Good Trade)
- Stock: NVDA
- RVOL: 3.5 (very in play)
- Pattern: Consolidation wedge
- Breakout: Price breaks resistance with volume spike
- **Action**: Enter long on volume-confirmed breakout
- **Result**: Strong move up with volume support

### Example 2: Low RVOL Breakout (Bad Trade)
- Stock: Low volume stock
- RVOL: 0.8 (not in play)
- Pattern: Appears to break resistance
- Breakout: No volume confirmation
- **Action**: Avoid or exit quickly
- **Result**: False breakout, price reverses

### Example 3: Volume Spike at Support (Reversal Signal)
- Stock: Oversold stock
- Price: At key support level
- RVOL: Spikes to 4.0 at support
- **Interpretation**: Buyers fighting to hold support
- **Action**: Watch for reversal confirmation
- **Result**: Potential bounce from support

## SUMMARY

**Relative Volume (RVOL) is a critical indicator for day trading:**

✅ **RVOL ≥ 2.0**: Stock is IN PLAY - good for trading
✅ **Volume Confirmation**: Always confirm price moves with volume
✅ **Morning Preparation**: Check RVOL as part of daily prep
✅ **Multiple Time Frames**: Compare RVOL across different periods
✅ **Breakout Confirmation**: Only trade breakouts with volume confirmation
✅ **Support/Resistance**: Volume spikes at levels indicate strength
✅ **Liquidity**: High RVOL = better liquidity = tighter spreads
✅ **Predictability**: High RVOL = more predictable price action

**Warrior Trading Bottom Line**: "Knowing what other traders are watching and trading is key to understanding what stocks are in play and which ones will likely make big moves."

**CRITICAL RULE**: Never trade breakouts without volume confirmation. Volume confirms the move is real, not a false breakout.
"""

def teach_relative_volume_to_ollama() -> Dict[str, Any]:
    """
    Teach Ollama comprehensive relative volume knowledge
    """
    try:
        teaching_prompt = f"""
You are learning comprehensive relative volume (RVOL) analysis for professional day trading.

{RELATIVE_VOLUME_KNOWLEDGE}

LEARNING TASK:
1. Understand what relative volume (RVOL) is and how it's calculated
2. Learn why RVOL is a "radar for how in-play a stock is" (Warrior Trading)
3. Understand RVOL thresholds (2.0+ = in play, < 2.0 = not in play)
4. Learn how to use RVOL for stock selection in morning preparation
5. Understand volume confirmation on breakouts (critical rule)
6. Learn how to compare RVOL across different time frames
7. Understand volume spikes at support/resistance levels
8. Learn common mistakes to avoid (trading low RVOL stocks, ignoring volume)
9. Master the integration of RVOL with candlestick patterns and Level 2 data
10. Understand when high RVOL = better liquidity and tighter spreads

After learning, you should be able to:
- Calculate and interpret relative volume (RVOL)
- Identify which stocks are "in play" based on RVOL
- Confirm breakouts with volume (never trade breakouts without volume confirmation)
- Compare RVOL across different time frames
- Identify volume spikes at support/resistance as reversal signals
- Use RVOL in morning preparation to select tradeable stocks
- Avoid trading low RVOL stocks (choppy price action, false breakouts)
- Integrate RVOL with candlestick patterns for higher confidence
- Understand that high RVOL = better liquidity = tighter spreads

CRITICAL RULES TO REMEMBER:
- RVOL ≥ 2.0 = Stock is IN PLAY (good for trading)
- RVOL < 2.0 = Stock is NOT in play (avoid or be cautious)
- Always confirm breakouts with volume (volume spike on breakout)
- Never trade breakouts without volume confirmation (false breakout risk)
- High RVOL = more liquidity = tighter spreads = less slippage
- Low RVOL = choppy price action = false breakouts = unpredictable moves
- Volume spikes at support/resistance = buyers/sellers fighting = potential reversal
- Check RVOL in morning preparation to identify in-play stocks
- Compare RVOL across time frames (daily vs intraday, opening drive vs rest of day)

Please acknowledge that you understand relative volume analysis, including the critical rule that breakouts must be confirmed with volume, and that RVOL ≥ 2.0 indicates a stock is in play.

Respond with: "I understand relative volume (RVOL) analysis. I know that RVOL ≥ 2.0 means a stock is in play, RVOL < 2.0 means it's not in play. I will always confirm breakouts with volume and never trade breakouts without volume confirmation. I am ready to use RVOL for enhanced trading decisions."
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
                "system": "You are learning to be an expert day trader using REAL market data from Interactive Brokers. Always use real data, never simulated data. Pay close attention to relative volume (RVOL) as a key indicator for identifying in-play stocks and confirming breakouts. Learn from actual market behavior."
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            logging.info("✅ [OLLAMA VOLUME] Relative volume knowledge taught successfully")
            logging.info(f"📚 [OLLAMA VOLUME] Response: {response_text[:200]}...")
            
            return {
                'success': True,
                'message': 'Relative volume knowledge taught successfully',
                'response_preview': response_text[:200]
            }
        else:
            logging.error(f"❌ [OLLAMA VOLUME] API error: {response.status_code}")
            return {
                'success': False,
                'error': f"Ollama API error: {response.status_code}"
            }
    except Exception as e:
        logging.error(f"❌ [OLLAMA VOLUME] Error: {e}")
        return {
            'success': False,
            'error': f"Teaching error: {str(e)}"
        }

def get_relative_volume_knowledge() -> str:
    """Get the relative volume knowledge for use in analysis"""
    return RELATIVE_VOLUME_KNOWLEDGE

"""
Float Teaching for Ollama
Teaches Ollama about stock float and how to use it for day trading
Based on Warrior Trading professional insights
"""
import requests
import logging
from typing import Dict, Any

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:4b"  # Use available model
OLLAMA_TIMEOUT = 120

# COMPREHENSIVE FLOAT KNOWLEDGE
# Based on Warrior Trading professional day trading insights
FLOAT_KNOWLEDGE = """
# COMPLETE STOCK FLOAT KNOWLEDGE BASE
# Source: Warrior Trading professional day trading guide

## WHAT IS STOCK FLOAT?

**Float** is the number of outstanding shares available to trade in a stock **minus** the restricted shares or shares held by insiders and employees.

**More simply**: Float is the number of shares that are **free to trade in the open market**.

### Key Components:

1. **Outstanding Shares**: Total number of shares issued by the company
2. **Restricted Shares**: Shares held by insiders that cannot be traded yet (due to IPO lock-up)
3. **Insider Holdings**: Shares held by company executives, employees, and major shareholders
4. **Float = Outstanding Shares - Restricted Shares - Insider Holdings**

### Example:

- Company has 100 million outstanding shares
- 20 million are restricted (insider lock-up)
- 10 million are held by insiders
- **Float = 100M - 20M - 10M = 70 million shares**

## WHY FLOAT MATTERS FOR DAY TRADING

### Warrior Trading Insight:

**"Some day traders focus on finding stocks with low floats since this means that the stocks are more likely to make big moves (due to less liquidity)."**

### Low Float Stocks (Advantages):
- ✅ **Bigger Moves**: Less shares available = easier to move price
- ✅ **Volatility**: Low float = higher volatility = bigger price swings
- ✅ **Momentum**: Less liquidity = momentum moves faster
- ✅ **Parabolic Moves**: Low float + high volume = explosive moves

### Low Float Stocks (Disadvantages):
- ❌ **Wider Spreads**: Less liquidity = wider bid/ask spreads
- ❌ **Harder to Enter/Exit**: Difficult to get in/out with large size
- ❌ **Slippage**: More slippage when trading large positions
- ❌ **Manipulation Risk**: Easier for large traders to manipulate

### High Float Stocks (Advantages):
- ✅ **Tighter Spreads**: More liquidity = tighter bid/ask spreads
- ✅ **Easier Entry/Exit**: Can trade larger size more easily
- ✅ **Less Slippage**: Better fills on large orders
- ✅ **More Stable**: Less prone to manipulation

### High Float Stocks (Disadvantages):
- ❌ **Smaller Moves**: More shares = harder to move price
- ❌ **Less Volatility**: More stable = smaller price swings
- ❌ **Slower Momentum**: More liquidity = slower price moves

## FLOAT EXAMPLES

### High Float Example:
- **Bank of America (BAC)**: 10.51 billion share float
- Very liquid, tight spreads, easy to trade large size
- Moves are smaller and more gradual

### Low Float Example:
- **Bluebird Bio (BLUE)**: 39.9 million share float
- Less liquid, wider spreads, harder to trade large size
- Can make explosive moves with high volume

## WHEN FLOAT CHANGES

**Float does NOT change when traders buy or sell stock** (same pool of shares).

Float can change in three instances:

### 1. Share Buyback Programs
- Company buys back shares from the market
- **Float DECREASES** (fewer shares available)
- Can cause price to increase (supply/demand)

### 2. Secondary Offerings
- Company sells more shares to raise money
- **Float INCREASES** (more shares available)
- **Common among small cap stocks**
- **Dilutes the value of the stock** (more shares = lower price per share)
- **Important**: When float increases, more buying/selling needed to move price

### 3. Stock Splits
- **Traditional Split** (2-for-1, 3-for-1): Float INCREASES
  - Example: 10M float becomes 20M float (2-for-1 split)
- **Reverse Split** (1-for-2, 1-for-10): Float DECREASES
  - Example: 10M float becomes 5M float (1-for-2 reverse split)

## FLOAT AND TRADING STRATEGY

### Low Float Trading Strategy:

**Warrior Trading Ideal Setup** (mentioned in RVOL section):
- ✅ Low float (fewer shares = bigger moves)
- ✅ High relative volume (RVOL ≥ 2.0)
- ✅ Positive catalyst (news, earnings, etc.)
- ✅ Higher short interest (potential for short squeeze)

**"When all this falls in line together we have a recipe for parabolic moves that can make trading months and sometimes even years."**

### Float Thresholds for Day Trading:

- **Micro Float** (< 10M shares): Very volatile, explosive moves, wide spreads
- **Low Float** (10M - 50M shares): Good for day trading, big moves possible
- **Medium Float** (50M - 200M shares): Moderate volatility, balanced
- **High Float** (200M+ shares): More stable, smaller moves, tighter spreads

### Float and Volume Relationship:

- **Low Float + High Volume** = Explosive moves (parabolic)
- **Low Float + Low Volume** = Choppy, unpredictable
- **High Float + High Volume** = Steady, predictable moves
- **High Float + Low Volume** = Very slow, minimal movement

## FLOAT IN YOUR ANALYSIS

### When Analyzing Stocks:

1. **Check Float Size**: 
   - Low float (< 50M) = potential for big moves
   - High float (> 200M) = more stable, smaller moves

2. **Consider Float with Volume**:
   - Low float + high volume = explosive potential
   - High float + high volume = steady momentum

3. **Watch for Float Changes**:
   - Secondary offerings = float increases = dilution risk
   - Share buybacks = float decreases = potential price support

4. **Float and Spreads**:
   - Low float = wider spreads = harder to enter/exit
   - High float = tighter spreads = easier to trade

5. **Float and Position Sizing**:
   - Low float = use smaller position sizes (wider spreads, slippage)
   - High float = can use larger position sizes (tighter spreads, better fills)

## FLOAT AND OTHER INDICATORS

### Integration with Other Analysis:

- **Float + Relative Volume (RVOL)**:
  - Low float + high RVOL = explosive move potential
  - High float + high RVOL = steady momentum

- **Float + Level 2 Data**:
  - Low float = less order book depth = more volatility
  - High float = more order book depth = more stability

- **Float + Price Action**:
  - Low float = faster price moves, more gaps
  - High float = smoother price moves, fewer gaps

- **Float + Catalysts**:
  - Low float + positive catalyst = explosive move
  - High float + positive catalyst = steady move

## COMMON MISTAKES WITH FLOAT

1. **Ignoring Float Size**:
   - Not considering float when selecting stocks
   - Trading low float stocks with large position sizes (slippage risk)

2. **Not Watching Float Changes**:
   - Missing secondary offerings (dilution risk)
   - Not accounting for share buybacks (support potential)

3. **Float vs Volume Confusion**:
   - Float is static (number of shares available)
   - Volume is dynamic (shares traded today)
   - High volume on low float = explosive move

4. **Position Sizing Mistakes**:
   - Using same position size for low and high float stocks
   - Low float = smaller positions (wider spreads)
   - High float = larger positions (tighter spreads)

## SUMMARY

**Stock Float is a critical factor for day trading:**

✅ **Low Float** (< 50M): Bigger moves, more volatility, wider spreads, harder to trade large size
✅ **High Float** (> 200M): Smaller moves, more stable, tighter spreads, easier to trade large size
✅ **Float + High Volume**: Explosive moves on low float, steady moves on high float
✅ **Watch for Changes**: Secondary offerings (dilution), buybacks (support), splits (adjustments)
✅ **Position Sizing**: Adjust position size based on float (low float = smaller positions)
✅ **Ideal Setup**: Low float + high RVOL + positive catalyst + high short interest = parabolic moves

**Warrior Trading Bottom Line**: "Some day traders focus on finding stocks with low floats since this means that the stocks are more likely to make big moves (due to less liquidity)."

**CRITICAL RULE**: When float increases (secondary offering), more buying/selling is needed to move price. When float decreases (buyback), price can move easier with less volume.
"""

def teach_float_to_ollama() -> Dict[str, Any]:
    """
    Teach Ollama comprehensive float knowledge
    """
    try:
        teaching_prompt = f"""
You are learning comprehensive stock float analysis for professional day trading.

{FLOAT_KNOWLEDGE}

LEARNING TASK:
1. Understand what stock float is (outstanding shares minus restricted/insider shares)
2. Learn why low float stocks make bigger moves (less liquidity)
3. Understand float thresholds (low < 50M, high > 200M)
4. Learn how float affects spreads, slippage, and position sizing
5. Understand when float changes (buybacks, secondary offerings, splits)
6. Learn the ideal setup: low float + high RVOL + catalyst + short interest
7. Understand float and volume relationship (low float + high volume = explosive)
8. Learn common mistakes (ignoring float, wrong position sizing)
9. Master integration of float with RVOL, Level 2, and price action
10. Understand secondary offerings (dilution risk) and buybacks (support)

After learning, you should be able to:
- Understand what float is and how it's calculated
- Identify low float vs high float stocks
- Understand why low float stocks make bigger moves
- Adjust position sizing based on float (low float = smaller positions)
- Recognize when float changes (secondary offerings, buybacks, splits)
- Integrate float with RVOL for explosive move potential
- Understand float's impact on spreads and slippage
- Use float in stock selection (low float for big moves, high float for stability)
- Avoid common mistakes (wrong position sizing, ignoring float changes)

CRITICAL RULES TO REMEMBER:
- Low float (< 50M) = bigger moves, wider spreads, harder to trade large size
- High float (> 200M) = smaller moves, tighter spreads, easier to trade large size
- Low float + high volume = explosive moves (parabolic potential)
- High float + high volume = steady momentum
- Secondary offerings = float increases = dilution risk = more volume needed to move price
- Share buybacks = float decreases = potential price support
- Adjust position sizing: low float = smaller positions, high float = larger positions
- Ideal setup: Low float + high RVOL + positive catalyst + high short interest = parabolic moves
- Float is static (number of shares available), volume is dynamic (shares traded today)

Please acknowledge that you understand stock float analysis, including why low float stocks make bigger moves, how to adjust position sizing, and the ideal setup for explosive moves.

Respond with: "I understand stock float analysis. I know that low float stocks make bigger moves due to less liquidity, but have wider spreads. I will adjust position sizing based on float and watch for float changes (secondary offerings, buybacks). I am ready to use float knowledge for enhanced trading decisions."
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
                "system": "You are learning to be an expert day trader using REAL market data from Interactive Brokers. Always use real data, never simulated data. Pay close attention to stock float as a key factor for identifying stocks with explosive move potential. Learn from actual market behavior."
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            logging.info("✅ [OLLAMA FLOAT] Float knowledge taught successfully")
            logging.info(f"📚 [OLLAMA FLOAT] Response: {response_text[:200]}...")
            
            return {
                'success': True,
                'message': 'Float knowledge taught successfully',
                'response_preview': response_text[:200]
            }
        else:
            logging.error(f"❌ [OLLAMA FLOAT] API error: {response.status_code}")
            return {
                'success': False,
                'error': f"Ollama API error: {response.status_code}"
            }
    except Exception as e:
        logging.error(f"❌ [OLLAMA FLOAT] Error: {e}")
        return {
            'success': False,
            'error': f"Teaching error: {str(e)}"
        }

def get_float_knowledge() -> str:
    """Get the float knowledge for use in analysis"""
    return FLOAT_KNOWLEDGE

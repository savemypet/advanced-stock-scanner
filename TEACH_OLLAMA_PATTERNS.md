# Teaching Ollama All Candlestick Patterns

## Overview

This guide explains how to teach Ollama all 36+ candlestick patterns from your codebase.

## Quick Start

### Method 1: Via Settings Panel (Recommended)

1. Open the app
2. Click **Settings** button
3. Click **AI Training** tab
4. Click **"Teach All Patterns"** button
5. Wait 30-60 seconds for teaching to complete

### Method 2: Via API Endpoint

```bash
curl -X POST http://localhost:5000/api/ollama/teach-all
```

### Method 3: Python Script

```python
from ollama_patterns_teaching import teach_all_patterns_to_ollama

result = teach_all_patterns_to_ollama()
print(result)
```

## What Gets Taught

### Single Candle Patterns (8)
1. **HAMMER** - Bullish reversal
2. **INVERTED_HAMMER** - Potential bullish reversal
3. **DRAGONFLY_DOJI** - Bullish reversal
4. **BULLISH_SPINNING_TOP** - Weak bullish
5. **SHOOTING_STAR** - Bearish reversal
6. **HANGING_MAN** - Bearish signal
7. **GRAVESTONE_DOJI** - Bearish reversal
8. **BEARISH_SPINNING_TOP** - Weak bearish

### Double Candle Patterns (10)
9. **BULLISH_ENGULFING** - Strong buy signal
10. **BEARISH_ENGULFING** - Strong sell signal
11. **BULLISH_HARAMI** - Potential reversal
12. **BEARISH_HARAMI** - Potential reversal
13. **PIERCING_LINE** - Bullish reversal
14. **DARK_CLOUD_COVER** - Bearish reversal
15. **BULLISH_KICKER** - Extremely strong reversal
16. **BEARISH_KICKER** - Extremely strong reversal
17. **TWEEZER_BOTTOM** - Support level
18. **TWEEZER_TOP** - Resistance level

### Triple Candle Patterns (14)
19. **MORNING_STAR** - Strong bullish reversal
20. **EVENING_STAR** - Strong bearish reversal
21. **MORNING_DOJI_STAR** - Very strong bullish reversal
22. **EVENING_DOJI_STAR** - Very strong bearish reversal
23. **BULLISH_ABANDONED_BABY** - Extremely rare, very strong
24. **BEARISH_ABANDONED_BABY** - Extremely rare, very strong
25. **THREE_WHITE_SOLDIERS** - Strong uptrend
26. **THREE_BLACK_CROWS** - Strong downtrend
27. **THREE_INSIDE_UP** - Bullish confirmation
28. **THREE_INSIDE_DOWN** - Bearish confirmation
29. **THREE_OUTSIDE_UP** - Strong bullish signal
30. **THREE_OUTSIDE_DOWN** - Strong bearish signal

### Four Candle Patterns (2)
31. **BULLISH_THREE_LINE_STRIKE** - Powerful continuation
32. **BEARISH_THREE_LINE_STRIKE** - Powerful continuation

### Neutral Patterns (4)
33. **DOJI** - Indecision
34. **SPINNING_TOP** - Indecision
35. **MARUBOZU** - Strong momentum
36. **STAR** - Component of star patterns

## Pattern Details Taught

For each pattern, Ollama learns:
- **Visual characteristics** (body size, shadow length, etc.)
- **Signal type** (BUY/SELL/HOLD)
- **Confidence levels** (HIGH/MEDIUM/LOW)
- **Volume requirements** (2x+ for high confidence)
- **Context requirements** (support/resistance, trend)
- **Reliability factors**
- **When to use** (trend conditions, market context)

## Teaching Process

1. **Comprehensive Library**: All 36+ patterns with detailed descriptions
2. **Visual Characteristics**: Exact measurements and ratios
3. **Context Rules**: When patterns are most reliable
4. **Volume Confirmation**: How volume affects confidence
5. **Trend Context**: How trend direction affects pattern meaning
6. **Risk Management**: How to calculate entry/stop/target

## Verification

After teaching, test Ollama by:
1. Opening a stock with clear patterns
2. Clicking "Analyze" in AI Analysis section
3. Checking if Ollama identifies patterns correctly
4. Verifying confidence levels match pattern strength

## Troubleshooting

### Teaching Fails
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Check model is installed: `ollama list`
- Increase timeout if needed

### Patterns Not Recognized
- Re-teach patterns: Click "Teach All Patterns" again
- Check Ollama response in backend logs
- Verify pattern library is loaded

### Analysis Quality Poor
- Ensure teaching completed successfully
- Try different model (mistral, codellama)
- Check if patterns match codebase definitions

## Files

- **`backend/ollama_patterns_teaching.py`** - Complete pattern library
- **`backend/ollama_service.py`** - Uses pattern library in analysis
- **`frontend/src/components/OllamaTeaching.tsx`** - UI component
- **`frontend/src/components/SettingsPanel.tsx`** - Settings integration

## Next Steps

After teaching:
1. Ollama will use all patterns in analysis
2. Analysis will be more accurate
3. Pattern recognition will improve
4. Confidence levels will be more precise

---

**Last Updated:** 2026-01-23  
**Status:** ✅ Ready to teach all patterns

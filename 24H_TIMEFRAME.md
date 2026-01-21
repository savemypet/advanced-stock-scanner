# 24-Hour (Daily) Timeframe

## Overview
The **24h timeframe** shows **daily candles** spanning the last **3 months**, giving you a macro view of price trends and patterns.

---

## 📊 **What You Get:**

### **Data Range:**
```yaml
Interval: 1 day (24 hours) per candle
Period: Last 3 months (~90 days)
Candles: ~90 daily candles
Best For: Long-term trends, swing trading, pattern analysis
```

### **Each Candle Represents:**
```yaml
Open: Opening price at market open (9:30 AM ET)
High: Highest price during the trading day
Low: Lowest price during the trading day
Close: Closing price at market close (4:00 PM ET)
Volume: Total volume traded that day
Time: One full trading day
```

---

## 🎯 **Use Cases:**

### **1. Trend Analysis:**
```yaml
See 3-month price trends:
  ✅ Uptrend: Higher highs, higher lows
  ✅ Downtrend: Lower highs, lower lows
  ✅ Sideways: Range-bound movement
  ✅ Breakouts: Price breaking key levels
```

### **2. Support & Resistance:**
```yaml
Identify key levels:
  ✅ Support: Price bounces repeatedly
  ✅ Resistance: Price fails to break through
  ✅ Round numbers: $50, $100, etc.
  ✅ Previous highs/lows
```

### **3. Pattern Recognition:**
```yaml
Spot chart patterns:
  ✅ Head & Shoulders
  ✅ Double Tops/Bottoms
  ✅ Triangles (ascending, descending, symmetrical)
  ✅ Flags & Pennants
  ✅ Channels
```

### **4. Volume Confirmation:**
```yaml
Validate price moves:
  ✅ Volume increase on breakout = strong
  ✅ Volume decrease on pullback = healthy
  ✅ High volume spikes = interest/news
  ✅ Low volume = weak move
```

---

## 💡 **How to Use in Modal:**

### **Quick Analysis Workflow:**
```
1. Scanner finds stock (e.g., GME up 12.5%)
2. Click stock card
3. Modal opens with 5m chart (current move)
4. Click "1m" → See minute-by-minute detail
5. Click "1h" → See hourly trend today
6. Click "24h" → See 3-month context ✅
7. Analyze:
   - Is today's move part of bigger trend?
   - At support or resistance?
   - Volume confirming or diverging?
   - Pattern forming?
```

---

## 📈 **Example Scenarios:**

### **Scenario 1: Breakout Confirmation**
```yaml
GME shows +12.5% gain today

Check 24h chart:
  → Stock was in downtrend for 2 months
  → Today broke above $45 resistance
  → Volume is 3x recent average
  → Bullish engulfing candle forming

Conclusion:
  ✅ Strong breakout candidate
  ✅ High conviction trade
  ✅ Volume confirms
```

### **Scenario 2: False Breakout**
```yaml
AMC shows +15% gain today

Check 24h chart:
  → Stock at 3-month resistance ($8)
  → Failed to break this level 5 times before
  → Volume lower than previous attempts
  → Long upper wick (rejection)

Conclusion:
  ❌ Likely false breakout
  ❌ Consider waiting
  ❌ Watch for pullback
```

### **Scenario 3: Trend Continuation**
```yaml
TSLA shows +8% gain today

Check 24h chart:
  → Strong uptrend for 6 weeks
  → Price pulling back to 20-day support
  → Today's green candle bouncing from support
  → Volume average (healthy)

Conclusion:
  ✅ Trend continuation
  ✅ Buy the dip opportunity
  ✅ Support holding
```

---

## 🔍 **What to Look For:**

### **Bullish Signals:**
```yaml
✅ Price making higher highs & higher lows
✅ Breaking above resistance with volume
✅ Bouncing off support levels
✅ Green candles with long lower wicks (support)
✅ Volume increasing on up days
✅ Moving above key moving averages
```

### **Bearish Signals:**
```yaml
❌ Price making lower highs & lower lows
❌ Failing at resistance levels
❌ Breaking below support with volume
❌ Red candles with long upper wicks (rejection)
❌ Volume increasing on down days
❌ Moving below key moving averages
```

---

## ⚡ **Instant Switching:**

### **No API Calls:**
```yaml
When Scanner Runs:
  → Fetches 24h data for qualifying stocks
  → Stores locally in stock.chartData['24h']
  → ~90 daily candles (~5 KB per stock)

When You Click "24h":
  → Reads from memory (instant)
  → No network request
  → No loading delay
  → 0ms switch time ✅
```

---

## 📊 **Compare Timeframes:**

### **1m - Ultra Short-Term:**
```yaml
Period: Last 1 day
Interval: 1 minute
Use: Scalping, day trading
View: Micro movements
```

### **5m - Short-Term:**
```yaml
Period: Last 5 days
Interval: 5 minutes
Use: Day trading, quick swings
View: Intraday trends
```

### **1h - Medium-Term:**
```yaml
Period: Last 1 month
Interval: 1 hour
Use: Swing trading
View: Daily trends
```

### **24h - Long-Term:**
```yaml
Period: Last 3 months
Interval: 1 day
Use: Position trading, trend analysis
View: Macro trends ✅
```

---

## 🎨 **Visual Example:**

### **1m Chart (Micro View):**
```
Price: $45.50 → $45.80 (tiny moves)
View: Last 6 hours, very granular
```

### **5m Chart (Intraday View):**
```
Price: $45.00 → $46.50 (today's range)
View: Last 5 days, intraday patterns
```

### **1h Chart (Daily View):**
```
Price: $40.00 → $46.50 (this week)
View: Last month, daily trends
```

### **24h Chart (Macro View):**
```
Price: $20.00 → $46.50 (3-month rally)
View: Last 3 months, big picture ✅
```

---

## 🚀 **Why It's Useful:**

### **Context:**
```yaml
✅ See if today's move is significant
✅ Understand bigger trend
✅ Identify key levels
✅ Spot patterns
```

### **Confidence:**
```yaml
✅ Validate short-term signals with long-term trend
✅ Avoid false breakouts
✅ Find better entries
✅ Improve timing
```

### **Risk Management:**
```yaml
✅ Identify stop-loss levels (support)
✅ Set profit targets (resistance)
✅ Understand risk/reward
✅ Avoid chasing tops
```

---

## 📋 **Quick Reference:**

### **Timeframe Selection Guide:**
```yaml
Scalping (<1 hour):      Use 1m
Day Trading (today):     Use 5m
Swing Trading (days):    Use 1h
Position Trading (weeks): Use 24h ✅

General Analysis:
  → Start with 24h (macro context)
  → Zoom to 1h (daily trend)
  → Zoom to 5m (current move)
  → Zoom to 1m (entry timing)
```

---

## 🎯 **Best Practices:**

### **1. Always Check Multiple Timeframes:**
```
24h → Is there a bigger trend?
1h  → Is today confirming or reversing?
5m  → Is current move strong?
1m  → Best entry point?
```

### **2. Use Volume for Confirmation:**
```
24h volume spikes = significant events
Compare today's volume to 90-day average
```

### **3. Identify Key Levels:**
```
Find 3-month highs/lows on 24h chart
Mark support/resistance zones
Watch for breakouts
```

### **4. Combine with Other Timeframes:**
```
24h shows uptrend → Look for 1h pullbacks
24h shows support → Look for 5m bounce
24h shows breakout → Look for 1m entry
```

---

## 💡 **Pro Tips:**

```yaml
Tip 1: Check 24h FIRST
  → Gives context to today's move
  → Prevents chasing false breakouts
  → Shows bigger picture

Tip 2: Look for Confluence
  → 24h support + 1h support = strong level
  → 24h resistance + 5m rejection = exit signal
  → Multiple timeframe alignment = high probability

Tip 3: Use for Swing Trades
  → 24h perfect for multi-day holds
  → Identify trend direction
  → Set wider stops at daily support

Tip 4: Pattern Recognition
  → Patterns more reliable on higher timeframes
  → 24h patterns = bigger targets
  → Wait for daily close confirmation
```

---

## ✅ **Summary:**

The **24h timeframe** provides:

```yaml
✅ 3-month daily candle view
✅ Macro trend analysis
✅ Support/resistance identification
✅ Pattern recognition
✅ Volume confirmation
✅ Context for short-term moves
✅ Better trade decisions
✅ Risk management tool

Access:
  → Click any stock
  → Click "24h" button
  → Instant display (0ms)
  → No API calls
```

---

**Use 24h to see the big picture, then zoom to shorter timeframes for timing! 📊📈🎯**

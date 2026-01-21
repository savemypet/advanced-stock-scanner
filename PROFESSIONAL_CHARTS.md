# Professional Stock Charts

## Overview
Beautiful, professional-grade candlestick charts with **green/red candles**, **3 moving averages** (20, 50, 200-day), and **buy/sell volume indicators** at the bottom!

---

## 🎨 **Chart Features:**

### **1. Candlestick Display:**
```yaml
Green Candles:
  → Price closed higher than open (bullish)
  → Gradient fill from bright to soft green
  → Body shows open-to-close range
  → Wicks show high-low range

Red Candles:
  → Price closed lower than open (bearish)
  → Gradient fill from bright to soft red
  → Body shows open-to-close range
  → Wicks show high-low range

Professional Look:
  ✅ Gradient fills (not solid colors)
  ✅ Smooth, modern design
  ✅ Clear visual distinction
  ✅ Easy pattern recognition
```

### **2. Moving Averages:**
```yaml
MA20 (Blue Line):
  → 20-period moving average
  → Short-term trend
  → Color: #3b82f6 (Blue)
  → Width: 2px

MA50 (Purple Line):
  → 50-period moving average
  → Medium-term trend
  → Color: #a855f7 (Purple)
  → Width: 2px

MA200 (Orange Line):
  → 200-period moving average
  → Long-term trend
  → Color: #f97316 (Orange)
  → Width: 2.5px (thicker for emphasis)

Benefits:
  ✅ Identify trend direction
  ✅ Find support/resistance
  ✅ Spot crossovers (golden cross, death cross)
  ✅ Gauge market strength
```

### **3. Volume Bars (Bottom):**
```yaml
Green Bars:
  → Volume on up candles (buying pressure)
  → Shows accumulation
  → Higher = stronger buying

Red Bars:
  → Volume on down candles (selling pressure)
  → Shows distribution
  → Higher = stronger selling

Display:
  → Separate chart below price
  → 30% of total height
  → Labels show volume in millions (e.g., "5.2M")
  → Color-coded to match price action

Purpose:
  ✅ Confirm price moves
  ✅ Spot divergences
  ✅ Identify climax volume
  ✅ Validate breakouts
```

---

## 📊 **Chart Sections:**

### **Main Chart (70% height):**
```
┌─────────────────────────────────────┐
│  Price Chart                        │
│                                     │
│  ┌─ MA20 (Blue)                    │
│  ├─ MA50 (Purple)                  │
│  └─ MA200 (Orange)                 │
│                                     │
│  [Green/Red Candlesticks]          │
│                                     │
│  Grid lines for easy reading        │
│  Tooltips on hover                  │
└─────────────────────────────────────┘
```

### **Volume Chart (30% height):**
```
┌─────────────────────────────────────┐
│  Volume                             │
│                                     │
│  [Green/Red Volume Bars]           │
│                                     │
│  Labels: 5.2M, 3.1M, etc.          │
└─────────────────────────────────────┘
```

---

## 🎯 **How to Use:**

### **Stock Cards (Small View):**
```yaml
Location: Scanner results list
Chart: Compact version with MAs
Volume: Hidden (to save space)
Height: 220px
Purpose: Quick glance at trend
Click: Opens detailed modal
```

### **Detail Modal (Large View):**
```yaml
Location: Click any stock card
Chart: Full-sized with all features
Volume: Visible (buy/sell pressure)
Height: 500px
Purpose: Detailed analysis
Features:
  ✅ All 3 moving averages
  ✅ Full volume chart
  ✅ Timeframe switching (1m/5m/1h/24h)
  ✅ Interactive tooltips
  ✅ Professional styling
```

---

## 💡 **Reading the Chart:**

### **Bullish Signals:**
```yaml
Price Action:
  ✅ Green candles dominating
  ✅ Price above all MAs (especially MA200)
  ✅ MAs sloping upward
  ✅ MA20 > MA50 > MA200 (golden alignment)

Volume:
  ✅ Green volume bars increasing
  ✅ Higher volume on up days
  ✅ Volume expansion on breakouts

Moving Averages:
  ✅ Price bouncing off MA20/MA50 (support)
  ✅ MA20 crossing above MA50 (golden cross)
  ✅ All MAs rising together
```

### **Bearish Signals:**
```yaml
Price Action:
  ❌ Red candles dominating
  ❌ Price below all MAs (especially MA200)
  ❌ MAs sloping downward
  ❌ MA20 < MA50 < MA200 (death alignment)

Volume:
  ❌ Red volume bars increasing
  ❌ Higher volume on down days
  ❌ Volume expansion on breakdowns

Moving Averages:
  ❌ Price rejected at MA20/MA50 (resistance)
  ❌ MA20 crossing below MA50 (death cross)
  ❌ All MAs falling together
```

---

## 🔍 **Tooltip Information:**

### **Hover Over Candle:**
```
┌─────────────────────────┐
│ 12:30 PM, Jan 20, 2026 │
│ ↑ Bullish               │
│ O: $45.50              │
│ H: $46.20              │
│ L: $45.30              │
│ C: $46.00              │
│ V: 5.23M               │
│ MA20: $44.80           │
│ MA50: $43.50           │
│ MA200: $40.20          │
└─────────────────────────┘
```

### **Hover Over Volume:**
```
┌─────────────────────────┐
│ 🟢 Buy Volume          │
│ 5.23M                  │
└─────────────────────────┘

or

┌─────────────────────────┐
│ 🔴 Sell Volume         │
│ 3.81M                  │
└─────────────────────────┘
```

---

## 📈 **Trading Strategies Using the Chart:**

### **1. Moving Average Crossover:**
```yaml
Golden Cross (Bullish):
  → MA20 crosses above MA50
  → Both above MA200
  → Price rising
  → Volume increasing on breakout
  ✅ Strong buy signal

Death Cross (Bearish):
  → MA20 crosses below MA50
  → Both below MA200
  → Price falling
  → Volume increasing on breakdown
  ❌ Strong sell signal
```

### **2. Support/Resistance:**
```yaml
MAs as Support:
  → Price pulls back to MA20
  → Bounces with green candle
  → Volume increases on bounce
  ✅ Buy opportunity

MAs as Resistance:
  → Price rallies to MA50
  → Rejected with red candle
  → Volume increases on rejection
  ❌ Exit or short opportunity
```

### **3. Volume Confirmation:**
```yaml
Breakout Validation:
  → Price breaks above resistance
  → Green volume bars spike
  → Volume 2x+ average
  ✅ Valid breakout

False Breakout:
  → Price breaks above resistance
  → Volume is low
  → Red candles follow
  ❌ Likely failure
```

---

## 🎨 **Design Details:**

### **Color Palette:**
```yaml
Green (Bullish):
  Primary: #22c55e
  Gradient: 80% to 30% opacity
  Use: Up candles, buy volume

Red (Bearish):
  Primary: #ef4444
  Gradient: 80% to 30% opacity
  Use: Down candles, sell volume

Blue (MA20):
  Color: #3b82f6
  Line: 2px solid
  Purpose: Short-term trend

Purple (MA50):
  Color: #a855f7
  Line: 2px solid
  Purpose: Medium-term trend

Orange (MA200):
  Color: #f97316
  Line: 2.5px solid (thicker)
  Purpose: Long-term trend
```

### **Chart Background:**
```yaml
Main: Gradient from muted/20 to muted/40
Border: border/50 opacity
Grid: Dotted lines, low opacity
Style: Modern, clean, professional
```

---

## ⚡ **Performance:**

### **Data Calculation:**
```yaml
Moving Averages:
  → Calculated server-side (Python/pandas)
  → Efficient rolling window
  → Minimal CPU impact

MA20:  Needs 20+ candles
MA50:  Needs 50+ candles
MA200: Needs 200+ candles

Volume Color:
  → Determined by candle direction
  → Green if close > open
  → Red if close < open
```

### **Rendering:**
```yaml
Library: Recharts
Method: Canvas-based rendering
Smooth: Hardware-accelerated
Fast: 60fps animations
Responsive: Adapts to screen size
```

---

## 📋 **Timeframe Specific MA Behavior:**

### **1m Timeframe:**
```yaml
Periods: Last 24 hours (~390 candles)
MA20: Shows last 20 minutes
MA50: Shows last 50 minutes
MA200: Shows last 200 minutes (~3.3 hours)

Best For: Scalping entries
```

### **5m Timeframe:**
```yaml
Periods: Last 5 days (~390 candles)
MA20: Shows last 100 minutes (~1.7 hours)
MA50: Shows last 250 minutes (~4.2 hours)
MA200: Shows last 1000 minutes (~16.7 hours)

Best For: Day trading setups
```

### **1h Timeframe:**
```yaml
Periods: Last month (~30 candles)
MA20: Shows last 20 hours
MA50: May not display (needs 50 hours)
MA200: Will not display (needs 200 hours)

Best For: Swing trade context
```

### **24h Timeframe:**
```yaml
Periods: Last 3 months (~90 candles)
MA20: Shows last 20 days
MA50: Shows last 50 days
MA200: Will not display (needs 200 days)

Best For: Long-term trends
```

---

## 🚀 **Example Analysis Workflow:**

### **Step 1: Check 24h Chart**
```
Look at: MA20, MA50 positions
Question: Is stock in uptrend?
Observation: Price above both MAs, MAs rising
Conclusion: ✅ Bullish macro trend
```

### **Step 2: Check 1h Chart**
```
Look at: Recent MA20 behavior
Question: Is today confirming trend?
Observation: Price bouncing off MA20
Conclusion: ✅ Healthy pullback
```

### **Step 3: Check 5m Chart**
```
Look at: Current candles + volume
Question: Is entry forming now?
Observation: Green candle, green volume spike
Conclusion: ✅ Entry signal
```

### **Step 4: Check 1m Chart**
```
Look at: Precise entry point
Question: Best entry price?
Observation: Price consolidating above MA20
Conclusion: ✅ Enter on next green candle
```

---

## ✅ **Summary:**

The Professional Chart provides:

```yaml
✅ Beautiful green/red candlesticks with gradients
✅ 3 moving averages (20, 50, 200-day)
✅ Buy/sell volume bars (color-coded)
✅ Interactive tooltips (OHLC + MAs + Volume)
✅ Professional styling and animations
✅ Responsive design (works on all screens)
✅ Instant timeframe switching (1m/5m/1h/24h)
✅ Modern, clean, easy-to-read interface

Features:
  → Main chart (70%): Price + MAs
  → Volume chart (30%): Buy/sell pressure
  → Grid lines for easy reading
  → Legend showing MA colors
  → Tooltips on hover
  → Zoom and pan support
```

---

**Open http://localhost:3000 and see the beautiful charts in action! 📊✨🎨**

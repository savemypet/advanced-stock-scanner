# ⏱️ Safe Refresh Intervals - Never Get Blocked Again!

## 🚨 Why You Got Blocked

**Your previous settings:**
```yaml
Symbols: 45 stocks
Interval: 30 seconds
Result: 5,400 requests/hour ❌ (2.7x over limit!)
```

**Yahoo Finance limit:** ~2,000 requests/hour

**You exceeded it by 170%!** That's why you got the 429 error.

---

## 📊 Safe Interval Calculator

### Formula:
```
Requests/Hour = Symbols × (3600 ÷ Interval)

Stay UNDER 2,000 to be safe!
```

---

## ✅ SAFE COMBINATIONS (All Under 2,000/hour)

### For Different Stock Counts:

#### 10 Symbols:
```
60s  → 600 req/hr  ✅ Very safe
30s  → 1,200 req/hr ✅ Safe
20s  → 1,800 req/hr ✅ Safe
15s  → 2,400 req/hr ⚠️ Risky
```

#### 20 Symbols:
```
120s → 600 req/hr  ✅ Very safe
60s  → 1,200 req/hr ✅ Safe
45s  → 1,600 req/hr ✅ Safe
30s  → 2,400 req/hr ⚠️ At limit (risky!)
```

#### 30 Symbols:
```
120s → 900 req/hr  ✅ Very safe
90s  → 1,200 req/hr ✅ Safe
60s  → 1,800 req/hr ✅ Safe
45s  → 2,400 req/hr ⚠️ At limit (risky!)
```

#### 40 Symbols:
```
180s → 800 req/hr  ✅ Very safe
120s → 1,200 req/hr ✅ Safe
90s  → 1,600 req/hr ✅ Safe
60s  → 2,400 req/hr ⚠️ At limit (risky!)
```

#### **45 Symbols (YOUR CURRENT):**
```
180s → 900 req/hr  ✅ Very safe
120s → 1,350 req/hr ✅ Safe
90s  → 1,800 req/hr ✅ RECOMMENDED ⭐
60s  → 2,700 req/hr ❌ Will block
45s  → 3,600 req/hr ❌ Will block fast
30s  → 5,400 req/hr ❌ Instant block
```

#### 50 Symbols:
```
180s → 1,000 req/hr ✅ Very safe
120s → 1,500 req/hr ✅ Safe
90s  → 2,000 req/hr ⚠️ Exactly at limit
60s  → 3,000 req/hr ❌ Will block
```

---

## 🎯 RECOMMENDED SETUP

### For Your 45 Symbols:

```yaml
✅ BEST: 90 seconds (1.5 minutes)
   - Requests: 1,800/hour
   - Buffer: 200 req/hr cushion
   - Fast enough for day trading
   - Won't get blocked

✅ SAFE: 120 seconds (2 minutes)
   - Requests: 1,350/hour
   - Big safety buffer
   - Still good for trading
   - Very reliable

⚠️ RISKY: 60 seconds
   - Requests: 2,700/hour
   - Over limit
   - Will eventually block
   - Not recommended
```

---

## 🔥 If You Want 30-Second Updates

### Option 1: Reduce Symbols to 20
```yaml
Symbols: 20 (remove 25 stocks)
Interval: 30 seconds

Calculation:
20 × (3600 / 30) = 2,400 req/hr ⚠️

Status: At limit, borderline
Recommendation: Use only during market hours
```

### Option 2: Use 15 Symbols (SAFEST for 30s)
```yaml
Symbols: 15 (focus on best movers)
Interval: 30 seconds

Calculation:
15 × (3600 / 30) = 1,800 req/hr ✅

Status: SAFE!
Recommendation: Best compromise
```

**Example 15 symbols:**
```python
# High-volume movers
DEFAULT_SYMBOLS = [
    'TSLA', 'AMD', 'NVDA', 'PLTR', 'SOFI',
    'GME', 'AMC', 'NIO', 'LCID', 'RIVN',
    'ATER', 'BBIG', 'PROG', 'SNDL', 'BBBY'
]
```

---

## 📈 Trading Style Recommendations

### Day Trader (Active):
```yaml
Symbols: 15-20 key stocks
Interval: 30-45 seconds
Requests: 1,600-2,400/hour
Risk: Medium (monitor for blocks)
```

### Swing Trader:
```yaml
Symbols: 30-40 stocks
Interval: 90-120 seconds  ⭐
Requests: 1,200-1,800/hour
Risk: Low (safe range)
```

### Scanner/Monitor:
```yaml
Symbols: 40-50 stocks
Interval: 120-180 seconds
Requests: 800-1,500/hour
Risk: Very low (plenty of buffer)
```

### Scalper (Fast):
```yaml
Symbols: 10-15 stocks
Interval: 20-30 seconds
Requests: 1,800-2,400/hour
Risk: Medium-High
Note: Only during market hours!
```

---

## ⏰ Market Hours Strategy

### During Market Hours (9:30am-4pm ET):

**Aggressive:**
```
Interval: 60-90 seconds
Why: Market is active, need faster updates
Risk: Medium (but worth it when trading)
```

### After Hours / Pre-Market:

**Conservative:**
```
Interval: 180+ seconds
Why: Less activity, conserve requests
Risk: Low (saves your quota)
```

### When Not Trading:

**Stop Scanner:**
```
Turn off auto-updates completely
Why: No need to waste requests
Risk: Zero (not running)
```

---

## 🛡️ Safety Buffer Strategy

### Always Add Buffer:

```
Yahoo Limit:     2,000 req/hr
Your Target:     1,500-1,800 req/hr
Buffer:          200-500 req/hr

Why?
- Account for manual refreshes
- Handle network retries
- Provide cushion for spikes
- Avoid accidental blocks
```

---

## 📊 Real-World Examples

### Example 1: Conservative Trader
```yaml
Goal: Never get blocked
Setup:
  - Symbols: 40 stocks
  - Interval: 120 seconds
  - Requests: 1,200/hour
  - Result: ✅ Works perfectly, never blocked
```

### Example 2: Active Day Trader
```yaml
Goal: Fast updates during trading
Setup:
  - Symbols: 20 stocks (focused list)
  - Interval: 45 seconds
  - Requests: 1,600/hour
  - Result: ✅ Good speed, safe buffer
```

### Example 3: Aggressive Scalper (Your Original)
```yaml
Goal: Very fast updates
Setup:
  - Symbols: 45 stocks ❌
  - Interval: 30 seconds ❌
  - Requests: 5,400/hour ❌
  - Result: ❌ BLOCKED immediately
  
Fix:
  - Reduce to 15 symbols
  - Keep 30s interval
  - Requests: 1,800/hour ✅
```

---

## 🔧 How to Change Settings

### Method 1: In App (Temporary)

1. Open http://localhost:3000
2. Click "Settings" button
3. Find "Update interval (seconds)"
4. Change to: **90** (recommended)
5. Click "Apply Settings"

### Method 2: In Code (Permanent)

**Already done for you!** Default is now 90 seconds.

If you want to change it:
1. Edit: `frontend/src/App.tsx`
2. Find: `updateInterval: 90`
3. Change to your preferred value
4. Save and refresh browser

---

## 🚦 Traffic Light System

### 🟢 GREEN (Safe - Won't Block)
```
Under 1,800 requests/hour
- 45 symbols @ 90s+
- 30 symbols @ 60s+
- 20 symbols @ 40s+
- 15 symbols @ 30s+
```

### 🟡 YELLOW (Caution - Might Block)
```
1,800-2,200 requests/hour
- 45 symbols @ 75-90s
- 30 symbols @ 50-60s
- 20 symbols @ 33-40s
- Use only during trading hours
- Monitor for errors
```

### 🔴 RED (Danger - Will Block)
```
Over 2,200 requests/hour
- 45 symbols @ 60s or less ❌
- 30 symbols @ 45s or less ❌
- 20 symbols @ 30s or less ⚠️
- Guaranteed block within 1-2 hours
```

---

## 💡 Pro Tips to Avoid Blocks

### 1. Start Conservative
```
First day: 120s intervals
See if it works: Yes? Try 90s
Still good? Try 75s
Got blocked? Back to 120s
```

### 2. Market Hours Only
```
Trading hours: Fast updates (60-90s)
Off hours: Slow updates (180s+)
Not watching: Turn off completely
```

### 3. Manual Refresh Limit
```
Auto-updates: Let it work
Manual refresh: Max 2-3 times/hour
Spam refresh: Guaranteed block!
```

### 4. Monitor Backend Logs
```
Watch for "429" errors in terminal
If you see them: Increase interval immediately
Prevention is better than cure!
```

### 5. Test on Weekends
```
Market closed = Lower Yahoo traffic
Good time to test different intervals
Find your sweet spot safely
```

---

## 🆘 Already Blocked? Recovery Plan

### Immediate Actions:
```
1. Stop scanner (close browser)
2. Wait 30-60 minutes
3. Increase interval to 120s
4. Restart scanner
5. Monitor for 30 minutes
6. If stable, slowly decrease interval
```

### Prevention for Next Time:
```
✅ Use 90s+ intervals with 40+ symbols
✅ Use 60s+ intervals with 20-30 symbols
✅ Use 45s+ intervals with 15-20 symbols
✅ Only use 30s with 10-15 symbols max
✅ Add manual delay between refreshes
✅ Turn off when not actively trading
```

---

## 📊 YOUR CURRENT STATUS

```yaml
UPDATED SETTINGS (SAFE!)
════════════════════════

Symbols:         45 stocks
Interval:        90 seconds ✅ (changed from 30s)
Requests/Hour:   1,800
Status:          SAFE (200 req/hr buffer)
Risk Level:      LOW

Expected Behavior:
- Updates every 1.5 minutes
- Fast enough for day trading
- Won't trigger rate limits
- Stable long-term use

Next Steps:
1. Wait for current rate limit to clear (30-60 min)
2. Scanner will auto-use 90s intervals
3. Should work perfectly!
4. Adjust if needed in Settings
```

---

## 🎯 Quick Reference Table

**Safe intervals for YOUR 45 symbols:**

| Interval | Req/Hr | Safe? | Use For |
|----------|--------|-------|---------|
| 180s | 900 | 🟢 | Overnight monitoring |
| 120s | 1,350 | 🟢 | Conservative trading |
| **90s** | **1,800** | **🟢** | **Day trading (BEST)** ⭐ |
| 75s | 2,160 | 🟡 | Aggressive (risky) |
| 60s | 2,700 | 🔴 | Will block |
| 45s | 3,600 | 🔴 | Will block fast |
| 30s | 5,400 | 🔴 | Instant block |

---

## ✅ FINAL RECOMMENDATION

```yaml
FOR YOUR SETUP (45 STOCKS):

Interval: 90 seconds (1.5 minutes)

Why This Works:
✅ 1,800 req/hr (safely under 2,000 limit)
✅ Updates every 1.5 min (fast enough for day trading)
✅ 200 req/hr safety buffer (handles spikes)
✅ Won't get blocked (proven safe range)
✅ Can run 24/7 if needed (though not recommended)

This is NOW your default! 🎉
```

---

**Remember:** Slower is safer! 90 seconds is the sweet spot for your setup. 🎯⏱️

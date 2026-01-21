# 🎯 Filter Settings Guide - Why You're Not Seeing Stocks

## 🚨 Problem: Empty Scanner Results

If you're seeing **"No Stocks Found"**, here's why and how to fix it:

---

## 📊 Understanding Your Filters

### Current UPDATED Settings (More Forgiving):

```yaml
BALANCED SETTINGS (Shows More Stocks)
═══════════════════════════════════════

Price Range:     $1 - $20  ✅ Good range
Max Float:       100M shares  ✅ Wider net
Min Gain:        2%  ✅ Shows activity  
Volume:          1.5x average  ✅ Normal activity
Display Count:   5 stocks
```

### Previous Settings (TOO STRICT):

```yaml
EXTREME SETTINGS (Very Few Results)
═══════════════════════════════════

Price Range:     $1 - $20
Max Float:       10M shares  ⚠️ SUPER RARE
Min Gain:        10%  ⚠️ HIGH BAR
Volume:          4x average  ⚠️ EXPLOSIVE ONLY
```

---

## 🎛️ Filter Impact Explained

### Max Float (Stock Share Supply)

| Setting | Impact | Result |
|---------|--------|--------|
| **10M** | 🔥 EXTREME | 0-2 stocks (super rare) |
| **50M** | 🔥 Aggressive | 2-5 stocks |
| **100M** | ✅ Balanced | 5-15 stocks |
| **500M** | ✅ Relaxed | 15-30 stocks |
| **1B+** | ✅ Wide | 20-40 stocks |

**Your OLD setting:** 10M = Almost NOTHING qualifies!
**Your NEW setting:** 100M = More reasonable

### Min Gain % (Momentum Filter)

| Setting | Impact | Result |
|---------|--------|--------|
| **15%+** | 🔥 Major moves only | Very few |
| **10%** | 🔥 Strong moves | Few stocks |
| **5%** | ✅ Good moves | Moderate |
| **2%** | ✅ Any movement | Many stocks |
| **1%** | ✅ Slight moves | Most stocks |

**Your OLD setting:** 10% = Only big movers
**Your NEW setting:** 2% = Shows activity

### Volume Multiplier (Interest Level)

| Setting | Impact | Result |
|---------|--------|--------|
| **5x+** | 🔥 Viral/Squeeze | Extremely rare |
| **4x** | 🔥 Explosive | Very rare |
| **3x** | 🔥 Strong | Rare |
| **2x** | ✅ Good | Common |
| **1.5x** | ✅ Moderate | Very common |
| **1x** | ✅ Normal | All stocks |

**Your OLD setting:** 4x = Only explosive volume
**Your NEW setting:** 1.5x = Shows normal activity

---

## 🎯 Recommended Settings by Goal

### For TESTING (See Results Now):

```yaml
Good for verifying scanner works:

Price:    $1 - $50
Float:    1,000,000,000 (1 billion)
Gain:     1%
Volume:   1x
Result:   Should show 10-30 stocks
```

### For DAY TRADING (Balanced):

```yaml
Real trading setup:

Price:    $1 - $20
Float:    100,000,000 (100M)
Gain:     5%
Volume:   2x
Result:   5-15 quality stocks
```

### For AGGRESSIVE SCALPING:

```yaml
High risk/reward:

Price:    $1 - $10
Float:    20,000,000 (20M)
Gain:     10%
Volume:   3x
Result:   0-5 elite setups
```

### For LOW-FLOAT HUNTING (Original Goal):

```yaml
Explosive potential:

Price:    $1 - $20
Float:    10,000,000 (10M)
Gain:     10%
Volume:   4x
Result:   0-3 rare opportunities
⚠️ May show NOTHING for hours!
```

---

## 🕐 Market Hours Matter!

### Why You See No Stocks:

**Market Closed (After 4pm ET):**
```
- Pre-market: 4am - 9:30am ET
- Regular: 9:30am - 4pm ET  ← Best time
- After-hours: 4pm - 8pm ET

If market closed:
→ Data is stale
→ Volume is low
→ Gains reset to 0%
→ Scanner finds NOTHING
```

**Solution:**
- Run scanner during 9:30am - 4pm ET
- Or lower filters to see previous day's data

---

## 🔧 How to Adjust Filters

### Step-by-Step:

1. **Open Scanner** - http://localhost:3000

2. **Click "Settings"** (top right)

3. **Find "Stock Criteria"** section

4. **Adjust These:**

   **Max Float:**
   ```
   Current: 100,000,000
   
   More stocks:    500,000,000 or 1,000,000,000
   Fewer stocks:   50,000,000 or 10,000,000
   ```

   **Min Gain %:**
   ```
   Current: 2
   
   More stocks:    1 or 0.5
   Fewer stocks:   5, 10, or 15
   ```

   **Volume Multiplier:**
   ```
   Current: 1.5
   
   More stocks:    1.0
   Fewer stocks:   2.0, 3.0, or 4.0
   ```

5. **Click "Apply Settings"**

6. **Wait 30 seconds** for next scan

---

## 📊 Real-Time Checker

### Is Your Scanner Working?

**Check These:**

✅ **Backend Running?**
```
Open: http://localhost:5000/api/health
Should show: {"status": "healthy"}
```

✅ **Frontend Loading?**
```
Open: http://localhost:3000
Should show: Scanner interface
```

✅ **Scanning Active?**
```
Look for: "Scanning Markets..." or countdown timer
```

✅ **Filters Too Strict?**
```
Try: Reset to Default in Settings
Then: Gradually make stricter
```

---

## 🎮 Quick Fixes

### Problem: "No Stocks Found"

**Fix 1: Lower ALL Filters**
```
Settings → Reset → Apply
This sets balanced defaults
```

**Fix 2: Check Market Hours**
```
Current time: After 4pm ET?
→ Market is closed
→ Lower min gain to 0.5%
```

**Fix 3: Increase Float Limit**
```
Settings → Max Float → 500,000,000
→ Way more stocks qualify
```

**Fix 4: Decrease Volume Requirement**
```
Settings → Volume Multiplier → 1.0
→ Shows all stocks
```

**Fix 5: Decrease Gain Requirement**
```
Settings → Min Gain % → 0
→ Shows ALL movement
```

---

## 🧪 Testing Mode

### Want to See Results RIGHT NOW?

**Ultra-Relaxed Settings:**

1. Open Settings
2. Set these values:

```
Price:           $1 - $100
Max Float:       10,000,000,000 (10 billion)
Min Gain:        -50% (negative OK!)
Volume:          0.1x (any volume)
Display Count:   10
```

3. Click Apply
4. Should show 10+ stocks immediately!

Once working, gradually increase strictness:
- First raise volume to 1x
- Then raise gain to 1%
- Then lower float to 500M
- Keep adjusting until you see 5-10 stocks

---

## 📈 Filter Strategy

### The Goldilocks Approach:

```
TOO LOOSE:
- 50+ stocks showing
- Most are garbage
- Hard to focus

TOO STRICT:
- 0 stocks showing  ← YOUR PROBLEM
- Missing opportunities
- Scanner looks broken

JUST RIGHT:
- 3-10 stocks showing
- All are quality
- Easy to monitor
```

**Goal:** Find the balance where you see 5-10 stocks consistently.

---

## 🎯 Current Market Reality

### Low-Float + High-Volume is RARE:

```
Total US Stocks:     ~7,000
Low-float (<100M):   ~1,500
With 4x volume:      ~50
With 10% gain:       ~5
Meets ALL criteria:  0-3 stocks

THIS IS NORMAL!
```

**Your old filters** were looking for:
- Top 0.1% of stocks
- May not exist on given day
- Could be 0 results for days

**Your new filters** look for:
- Top 5% of stocks
- Should find 5-15 daily
- Better for consistent trading

---

## 💡 Pro Tips

### 1. Start Wide, Then Narrow

```
Week 1: Max Float 1B, Gain 1%, Volume 1x
Week 2: Max Float 500M, Gain 2%, Volume 1.5x
Week 3: Max Float 100M, Gain 5%, Volume 2x
Week 4: Max Float 50M, Gain 10%, Volume 3x
```

### 2. Different Filters for Different Times

```
Morning (9:30-11am):
- Tightest filters
- Best opportunities
- Max Float 50M, Gain 10%, Volume 3x

Afternoon (11am-3pm):
- Moderate filters
- Steady scanning
- Max Float 100M, Gain 5%, Volume 2x

Power Hour (3-4pm):
- Looser filters
- Catch late movers
- Max Float 200M, Gain 3%, Volume 1.5x
```

### 3. Save Multiple Profiles (Future Feature)

```
Profile 1: "Testing" (wide)
Profile 2: "Day Trading" (balanced)
Profile 3: "Scalping" (aggressive)
Profile 4: "Low-Float Hunter" (extreme)
```

---

## 🚨 Common Mistakes

### ❌ Don't Do This:

1. **Set ALL filters to maximum strictness**
   - Result: 0 stocks forever
   - Fix: Start balanced

2. **Never adjust filters**
   - Result: Miss opportunities
   - Fix: Adjust based on market

3. **Expect stocks when market closed**
   - Result: Frustration
   - Fix: Check market hours

4. **Think scanner is broken when 0 results**
   - Result: Waste time debugging
   - Fix: Just lower filters!

---

## ✅ Success Checklist

**Your Scanner is Working IF:**

- [ ] Backend shows "healthy" at /api/health
- [ ] Frontend loads at localhost:3000
- [ ] You see countdown timer
- [ ] You see "Scanning Markets..." initially
- [ ] With WIDE filters (Float 1B, Gain 1%), you see stocks
- [ ] You can open Settings and change values
- [ ] After clicking Apply, new scan starts

**If ALL above = ✅ then scanner works!**
**Problem is just FILTER SETTINGS!**

---

## 🎉 Your NEW Settings Summary

```yaml
UPDATED TO BALANCED DEFAULTS
═══════════════════════════════

Max Float:       100M shares (vs 10M)
Min Gain:        2% (vs 10%)
Volume:          1.5x (vs 4x)

Expected Result: 5-15 stocks during market hours

To go back to extreme mode:
Settings → Set 10M float, 10% gain, 4x volume
(But expect 0-2 results!)
```

---

**Scanner is WORKING - just need the right filter balance! 🎯📈**

**Quick test:** Set Max Float to 1,000,000,000 and Min Gain to 0% → Should see many stocks!

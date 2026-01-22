# How Stock Selection Works - Preset Filtering

## ✅ Yes! If a stock matches ALL your presets, it gets picked!

## 🔍 How It Works

### Step 1: Scanner Checks Each Stock
For each stock in your scan list:
1. Fetches data from IBKR (price, volume, charts, etc.)
2. Gets float data from Massive.com (if available)
3. Applies ALL your preset filters

### Step 2: Filter Checks (ALL Must Pass)
A stock is picked ONLY if it passes **ALL** of these:

1. **Price Check** ✅
   - `minPrice <= currentPrice <= maxPrice`
   - Example: If you set $1-$20, stock must be between $1 and $20

2. **Float Check** ✅
   - `float <= maxFloat`
   - Example: If you set 10M max, stock float must be ≤ 10M
   - Note: Only works if Massive.com provides float data

3. **Gain Check** ✅
   - `changePercent >= minGainPercent`
   - Example: If you set 10%, stock must be up 10% or more

4. **Volume Check** ✅
   - `currentVolume >= (avgVolume × volumeMultiplier)`
   - Example: If you set 2x, current volume must be 2× average volume

### Step 3: Stock Gets Picked
If **ALL 4 checks pass**:
- ✅ Stock is added to results
- ✅ Stock is added to `active_symbols` (auto-tracking)
- ✅ Stock is added to `daily_discovered_stocks` (for AI learning)
- ✅ Stock appears in your scanner results

## 📊 Example

**Your Presets:**
- Price: $1 - $20
- Float: ≤ 10,000,000
- Gain: ≥ 10%
- Volume: ≥ 2.0x average

**Stock: GME**
- Price: $15.50 ✅ (between $1-$20)
- Float: 8,500,000 ✅ (≤ 10M)
- Gain: +12.5% ✅ (≥ 10%)
- Volume: 2.5× average ✅ (≥ 2.0x)

**Result:** ✅ **GME gets picked!**

## 🔄 Auto-Tracking

### Active Symbols (`active_symbols`)
- Stocks that pass your filters are **automatically added**
- These stocks are scanned in **future scans**
- List grows as scanner finds qualifying stocks
- Starts with `SEED_SYMBOLS` (GME, AMC, TSLA, etc.)

### Daily Discovered (`daily_discovered_stocks`)
- Stocks discovered today that match your criteria
- Used for AI learning
- Reset each day
- Only stocks that pass ALL filters

## 🎯 Does IBKR "Know" Which Stocks You Want?

**Short Answer:** Not exactly, but the system tracks them automatically.

**How It Works:**
1. **You set presets** (price, float, gain, volume)
2. **Scanner checks stocks** from `active_symbols` list
3. **IBKR fetches data** for each stock
4. **Filters are applied** to the IBKR data
5. **Qualifying stocks** are automatically added to `active_symbols`
6. **Next scan** includes these new stocks automatically

**IBKR's Role:**
- IBKR provides the data (price, volume, charts)
- Your scanner applies the filters
- Qualifying stocks are tracked automatically
- IBKR doesn't "know" your preferences, but the scanner does!

## 📈 Flow Diagram

```
1. Scanner starts with active_symbols list
   ↓
2. For each stock:
   - Fetch data from IBKR
   - Get float from Massive.com
   ↓
3. Apply ALL preset filters:
   - Price check ✅
   - Float check ✅
   - Gain check ✅
   - Volume check ✅
   ↓
4. If ALL pass:
   - Add to results ✅
   - Add to active_symbols ✅
   - Add to daily_discovered ✅
   - AI learns from it ✅
   ↓
5. Next scan includes new stocks automatically
```

## ✅ Summary

**Question:** If everything matches my presets, will it pick that stock?

**Answer:** ✅ **YES!**

- If a stock passes **ALL 4 filters** (price, float, gain, volume)
- It gets **automatically picked**
- It's added to **active_symbols** (tracked for future scans)
- It's added to **daily_discovered** (for AI learning)
- **IBKR doesn't "know"** your preferences, but the scanner tracks qualifying stocks automatically

**The scanner automatically finds and tracks stocks that match your criteria!** 🎯

# 🔑 AlphaVantage API Setup

## Overview

Your Advanced Stock Scanner now has **3-layer API fallback** with AlphaVantage as the third safety net!

```
1️⃣ Yahoo Finance (FREE, unlimited)
    ↓ (if rate limited)
2️⃣ SerpAPI (250 calls/month)
    ↓ (if quota exhausted)
3️⃣ AlphaVantage (500 calls/day)
    ↓ (if quota exhausted)
🔄 Back to Yahoo Finance (after 2 hours)
```

---

## 🎯 Why AlphaVantage?

### **Benefits:**
- ✅ **FREE tier**: 500 API calls per day
- ✅ **Real-time data**: Accurate stock quotes
- ✅ **No credit card**: Completely free
- ✅ **Simple setup**: Just need an API key
- ✅ **Third safety net**: When Yahoo & SerpAPI both fail

### **Limitations:**
- ⚠️ 500 calls/day limit (resets daily)
- ⚠️ No company name in basic quotes
- ⚠️ No float/shares outstanding data
- ⚠️ Limited intraday data in free tier

---

## 📝 How To Get Your FREE API Key

### **Step 1: Visit AlphaVantage**
Go to: https://www.alphavantage.co/support/#api-key

### **Step 2: Claim Your Free API Key**
1. Enter your email address
2. Check "I agree to the Terms of Service"
3. Click **"GET FREE API KEY"**
4. You'll receive your key instantly (no email verification needed!)

### **Step 3: Copy Your API Key**
Example key format: `ABC123DEF456GHI789JKL012MNO345`
- 32 characters
- Mix of letters and numbers
- Keep it secret!

---

## 🔧 Installation

### **Step 1: Open `backend/app.py`**

### **Step 2: Find Line 38** (AlphaVantage Configuration section):

```python
# AlphaVantage Configuration (Third fallback when SerpAPI exhausted)
ALPHAVANTAGE_KEY = 'YOUR_ALPHAVANTAGE_API_KEY'  # ← Replace this
ALPHAVANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
ALPHAVANTAGE_FREE_LIMIT = 500  # Daily free tier limit
```

### **Step 3: Replace `YOUR_ALPHAVANTAGE_API_KEY`** with your actual key:

```python
ALPHAVANTAGE_KEY = 'ABC123DEF456GHI789JKL012MNO345'  # ← Your key here
```

### **Step 4: Save the file**

### **Step 5: Restart the backend**

```bash
# Kill existing Python process
taskkill /F /IM python.exe

# Start backend
cd C:\Users\derri\advanced-stock-scanner\backend
python app.py
```

---

## 🧪 Testing

### **Test AlphaVantage is Working:**

1. **Exhaust Yahoo** (scan multiple times until locked)
2. **Exhaust SerpAPI** (use 250/250 calls)
3. **Watch backend logs:**

```
INFO: 🔍 Fetching data for TSLA (timeframe: 5m)
INFO: 🌐 Using Yahoo Finance for TSLA
ERROR: 429 Client Error: Too Many Requests
WARNING: 🔒 Yahoo Finance LOCKED!
INFO: 🌐 Using SerpAPI for TSLA
WARNING: ⚠️ SerpAPI quota exhausted (250/250)
INFO: 🌐 Using AlphaVantage for TSLA (Yahoo locked: True, SerpAPI: 250/250)
INFO: 🔍 AlphaVantage call #1/500 today (499 remaining)
INFO: 🔍 Fetching TSLA from AlphaVantage...
INFO: ✅ Successfully fetched TSLA from AlphaVantage: $423.24 (+2.04%)
```

---

## 📊 Usage Tracking

### **Backend Logs Show:**

```
🔍 AlphaVantage call #1/500 today (499 remaining)
🔍 AlphaVantage call #2/500 today (498 remaining)
🔍 AlphaVantage call #3/500 today (497 remaining)
...
```

### **API Response Includes:**

```json
{
  "stocks": [...],
  "apiStatus": {
    "yahooLocked": true,
    "yahooUnlockAt": "2026-01-21T14:18:00",
    "serpapiQuota": {
      "used": 250,
      "limit": 250,
      "remaining": 0
    },
    "alphavantageQuota": {
      "used": 15,
      "limit": 500,
      "remaining": 485
    },
    "activeSource": "AlphaVantage",
    "fallbackAvailable": true
  }
}
```

---

## 🔄 Smart Switching Logic

### **Automatic Fallback Flow:**

```
User clicks "Scan"
    ↓
Try Yahoo Finance
    ├─► ✅ Success → Return data
    └─► ❌ Fail (429) → Lock Yahoo for 2 hours
        ↓
Try SerpAPI
    ├─► ✅ Success → Return data
    ├─► ❌ No data → Try AlphaVantage
    └─► ❌ Quota exhausted (250/250) → Try AlphaVantage
        ↓
Try AlphaVantage
    ├─► ✅ Success → Return data
    └─► ❌ Quota exhausted (500/500) → All APIs unavailable
        ↓
Error: "All APIs unavailable"
Wait for Yahoo unlock (2 hours)
```

---

## ⚡ Performance Tips

### **Optimize API Usage:**

1. **Use Penny Stocks preset** - Scans fewer symbols
2. **Increase scan interval** - 30-60s instead of 20s
3. **Reduce display count** - Show 5-10 stocks instead of 20
4. **Monitor quota** - Check `apiStatus` in response

### **Daily Limits:**

| API | Limit | Reset | Cost |
|-----|-------|-------|------|
| **Yahoo Finance** | ~60/min | Continuous | FREE |
| **SerpAPI** | 250/month | Monthly (1st) | FREE |
| **AlphaVantage** | 500/day | Daily (midnight) | FREE |

**Total FREE calls per day:**
- Yahoo: ~86,400 calls (60/min × 1440 min)
- SerpAPI: ~8 calls/day (250/30 days)
- AlphaVantage: 500 calls/day

**= 86,908 FREE API calls per day!** 🎉

---

## 🔐 Security

### **Keep Your Keys Safe:**

❌ **DON'T:**
- Commit API keys to GitHub
- Share keys publicly
- Hard-code keys in frontend

✅ **DO:**
- Keep keys in `backend/app.py` only
- Add `app.py` to `.gitignore` (optional)
- Use environment variables for production

### **Environment Variables (Optional):**

```python
# backend/app.py
import os

ALPHAVANTAGE_KEY = os.getenv('ALPHAVANTAGE_KEY', 'YOUR_ALPHAVANTAGE_API_KEY')
```

Then set in PowerShell:
```powershell
$env:ALPHAVANTAGE_KEY = "ABC123DEF456GHI789JKL012MNO345"
```

---

## 🐛 Troubleshooting

### **Issue 1: "AlphaVantage key not configured"**

**Solution:**
```python
# Make sure you replaced this:
ALPHAVANTAGE_KEY = 'YOUR_ALPHAVANTAGE_API_KEY'

# With your actual key:
ALPHAVANTAGE_KEY = 'ABC123DEF456GHI789JKL012MNO345'
```

### **Issue 2: "AlphaVantage quota exhausted (500/500)"**

**Solution:**
- Wait until midnight (daily reset)
- System will auto-switch back to Yahoo (if unlocked)
- Quota resets at **12:00 AM your timezone**

### **Issue 3: "AlphaVantage returned no quote data"**

**Solution:**
- Check stock symbol is valid (e.g., TSLA, not TSLA:NASDAQ)
- Some penny stocks may not be available
- System will auto-skip and continue scan

### **Issue 4: Rate limit errors from AlphaVantage**

**Solution:**
- Free tier: 5 API calls per minute max
- System automatically tracks usage
- If you hit rate limit, wait 1 minute
- System will retry automatically

---

## 📈 Real-World Example

### **Scenario: Heavy Trading Day**

**9:30 AM - Market Open:**
- ✅ Using Yahoo Finance (fast, unlimited)
- Scanning every 20 seconds

**10:15 AM - Yahoo Rate Limited:**
- ❌ Yahoo locked (too many scans)
- 🔄 Auto-switched to SerpAPI
- ✅ Using SerpAPI (250 calls/month)

**2:45 PM - SerpAPI Exhausted:**
- ❌ SerpAPI 250/250 calls used
- 🔄 Auto-switched to AlphaVantage
- ✅ Using AlphaVantage (500 calls/day)

**3:55 PM - AlphaVantage Exhausted:**
- ❌ AlphaVantage 500/500 calls used
- ⏰ Waiting for Yahoo unlock (12:15 PM - 2 hours)

**12:15 PM - Yahoo Unlocked:**
- 🔓 Yahoo unlocked automatically
- 🔄 Auto-switched back to Yahoo
- ✅ Scanning resumed!

**Midnight - Quotas Reset:**
- 📊 SerpAPI: Stays at 250 used (resets next month)
- 📊 AlphaVantage: Resets to 0/500 ✅
- 🎉 Full quota available tomorrow!

---

## 🎉 Summary

✅ **Added AlphaVantage as 3rd fallback**
✅ **500 free calls per day**
✅ **Automatic switching between 3 APIs**
✅ **Complete documentation provided**
✅ **Usage tracking implemented**
✅ **Security best practices included**

**Next Step:** Get your FREE API key and paste it into `backend/app.py`! 🚀

---

**Get Your Key:** https://www.alphavantage.co/support/#api-key
**Documentation:** https://www.alphavantage.co/documentation/
**Support:** https://www.alphavantage.co/support/

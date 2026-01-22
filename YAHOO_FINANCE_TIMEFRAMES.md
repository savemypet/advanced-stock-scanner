# 📊 Yahoo Finance Available Timeframes

## **Currently Implemented:**

| Timeframe | Period | Interval | Status |
|-----------|--------|----------|--------|
| 1m | 1d | 1m | ✅ Implemented |
| 3m | 5d | 2m | ✅ Implemented |
| 5m | 5d | 5m | ✅ Implemented |
| 15m | 5d | 15m | ✅ Implemented |
| 30m | 5d | 30m | ✅ Implemented |
| 1h | 1mo | 1h | ✅ Implemented |
| 24h | 3mo | 1d | ✅ Implemented |
| 1month | 2y | 1mo | ✅ Implemented |

---

## **Available from Yahoo Finance (Not Yet Added):**

### **Intraday Timeframes:**
| Timeframe | Period | Interval | Max History | Notes |
|-----------|--------|----------|-------------|-------|
| **2m** | 5d | 2m | ~7 days | ⚠️ Minute data limited to 7 days |
| **90m** | 60d | 90m | 60 days | 90-minute candles |

### **Daily & Longer Timeframes:**
| Timeframe | Period | Interval | Max History | Notes |
|-----------|--------|----------|-------------|-------|
| **1week** | max | 1wk | Full history | Weekly candles |
| **3month** | max | 3mo | Full history | Quarterly candles |
| **6month** | 1y | 1d | 1 year | 6-month view with daily candles |
| **1year** | 1y | 1d | 1 year | Yearly view with daily candles |
| **2year** | 2y | 1d | 2 years | 2-year view with daily candles |
| **5year** | 5y | 1d | 5 years | 5-year view with daily candles |
| **10year** | 10y | 1d | 10 years | 10-year view with daily candles |
| **max** | max | 1d | All history | Maximum available history |

### **Special Periods:**
| Timeframe | Period | Interval | Description |
|-----------|--------|----------|-------------|
| **ytd** | ytd | 1d | Year-to-date (from January 1st) |

---

## **Yahoo Finance Limitations:**

### **Intraday Data (Minute/Hour Intervals):**
- ⚠️ **1m, 2m intervals**: Limited to ~7 days of history
- ⚠️ **5m, 15m, 30m, 60m, 90m intervals**: Limited to 60 days of history
- ✅ **Daily and longer intervals**: Full historical data available

### **Period + Interval Combinations:**
- Must match: e.g., `period='1d'` with `interval='1m'` works
- Cannot exceed: e.g., `period='1y'` with `interval='1m'` will fail (use `interval='1d'`)

---

## **Recommended Additions:**

### **High Priority (Most Useful):**
1. **1week** - Weekly candles (full history)
   - Great for swing trading
   - Shows weekly patterns
   - Full historical data

2. **1year** - Yearly view with daily candles
   - Long-term trend analysis
   - 1 year of daily data

3. **5year** - 5-year view with daily candles
   - Very long-term analysis
   - Shows major trends

### **Medium Priority:**
4. **2m** - 2-minute candles
   - More granular than 5m
   - Limited to 7 days

5. **90m** - 90-minute candles
   - Between 1h and daily
   - 60 days max

6. **ytd** - Year-to-date
   - Shows performance since Jan 1
   - Useful for annual tracking

### **Low Priority:**
7. **3month** - Quarterly candles
   - Less common timeframe
   - Full history available

8. **6month** - 6-month view
   - Similar to 3mo but different period

9. **2year, 10year, max** - Extended history
   - For very long-term analysis

---

## **Implementation Notes:**

### **For Intraday (< 1 day):**
```python
period_map = {
    '2m': '5d',    # Max 7 days
    '90m': '60d',  # Max 60 days
}
interval_map = {
    '2m': '2m',
    '90m': '90m',
}
```

### **For Daily & Longer:**
```python
period_map = {
    '1week': 'max',    # Full history
    '1year': '1y',     # 1 year
    '5year': '5y',     # 5 years
    'ytd': 'ytd',      # Year-to-date
}
interval_map = {
    '1week': '1wk',    # Weekly candles
    '1year': '1d',     # Daily candles
    '5year': '1d',     # Daily candles
    'ytd': '1d',       # Daily candles
}
```

---

## **Summary:**

**Total Available:** 20+ timeframes  
**Currently Implemented:** 8 timeframes  
**Can Add:** 12+ additional timeframes  

**Best to Add First:**
1. ✅ **1week** (weekly candles - very useful)
2. ✅ **1year** (yearly view - popular)
3. ✅ **5year** (long-term analysis)
4. ✅ **ytd** (year-to-date tracking)

---

**Status:** Ready to implement any of these timeframes! 🚀

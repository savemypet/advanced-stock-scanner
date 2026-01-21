# 📰 Stock News Search Feature

## **Overview:**

The backend automatically searches the internet for news on stocks that qualify in the scanner, sends push notifications, and logs news in the app.

---

## **How It Works:**

### **1. Automatic News Search:**
- When stocks qualify in the scanner, the backend automatically searches for news
- Uses SerpAPI (if configured) or Google News RSS (free fallback)
- News is cached for 1 hour to reduce API calls

### **2. Push Notifications:**
- When news is found, OneSignal push notification is sent (if userId provided)
- Notification includes: stock symbol, news count, latest article title
- User can click notification to view news in app

### **3. News Logging:**
- All news is stored in database (in-memory, can be moved to SQLite/Redis)
- News is filtered by ticker and date (only shows today's news)
- News persists for the day and can be viewed in the app

---

## **API Endpoints:**

### **1. Get News for Symbol (Today's News):**
```
GET /api/stocks/news/:symbol
GET /api/stocks/news/:symbol?date=2026-01-21
```

**Response:**
```json
{
  "success": true,
  "symbol": "TSLA",
  "date": "2026-01-21",
  "newsCount": 5,
  "news": [
    {
      "id": "news-TSLA-...",
      "symbol": "TSLA",
      "title": "Tesla announces new model",
      "source": "Reuters",
      "url": "https://...",
      "snippet": "...",
      "publishedAt": "2026-01-21T10:00:00Z",
      "foundAt": "2026-01-21T10:05:00Z"
    }
  ]
}
```

### **2. Search News (Manual Search + Notification):**
```
POST /api/stocks/news/:symbol/search
Body: {
  "userId": "+1234567890",  // Optional: OneSignal user ID
  "sendNotification": true  // Optional: Send push notification
}
```

**Response:**
```json
{
  "success": true,
  "symbol": "TSLA",
  "newsCount": 5,
  "news": [...],
  "notificationSent": true,
  "notificationId": "..."
}
```

### **3. Get All News Today:**
```
GET /api/stocks/news/all
```

**Response:**
```json
{
  "success": true,
  "date": "2026-01-21",
  "symbols": ["TSLA", "GME", "AMC"],
  "newsBySymbol": {
    "TSLA": [...],
    "GME": [...],
    "AMC": [...]
  }
}
```

---

## **Frontend Integration:**

### **News Section Component:**
- Displays all news found today for stocks that qualified
- Shows news grouped by ticker symbol
- Each news item is clickable (opens in new tab)
- Shows source, date, and snippet

### **Stock Detail Modal:**
- Automatically fetches and displays news when modal opens
- News is shown in the modal's news section

---

## **Configuration:**

### **Environment Variables (Optional):**
```env
# SerpAPI (optional - more reliable, requires API key)
SERPAPI_KEY=your_serpapi_key_here

# If not set, uses Google News RSS (free, no API key needed)
```

### **OneSignal Setup:**
- Already configured in your backend
- Uses existing OneSignal credentials
- Push notifications work automatically

---

## **Features:**

✅ **Automatic News Search** - Searches when stocks qualify  
✅ **Push Notifications** - Alerts when news is found  
✅ **News Logging** - Stores news by ticker and date  
✅ **Today's News Only** - Filters to show only today's news  
✅ **Caching** - 1-hour cache reduces API calls  
✅ **Multiple Sources** - SerpAPI or Google News  
✅ **Frontend Display** - News section in app  

---

## **Usage:**

### **Automatic (Recommended):**
1. Stock qualifies in scanner
2. Backend automatically searches for news
3. If news found and userId provided → Push notification sent
4. News appears in "News Found Today" section

### **Manual Search:**
1. Click "Search News" button in NewsSection
2. Backend searches internet for news
3. Push notification sent (if userId provided)
4. News appears in app

---

## **Example Flow:**

```
1. Scanner finds TSLA qualifies (price up 15%)
2. Backend automatically searches: "TSLA stock news"
3. Finds 5 news articles
4. Sends push notification: "📰 5 News Articles Found: TSLA"
5. News stored in database
6. User opens app → Sees news in "News Found Today" section
7. User clicks stock → Modal shows news for that ticker
```

---

## **Benefits:**

- 📰 **Stay Informed** - Get news on stocks you're watching
- 🔔 **Real-time Alerts** - Push notifications when news breaks
- 📊 **Organized** - News grouped by ticker and date
- 🚀 **Automatic** - No manual searching needed
- 💾 **Persistent** - News logged for the day

---

**Status:** ✅ Implemented and ready to use!

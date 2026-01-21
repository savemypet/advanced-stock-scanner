from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
from typing import List, Dict, Any
import logging
import requests

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Finnhub API Configuration
FINNHUB_API_KEY = 'd5nsql9r01qma2b65ef0d5nsql9r01qma2b65efg'
FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'

# Finnhub FREE Tier Limits:
# - 60 API calls per minute
# - Safe rate: 1 call per second (with buffer)
# - Monthly limit: ~30,000 calls (varies by endpoint)
FINNHUB_RATE_LIMIT_DELAY = 1.5  # 1.5 seconds between calls (safer than 1 second)

# ScraperAPI Configuration (Fallback for Yahoo Finance rate limits)
SCRAPERAPI_KEY = 'd787516e0bbe1264e92e43db77a12244'  # ScraperAPI key configured ✅
SCRAPERAPI_BASE_URL = 'http://api.scraperapi.com'
SCRAPERAPI_FREE_LIMIT = 1000  # Monthly free tier limit

# SerpAPI Configuration (Alternative data source when Yahoo is blocked)
SERPAPI_KEY = '76b777fb92f33e02aeff118d208fa182414297f1249715b1d262571a82ec245c'  # SerpAPI key configured ✅
SERPAPI_BASE_URL = 'https://serpapi.com/search'
SERPAPI_FREE_LIMIT = 250  # Monthly free tier limit

# AlphaVantage Configuration (Third fallback when SerpAPI exhausted)
ALPHAVANTAGE_KEY = 'ED8M1QO531HEYLOS'  # AlphaVantage API key configured ✅
ALPHAVANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
ALPHAVANTAGE_FREE_LIMIT = 25  # Daily free tier limit (25 API calls per day)

# Massive.com Configuration (Fourth fallback - high frequency backup)
MASSIVE_KEY = 'B29V_lqg13rHpwpflNgsxBimbiTVHqe9'  # Massive.com API key configured ✅
MASSIVE_BASE_URL = 'https://api.massive.com/v1'  # Placeholder URL (adjust based on actual API docs)
MASSIVE_RATE_LIMIT = 5  # Free tier: 5 API calls per minute
MASSIVE_RATE_WINDOW = 60  # 60 seconds (1 minute)

# Smart API switching - automatically rotates between Yahoo, SerpAPI, and AlphaVantage
use_yahoo_locked = False  # Yahoo Finance locked status
yahoo_locked_until = None  # When Yahoo unlocks
proxy_calls_used = 0  # Track monthly usage (not used anymore)
proxy_calls_reset_date = None  # Reset counter monthly

# Smart fallback system (AUTO SWITCH)
FORCE_SERPAPI_MODE = False  # Let system auto-choose based on availability

# AlphaVantage usage tracking
alphavantage_calls_used = 0  # Track daily usage
alphavantage_calls_reset_date = None  # Reset counter daily

# Massive.com usage tracking (rate limiting per minute)
massive_calls_history = []  # Track timestamps of API calls
massive_calls_lock = threading.Lock()  # Thread-safe access

# SerpAPI tracking
use_serpapi_mode = False  # Switch to True when Yahoo + ScraperAPI both fail
serpapi_calls_used = 0  # Track monthly usage
serpapi_calls_reset_date = None  # Reset counter monthly

# In-memory cache for stock data and news
stock_cache = {}
news_cache = {}  # Stores news fetched at 4 AM
news_fetched_today = False  # Track if we already fetched news today
last_news_fetch_date = None  # Track the date of last news fetch
finnhub_api_calls_today = 0  # Track daily API calls
cache_lock = threading.Lock()

# Starting symbols to scan (will auto-expand when new stocks qualify)
SEED_SYMBOLS = [
    'GME', 'AMC', 'TSLA', 'AMD', 'PLTR', 
    'SOFI', 'NIO', 'LCID', 'ATER', 'BBIG'
]

# Broader pool of potential symbols to discover from
# Scanner will sample from this list to find movers
DISCOVERY_POOL = [
    # Meme/High Volume
    'GME', 'AMC', 'TSLA', 'BBBY', 'EXPR', 'KOSS', 'NAKD', 'SNDL',
    # Low Float Plays
    'ATER', 'BBIG', 'RDBX', 'MULN', 'BKSY', 'GREE', 'SPRT',
    # Penny Stocks
    'SNDL', 'ZOM', 'NAKD', 'GNUS', 'TLRY', 'SAVA', 'OCGN',
    # EV Sector
    'NIO', 'LCID', 'RIVN', 'FSR', 'RIDE', 'GOEV', 'NKLA',
    # Tech Volatile
    'AMD', 'NVDA', 'PLTR', 'SOFI', 'HOOD', 'COIN', 'RBLX',
    # Biotech Movers
    'SAVA', 'OCGN', 'BNGO', 'CIDM', 'JAGX', 'SENS',
    # SPACs
    'DWAC', 'PHUN', 'BENE', 'IRNT',
    # Crypto Related
    'COIN', 'MARA', 'RIOT', 'BTBT', 'EBON',
    # Recent IPOs
    'HOOD', 'RBLX', 'DIDI', 'GRAB',
]

# Active symbols that have qualified (auto-expands)
active_symbols = set(SEED_SYMBOLS)  # Start with seed symbols
active_symbols_lock = threading.Lock()

def should_use_proxy() -> bool:
    """Check if we should use ScraperAPI proxy mode"""
    global use_proxy_mode, proxy_mode_until
    
    if not use_proxy_mode:
        return False
    
    # Check if 24 hours have passed
    if proxy_mode_until and datetime.now() >= proxy_mode_until:
        logging.info("🔓 24 hours passed - Switching back to direct Yahoo Finance")
        use_proxy_mode = False
        proxy_mode_until = None
        return False
    
    return True

def should_use_yahoo() -> bool:
    """Check if we should use Yahoo Finance (not locked)"""
    global use_yahoo_locked, yahoo_locked_until
    
    # If never locked, use Yahoo
    if not use_yahoo_locked:
        return True
    
    # Check if Yahoo lockout period has expired
    if yahoo_locked_until and datetime.now() > yahoo_locked_until:
        use_yahoo_locked = False
        yahoo_locked_until = None
        logging.info("✅ Yahoo Finance unlocked! Switching back to Yahoo as primary source")
        return True
    
    return False

def should_use_serpapi() -> bool:
    """Check if we should use SerpAPI (has quota remaining)"""
    global serpapi_calls_used
    
    # Check if SerpAPI quota exhausted
    if serpapi_calls_used >= SERPAPI_FREE_LIMIT:
        logging.warning(f"⚠️ SerpAPI quota exhausted ({serpapi_calls_used}/{SERPAPI_FREE_LIMIT})")
        return False
    
    return True

def should_use_alphavantage() -> bool:
    """Check if we should use AlphaVantage (has quota remaining)"""
    global alphavantage_calls_used
    
    # Check if AlphaVantage quota exhausted
    if alphavantage_calls_used >= ALPHAVANTAGE_FREE_LIMIT:
        logging.warning(f"⚠️ AlphaVantage quota exhausted ({alphavantage_calls_used}/{ALPHAVANTAGE_FREE_LIMIT})")
        return False
    
    return True

def should_use_massive() -> bool:
    """Check if we can use Massive.com (rate limit: 5 calls/minute)"""
    global massive_calls_history
    
    with massive_calls_lock:
        # Remove calls older than 1 minute
        current_time = time.time()
        massive_calls_history = [
            call_time for call_time in massive_calls_history 
            if current_time - call_time < MASSIVE_RATE_WINDOW
        ]
        
        # Check if we're under the rate limit
        if len(massive_calls_history) >= MASSIVE_RATE_LIMIT:
            wait_time = int(MASSIVE_RATE_WINDOW - (current_time - massive_calls_history[0]))
            logging.warning(f"⚠️ Massive.com rate limit reached ({len(massive_calls_history)}/{MASSIVE_RATE_LIMIT}/min), wait {wait_time}s")
            return False
        
        return True

def lock_yahoo_finance():
    """Lock Yahoo Finance for 2 hours (switches to SerpAPI)"""
    global use_yahoo_locked, yahoo_locked_until
    
    use_yahoo_locked = True
    yahoo_locked_until = datetime.now() + timedelta(hours=2)
    
    logging.warning("🔒 Yahoo Finance LOCKED (rate limited)! Switching to SerpAPI")
    logging.info(f"🕐 Will retry Yahoo Finance after: {yahoo_locked_until.strftime('%Y-%m-%d %I:%M %p')}")

def track_proxy_usage():
    """Track ScraperAPI usage (1000/month free limit)"""
    global proxy_calls_used, proxy_calls_reset_date
    
    # Reset counter on new month
    now = datetime.now()
    if proxy_calls_reset_date is None or now.month != proxy_calls_reset_date.month:
        proxy_calls_used = 0
        proxy_calls_reset_date = now
        logging.info(f"📊 ScraperAPI usage reset for {now.strftime('%B %Y')}")
    
    proxy_calls_used += 1
    remaining = SCRAPERAPI_FREE_LIMIT - proxy_calls_used
    
    if proxy_calls_used <= SCRAPERAPI_FREE_LIMIT:
        logging.info(f"📡 ScraperAPI call #{proxy_calls_used}/1000 this month ({remaining} remaining)")
    else:
        logging.error(f"⚠️ ScraperAPI FREE limit exceeded! {proxy_calls_used}/1000 used this month")

def fetch_with_scraperapi(url: str) -> requests.Response:
    """Fetch URL through ScraperAPI proxy"""
    track_proxy_usage()
    
    if SCRAPERAPI_KEY == 'YOUR_FREE_API_KEY':
        logging.error("❌ ScraperAPI key not configured! Get free key from https://www.scraperapi.com")
        raise Exception("ScraperAPI key not configured")
    
    proxy_url = f"{SCRAPERAPI_BASE_URL}?api_key={SCRAPERAPI_KEY}&url={url}"
    
    logging.debug(f"🔄 Fetching via ScraperAPI proxy: {url}")
    response = requests.get(proxy_url, timeout=30)
    
    return response

def track_serpapi_usage():
    """Track SerpAPI usage (100/month free limit)"""
    global serpapi_calls_used, serpapi_calls_reset_date
    
    # Reset counter on new month
    now = datetime.now()
    if serpapi_calls_reset_date is None or now.month != serpapi_calls_reset_date.month:
        serpapi_calls_used = 0
        serpapi_calls_reset_date = now
        logging.info(f"📊 SerpAPI usage reset for {now.strftime('%B %Y')}")
    
    serpapi_calls_used += 1
    remaining = SERPAPI_FREE_LIMIT - serpapi_calls_used
    
    if serpapi_calls_used <= SERPAPI_FREE_LIMIT:
        logging.info(f"🔍 SerpAPI call #{serpapi_calls_used}/250 this month ({remaining} remaining)")
    else:
        logging.error(f"⚠️ SerpAPI FREE limit exceeded! {serpapi_calls_used}/250 used this month")

def fetch_stock_from_serpapi(symbol: str) -> Dict[str, Any]:
    """Fetch stock data from SerpAPI Google Finance as ultimate fallback"""
    track_serpapi_usage()
    
    if SERPAPI_KEY == 'YOUR_SERPAPI_KEY':
        logging.error("❌ SerpAPI key not configured! Get free key from https://serpapi.com")
        raise Exception("SerpAPI key not configured")
    
    try:
        # SerpAPI Google Finance endpoint
        params = {
            'engine': 'google_finance',
            'q': f'{symbol}:NASDAQ',  # Try NASDAQ first
            'api_key': SERPAPI_KEY,
            'hl': 'en'
        }
        
        logging.info(f"🔍 Fetching {symbol} from SerpAPI Google Finance...")
        response = requests.get(SERPAPI_BASE_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract summary data
            summary = data.get('summary', {})
            graph_data = data.get('graph', [])
            
            # Require at least summary data (price)
            if not summary or not summary.get('price'):
                logging.warning(f"⚠️ SerpAPI returned no price data for {symbol}")
                return None
            
            # Parse current price
            current_price_str = summary.get('price', '0')
            current_price = float(current_price_str.replace('$', '').replace(',', ''))
            
            if current_price <= 0:
                logging.warning(f"⚠️ Invalid price for {symbol}: {current_price}")
                return None
            
            # Parse previous close (or estimate)
            prev_close_str = summary.get('previous_close', None)
            if prev_close_str:
                previous_close = float(prev_close_str.replace('$', '').replace(',', ''))
            else:
                # Estimate previous close from current price
                previous_close = current_price * 0.98  # Assume 2% down from current
            
            # Calculate change
            change_amount = current_price - previous_close
            change_percent = (change_amount / previous_close) * 100 if previous_close > 0 else 0
            
            # Build candle data from graph OR generate synthetic candles
            candles = []
            if graph_data and len(graph_data) > 0:
                # Use actual graph data
                for point in graph_data[-60:]:  # Last 60 data points
                    price = float(point.get('price', current_price))
                    candles.append({
                        'time': point.get('date', datetime.now().isoformat()),
                        'open': price,
                        'high': price * 1.01,  # Estimate high
                        'low': price * 0.99,   # Estimate low
                        'close': price,
                        'volume': 1000000  # SerpAPI doesn't provide volume, use placeholder
                    })
            else:
                # Generate synthetic candles (60 candles, 5-minute intervals)
                logging.info(f"📊 Generating synthetic candles for {symbol} (no graph data from SerpAPI)")
                base_time = datetime.now() - timedelta(hours=5)
                for i in range(60):
                    # Create gradual price movement towards current price
                    progress = i / 60.0
                    price = previous_close + (change_amount * progress)
                    candles.append({
                        'time': (base_time + timedelta(minutes=i*5)).isoformat(),
                        'open': price,
                        'high': price * 1.005,
                        'low': price * 0.995,
                        'close': price,
                        'volume': 1000000
                    })
            
            stock_data = {
                'symbol': symbol,
                'name': summary.get('title', symbol),
                'currentPrice': current_price,
                'previousClose': previous_close,
                'openPrice': previous_close,  # Estimate
                'dayHigh': current_price * 1.02,  # Estimate
                'dayLow': current_price * 0.98,  # Estimate
                'volume': 5000000,  # Placeholder
                'avgVolume': 3000000,  # Placeholder
                'changeAmount': change_amount,
                'changePercent': change_percent,
                'float': 50000000,  # Placeholder
                'marketCap': current_price * 50000000,
                'candles': candles,
                'chartData': {'5m': candles},  # Limited data from SerpAPI
                'lastUpdated': datetime.now().isoformat(),
                'signal': 'BUY' if change_percent > 5 else 'HOLD',
                'dataSource': 'SerpAPI'  # Tag data source
            }
            
            logging.info(f"✅ Successfully fetched {symbol} from SerpAPI: ${current_price} ({change_percent:+.2f}%)")
            return stock_data
            
        elif response.status_code == 429:
            logging.error(f"🔴 SerpAPI rate limit exceeded!")
            return None
        else:
            logging.error(f"⚠️ SerpAPI error: Status {response.status_code}")
            return None
            
    except Exception as e:
        logging.error(f"❌ SerpAPI fetch failed for {symbol}: {str(e)}")
        return None

def fetch_stock_from_alphavantage(symbol: str) -> Dict[str, Any]:
    """Fetch stock data from AlphaVantage as third fallback"""
    track_alphavantage_usage()
    
    if ALPHAVANTAGE_KEY == 'YOUR_ALPHAVANTAGE_API_KEY':
        logging.error("❌ AlphaVantage key not configured! Get free key from https://www.alphavantage.co/support/#api-key")
        return None
    
    try:
        logging.info(f"🔍 Fetching {symbol} from AlphaVantage...")
        
        # Fetch quote data (GLOBAL_QUOTE function)
        quote_params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': ALPHAVANTAGE_KEY
        }
        
        quote_response = requests.get(ALPHAVANTAGE_BASE_URL, params=quote_params, timeout=10)
        quote_response.raise_for_status()
        quote_data = quote_response.json()
        
        if 'Global Quote' not in quote_data or not quote_data['Global Quote']:
            logging.warning(f"⚠️ AlphaVantage returned no quote data for {symbol}")
            return None
        
        quote = quote_data['Global Quote']
        
        # Extract data
        current_price = float(quote.get('05. price', 0))
        previous_close = float(quote.get('08. previous close', current_price))
        open_price = float(quote.get('02. open', current_price))
        day_high = float(quote.get('03. high', current_price))
        day_low = float(quote.get('04. low', current_price))
        volume = int(quote.get('06. volume', 1000000))
        
        change_amount = float(quote.get('09. change', 0))
        change_percent_str = quote.get('10. change percent', '0%')
        change_percent = float(change_percent_str.replace('%', ''))
        
        logging.info(f"✅ Successfully fetched {symbol} from AlphaVantage: ${current_price} ({change_percent:+.2f}%)")
        
        # Generate synthetic candles (AlphaVantage free tier has strict rate limits for intraday data)
        logging.info(f"📊 Generating synthetic candles for {symbol} (saving AlphaVantage intraday quota)")
        candles = []
        base_time = datetime.now() - timedelta(hours=5)
        for i in range(60):
            progress = i / 60.0
            price = previous_close + (change_amount * progress)
            candles.append({
                'time': (base_time + timedelta(minutes=i*5)).isoformat(),
                'open': price,
                'high': price * 1.005,
                'low': price * 0.995,
                'close': price,
                'volume': volume // 60
            })
        
        return {
            'symbol': symbol,
            'name': symbol,  # AlphaVantage doesn't provide company name in basic quote
            'currentPrice': round(current_price, 2),
            'previousClose': round(previous_close, 2),
            'openPrice': round(open_price, 2),
            'dayHigh': round(day_high, 2),
            'dayLow': round(day_low, 2),
            'volume': volume,
            'avgVolume': volume,  # Estimate
            'float': 10_000_000,  # Placeholder - AlphaVantage doesn't provide float
            'changePercent': round(change_percent, 2),
            'changeAmount': round(change_amount, 2),
            'candles': candles,
            'chartData': {'5m': candles},
            'lastUpdated': datetime.now().isoformat(),
            'dataSource': 'AlphaVantage'
        }
        
    except Exception as e:
        logging.error(f"❌ AlphaVantage error for {symbol}: {str(e)}")
        return None

def track_alphavantage_usage():
    """Track AlphaVantage API usage (resets daily)"""
    global alphavantage_calls_used, alphavantage_calls_reset_date
    
    # Check if we need to reset the counter (daily reset)
    today = datetime.now().date()
    if alphavantage_calls_reset_date is None or alphavantage_calls_reset_date < today:
        alphavantage_calls_used = 0
        alphavantage_calls_reset_date = today
        logging.info(f"📊 AlphaVantage usage reset for {today.strftime('%B %d, %Y')}")
    
    alphavantage_calls_used += 1
    remaining = ALPHAVANTAGE_FREE_LIMIT - alphavantage_calls_used
    logging.info(f"🔍 AlphaVantage call #{alphavantage_calls_used}/{ALPHAVANTAGE_FREE_LIMIT} today ({remaining} remaining)")

def fetch_stock_from_massive(symbol: str) -> Dict[str, Any]:
    """Fetch stock data from Massive.com as fourth fallback (5 calls/minute)"""
    track_massive_usage()
    
    if MASSIVE_KEY == 'YOUR_MASSIVE_API_KEY':
        logging.error("❌ Massive.com key not configured! Get free key from https://massive.com")
        return None
    
    try:
        logging.info(f"🔍 Fetching {symbol} from Massive.com...")
        
        # Massive.com API endpoint (adjust based on actual API documentation)
        params = {
            'symbol': symbol,
            'apikey': MASSIVE_KEY
        }
        
        response = requests.get(f"{MASSIVE_BASE_URL}/quote", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract data (adjust based on actual API response format)
        current_price = float(data.get('price', 0))
        previous_close = float(data.get('previousClose', current_price))
        open_price = float(data.get('open', current_price))
        day_high = float(data.get('high', current_price))
        day_low = float(data.get('low', current_price))
        volume = int(data.get('volume', 1000000))
        
        change_amount = current_price - previous_close
        change_percent = (change_amount / previous_close) * 100 if previous_close > 0 else 0
        
        logging.info(f"✅ Successfully fetched {symbol} from Massive.com: ${current_price} ({change_percent:+.2f}%)")
        
        # Generate synthetic candles (rate limit is tight at 5/min, save quota)
        logging.info(f"📊 Generating synthetic candles for {symbol} (saving Massive.com quota)")
        candles = []
        base_time = datetime.now() - timedelta(hours=5)
        for i in range(60):
            progress = i / 60.0
            price = previous_close + (change_amount * progress)
            candles.append({
                'time': (base_time + timedelta(minutes=i*5)).isoformat(),
                'open': price,
                'high': price * 1.005,
                'low': price * 0.995,
                'close': price,
                'volume': volume // 60
            })
        
        return {
            'symbol': symbol,
            'name': symbol,
            'currentPrice': round(current_price, 2),
            'previousClose': round(previous_close, 2),
            'openPrice': round(open_price, 2),
            'dayHigh': round(day_high, 2),
            'dayLow': round(day_low, 2),
            'volume': volume,
            'avgVolume': volume,
            'float': 10_000_000,  # Placeholder
            'changePercent': round(change_percent, 2),
            'changeAmount': round(change_amount, 2),
            'candles': candles,
            'chartData': {'5m': candles},
            'lastUpdated': datetime.now().isoformat(),
            'dataSource': 'Massive.com'
        }
        
    except Exception as e:
        logging.error(f"❌ Massive.com error for {symbol}: {str(e)}")
        return None

def track_massive_usage():
    """Track Massive.com API usage (rate limit: 5 calls/minute)"""
    global massive_calls_history
    
    with massive_calls_lock:
        current_time = time.time()
        massive_calls_history.append(current_time)
        
        # Clean up old calls (older than 1 minute)
        massive_calls_history = [
            call_time for call_time in massive_calls_history 
            if current_time - call_time < MASSIVE_RATE_WINDOW
        ]
        
        remaining = MASSIVE_RATE_LIMIT - len(massive_calls_history)
        logging.info(f"🔍 Massive.com call #{len(massive_calls_history)}/{MASSIVE_RATE_LIMIT}/min ({remaining} remaining)")

def fetch_news_for_stock(symbol: str) -> List[Dict[str, Any]]:
    """Fetch today's news for a specific stock from Finnhub"""
    global finnhub_api_calls_today
    
    try:
        finnhub_api_calls_today += 1
        # Get today's date range
        today = datetime.now().date()
        from_date = today.strftime('%Y-%m-%d')
        to_date = today.strftime('%Y-%m-%d')
        
        # Finnhub company news endpoint
        url = f'{FINNHUB_BASE_URL}/company-news'
        params = {
            'symbol': symbol,
            'from': from_date,
            'to': to_date,
            'token': FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            news_items = response.json()
            
            # Filter and format news
            formatted_news = []
            for item in news_items[:5]:  # Limit to 5 most recent
                formatted_news.append({
                    'headline': item.get('headline', 'No headline'),
                    'summary': item.get('summary', ''),
                    'source': item.get('source', 'Unknown'),
                    'url': item.get('url', ''),
                    'timestamp': item.get('datetime', 0),  # Unix timestamp
                    'category': item.get('category', '')
                })
            
            logging.info(f"✅ Finnhub: Successfully fetched {len(formatted_news)} news items for {symbol}")
            return formatted_news
        elif response.status_code == 429:
            logging.error(f"🔴 Finnhub RATE LIMIT hit for {symbol}! You've exceeded 60 calls/minute.")
            return []
        elif response.status_code == 403:
            logging.error(f"🔴 Finnhub API key invalid or expired for {symbol}")
            return []
        else:
            logging.warning(f"⚠️ Finnhub API error for {symbol}: Status {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Error fetching news for {symbol}: {str(e)}")
        return []

def should_fetch_news() -> bool:
    """Check if we should fetch news (4-9 AM window, once per day)"""
    global news_fetched_today, last_news_fetch_date
    
    now = datetime.now()
    current_hour = now.hour
    current_date = now.date()
    
    # Reset flag if it's a new day
    if last_news_fetch_date != current_date:
        news_fetched_today = False
        last_news_fetch_date = current_date
    
    # Only fetch between 4 AM and 9 AM, and only once per day
    if 4 <= current_hour < 9 and not news_fetched_today:
        return True
    
    return False

def fetch_news_for_scanner_stocks(symbols: List[str]):
    """Fetch news for all stocks in the scanner at 4 AM"""
    global news_fetched_today, news_cache
    
    if not should_fetch_news():
        return
    
    logging.info(f"📰 Starting news fetch for {len(symbols)} stocks at 4 AM...")
    logging.info(f"📊 Finnhub FREE tier limit: 60 calls/minute (using {FINNHUB_RATE_LIMIT_DELAY}s delay)")
    
    start_time = time.time()
    successful_fetches = 0
    
    with cache_lock:
        news_cache = {}
        for i, symbol in enumerate(symbols, 1):
            logging.info(f"📡 [{i}/{len(symbols)}] Fetching news for {symbol}...")
            news = fetch_news_for_stock(symbol)
            if news:
                news_cache[symbol] = news
                successful_fetches += 1
                logging.info(f"✅ Found {len(news)} news items for {symbol}")
            else:
                logging.info(f"ℹ️  No news found for {symbol}")
            
            # Respect Finnhub rate limits (60 calls/min FREE tier)
            # Use 1.5 second delay for safety buffer
            if i < len(symbols):  # Don't delay after last symbol
                logging.debug(f"⏸️  Waiting {FINNHUB_RATE_LIMIT_DELAY}s before next request...")
                time.sleep(FINNHUB_RATE_LIMIT_DELAY)
        
        news_fetched_today = True
        elapsed_time = time.time() - start_time
        logging.info(f"✅ News fetching complete!")
        logging.info(f"📊 Stats: {successful_fetches}/{len(symbols)} stocks with news")
        logging.info(f"⏱️  Total time: {elapsed_time:.1f} seconds")
        logging.info(f"📈 API calls made: {len(symbols)} (under 60/min limit)")

def news_scheduler():
    """Background thread to check time and fetch news at 4 AM"""
    global news_fetched_today
    
    while True:
        try:
            now = datetime.now()
            current_hour = now.hour
            
            # Check if it's 4 AM and we haven't fetched news today
            if current_hour == 4 and not news_fetched_today:
                logging.info("It's 4 AM! Fetching news for scanner stocks...")
                # Fetch news for all active symbols (including newly discovered ones)
                with active_symbols_lock:
                    symbols_to_fetch = list(active_symbols)
                logging.info(f"📰 Fetching news for {len(symbols_to_fetch)} active symbols (auto-discovered)")
                fetch_news_for_scanner_stocks(symbols_to_fetch)
            
            # Check every minute
            time.sleep(60)
            
        except Exception as e:
            logging.error(f"Error in news scheduler: {str(e)}")
            time.sleep(60)

class StockScanner:
    def __init__(self):
        # Note: symbols are now managed globally in active_symbols (auto-expands)
        self.symbols = SEED_SYMBOLS  # Not used anymore, kept for compatibility
        self.min_price = 1.0
        self.max_price = 20.0
        self.max_float = 1_000_000_000  # 1B shares
        self.min_gain_percent = 10.0
        self.volume_multiplier = 2.0
        
    def get_stock_data(self, symbol: str, timeframe: str = '5m') -> Dict[str, Any]:
        """Fetch real-time stock data with Massive.com as primary API (5 calls/min)"""
        try:
            logging.info(f"🔍 Fetching data for {symbol} (timeframe: {timeframe})")
            
            # SMART AUTO-SWITCHING LOGIC (Massive.com First - 5 calls/min refresh!)
            # Priority 1: Try Massive.com FIRST (best for real-time: 5 calls/min)
            if should_use_massive():
                logging.info(f"⚡ Using Massive.com for {symbol} (PRIMARY API - 5/min)")
                try:
                    massive_data = fetch_stock_from_massive(symbol)
                    if massive_data:
                        logging.info(f"✅ Successfully fetched {symbol} from Massive.com")
                        return massive_data
                    else:
                        logging.warning(f"⚠️ Massive.com returned no data for {symbol}, trying AlphaVantage...")
                        # Fall through to AlphaVantage
                except Exception as e:
                    logging.error(f"❌ Massive.com failed for {symbol}: {str(e)}, trying AlphaVantage...")
                    # Fall through to AlphaVantage
            
            # Priority 2: Try AlphaVantage (if Massive rate-limited - 25/day)
            if should_use_alphavantage():
                logging.info(f"🌐 Using AlphaVantage for {symbol} (Massive rate-limited)")
                try:
                    alphavantage_data = fetch_stock_from_alphavantage(symbol)
                    if alphavantage_data:
                        logging.info(f"✅ Successfully fetched {symbol} from AlphaVantage")
                        return alphavantage_data
                    else:
                        logging.warning(f"⚠️ AlphaVantage returned no data for {symbol}, trying Yahoo...")
                        # Fall through to Yahoo
                except Exception as e:
                    logging.error(f"❌ AlphaVantage failed for {symbol}: {str(e)}, trying Yahoo...")
                    # Fall through to Yahoo
            
            # Priority 3: Try Yahoo Finance (if AlphaVantage and Massive failed)
            if should_use_yahoo():
                logging.info(f"🌐 Using Yahoo Finance for {symbol}")
                try:
                    return self._fetch_from_yahoo(symbol, timeframe)
                except Exception as e:
                    error_msg = str(e)
                    logging.error(f"❌ Yahoo Finance failed for {symbol}: {error_msg}")
                    
                    # Check if rate limited
                    if any(err in error_msg for err in ["429", "Too Many Requests", "Expecting value", "Max retries"]):
                        lock_yahoo_finance()
                        logging.warning(f"🔄 Switching to SerpAPI for {symbol}...")
                        # Fall through to SerpAPI
                    else:
                        # Fall through to next API
                        pass
            
            # Priority 4: Try SerpAPI (last resort)
            if should_use_serpapi():
                logging.info(f"🌐 Using SerpAPI for {symbol} (Yahoo locked: {use_yahoo_locked})")
                try:
                    serpapi_data = fetch_stock_from_serpapi(symbol)
                    if serpapi_data:
                        logging.info(f"✅ Successfully fetched {symbol} from SerpAPI")
                        return serpapi_data
                    else:
                        logging.warning(f"⚠️ SerpAPI returned no data for {symbol}")
                        return None
                except Exception as e:
                    logging.error(f"❌ SerpAPI failed for {symbol}: {str(e)}")
                    return None
            else:
                massive_count = len(massive_calls_history) if 'massive_calls_history' in globals() else 0
                logging.error(f"❌ All APIs unavailable for {symbol}: AlphaVantage ({alphavantage_calls_used}/{ALPHAVANTAGE_FREE_LIMIT}), Massive.com ({massive_count}/{MASSIVE_RATE_LIMIT}/min), Yahoo (locked), SerpAPI ({serpapi_calls_used}/{SERPAPI_FREE_LIMIT})")
                return None
                
        except Exception as e:
            logging.error(f"❌ Error fetching {symbol}: {str(e)}")
            return None
    
    def _fetch_from_yahoo(self, symbol: str, timeframe: str = '5m') -> Dict[str, Any]:
        """Fetch from Yahoo Finance (extracted method)"""
        # Configure yfinance - direct connection
        ticker = yf.Ticker(symbol)
        
        # Get basic info
        logging.info(f"📋 Fetching info for {symbol}...")
        info = ticker.info
        logging.info(f"✅ Info received for {symbol}: {info.get('longName', 'N/A')}")
        
        # Get historical data based on timeframe
        period_map = {
            '1m': '1d',
            '3m': '5d',
            '5m': '5d',
            '15m': '5d',
            '30m': '5d',
            '1h': '1mo',
            '24h': '3mo'
        }
        
        interval_map = {
            '1m': '1m',
            '3m': '2m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '24h': '1d'
        }
        
        period = period_map.get(timeframe, '5d')
        interval = interval_map.get(timeframe, '5m')
        
        logging.info(f"📊 Fetching history for {symbol}: period={period}, interval={interval}")
        hist = ticker.history(period=period, interval=interval)
        logging.info(f"📈 History received for {symbol}: {len(hist)} candles")
        
        if hist.empty or len(hist) < 2:
            logging.warning(f"❌ {symbol}: Insufficient data (empty={hist.empty}, length={len(hist)})")
            raise Exception(f"Insufficient data for {symbol}")
            
        current_price = float(hist['Close'].iloc[-1])
        previous_close = float(hist['Close'].iloc[-2])
        open_price = float(hist['Open'].iloc[-1])
        day_high = float(hist['High'].max())
        day_low = float(hist['Low'].min())
        
        current_volume = int(hist['Volume'].iloc[-1])
        avg_volume = int(hist['Volume'].mean())
        
        change_amount = current_price - previous_close
        change_percent = (change_amount / previous_close) * 100 if previous_close > 0 else 0
        
        # Get float (shares outstanding) - fallback to large number if not available
        float_shares = info.get('floatShares', info.get('sharesOutstanding', 1_000_000_000))
        if float_shares is None:
            float_shares = 1_000_000_000
            
        # Calculate moving averages
        closes = hist['Close']
        ma20 = closes.rolling(window=20, min_periods=1).mean()
        ma50 = closes.rolling(window=50, min_periods=1).mean()
        ma200 = closes.rolling(window=200, min_periods=1).mean()
        
        # Prepare candlestick data with MAs
        candles = []
        for i, (idx, row) in enumerate(hist.iterrows()):
            candle = {
                'time': idx.isoformat(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            }
            
            # Add moving averages if available
            if i >= 19:  # At least 20 periods for MA20
                candle['ma20'] = round(float(ma20.iloc[i]), 2)
            if i >= 49:  # At least 50 periods for MA50
                candle['ma50'] = round(float(ma50.iloc[i]), 2)
            if i >= 199:  # At least 200 periods for MA200
                candle['ma200'] = round(float(ma200.iloc[i]), 2)
            
            candles.append(candle)
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'currentPrice': round(current_price, 2),
            'previousClose': round(previous_close, 2),
            'openPrice': round(open_price, 2),
            'dayHigh': round(day_high, 2),
            'dayLow': round(day_low, 2),
            'volume': current_volume,
            'avgVolume': avg_volume,
            'float': float_shares,
            'changePercent': round(change_percent, 2),
            'changeAmount': round(change_amount, 2),
            'candles': candles,
            'lastUpdated': datetime.now().isoformat(),
            'dataSource': 'Yahoo Finance'  # Tag data source
        }
    
    def filter_stocks(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter stocks based on criteria and auto-discover new symbols"""
        global active_symbols
        
        min_price = criteria.get('minPrice', self.min_price)
        max_price = criteria.get('maxPrice', self.max_price)
        max_float = criteria.get('maxFloat', self.max_float)
        min_gain = criteria.get('minGainPercent', self.min_gain_percent)
        vol_multiplier = criteria.get('volumeMultiplier', self.volume_multiplier)
        timeframe = criteria.get('chartTimeframe', '5m')
        display_count = criteria.get('displayCount', 5)
        
        # Build scan list: active symbols + random sample from discovery pool
        import random
        with active_symbols_lock:
            scan_symbols = list(active_symbols)
        
        # Add 10 random symbols from discovery pool to discover new movers
        discovery_sample = random.sample(
            [s for s in DISCOVERY_POOL if s not in scan_symbols], 
            min(10, len([s for s in DISCOVERY_POOL if s not in scan_symbols]))
        )
        scan_symbols.extend(discovery_sample)
        
        logging.info(f"🔍 Scanning {len(scan_symbols)} symbols ({len(active_symbols)} active + {len(discovery_sample)} discovery)")
        
        results = []
        newly_added = []
        
        for symbol in scan_symbols:
            # Get primary timeframe data
            stock_data = self.get_stock_data(symbol, timeframe)
            
            if stock_data is None:
                continue
            
            # Apply filters
            price_check = min_price <= stock_data['currentPrice'] <= max_price
            float_check = stock_data['float'] <= max_float
            gain_check = stock_data['changePercent'] >= min_gain
            volume_check = stock_data['volume'] >= (stock_data['avgVolume'] * vol_multiplier)
            
            if price_check and float_check and gain_check and volume_check:
                # Stock qualifies! Add to active symbols if new
                with active_symbols_lock:
                    if symbol not in active_symbols:
                        active_symbols.add(symbol)
                        newly_added.append(symbol)
                        logging.info(f"🆕 NEW MOVER DISCOVERED: {symbol} - {stock_data['name']} (+{stock_data['changePercent']:.2f}%)")
                
                # Calculate signal
                if stock_data['changePercent'] > 15 and stock_data['volume'] > stock_data['avgVolume'] * 3:
                    stock_data['signal'] = 'BUY'
                elif stock_data['changePercent'] < -5:
                    stock_data['signal'] = 'SELL'
                else:
                    stock_data['signal'] = 'HOLD'
                
                stock_data['isHot'] = stock_data['volume'] > stock_data['avgVolume'] * 5
                
                # Check if this stock has news (from 4 AM news cache)
                stock_data['hasNews'] = symbol in news_cache and len(news_cache[symbol]) > 0
                stock_data['newsCount'] = len(news_cache.get(symbol, []))
                
                # Fetch additional timeframes for modal switching (no extra filtering)
                chart_data = {}
                for tf in ['1m', '5m', '1h', '24h']:
                    if tf == timeframe:
                        # Use existing candles for current timeframe
                        chart_data[tf] = stock_data['candles']
                    else:
                        # Fetch additional timeframe
                        tf_data = self.get_stock_data(symbol, tf)
                        if tf_data and 'candles' in tf_data:
                            chart_data[tf] = tf_data['candles']
                
                stock_data['chartData'] = chart_data
                results.append(stock_data)
        
        # Sort by change percent (highest first)
        results.sort(key=lambda x: x['changePercent'], reverse=True)
        
        # Log summary
        with active_symbols_lock:
            total_active = len(active_symbols)
        
        if newly_added:
            logging.info(f"🎯 Scan complete: {len(results)} qualifying stocks | {len(newly_added)} NEW symbols added: {', '.join(newly_added)}")
        else:
            logging.info(f"🎯 Scan complete: {len(results)} qualifying stocks | Total active symbols: {total_active}")
        
        return results[:display_count]

scanner = StockScanner()

@app.route('/api/scan', methods=['POST'])
def scan_stocks():
    """Scan stocks with given criteria"""
    try:
        criteria = request.json
        results = scanner.filter_stocks(criteria)
        
        # Include smart API switching status
        yahoo_available = should_use_yahoo()
        serpapi_available = should_use_serpapi()
        alphavantage_available = should_use_alphavantage()
        massive_available = should_use_massive()
        
        # Determine active source (Massive.com is PRIMARY - fastest refresh at 5/min)
        if massive_available:
            active_source = 'Massive.com'
        elif alphavantage_available:
            active_source = 'AlphaVantage'
        elif yahoo_available:
            active_source = 'Yahoo Finance'
        elif serpapi_available:
            active_source = 'SerpAPI'
        else:
            active_source = 'None (all exhausted)'
        
        # Massive.com call count (last minute)
        with massive_calls_lock:
            current_time = time.time()
            massive_recent_calls = [
                call for call in massive_calls_history 
                if current_time - call < MASSIVE_RATE_WINDOW
            ]
            massive_calls_count = len(massive_recent_calls)
        
        api_status = {
            'yahooLocked': use_yahoo_locked,
            'yahooUnlockAt': yahoo_locked_until.isoformat() if yahoo_locked_until else None,
            'serpapiQuota': {
                'used': serpapi_calls_used,
                'limit': SERPAPI_FREE_LIMIT,
                'remaining': SERPAPI_FREE_LIMIT - serpapi_calls_used
            },
            'alphavantageQuota': {
                'used': alphavantage_calls_used,
                'limit': ALPHAVANTAGE_FREE_LIMIT,
                'remaining': ALPHAVANTAGE_FREE_LIMIT - alphavantage_calls_used
            },
            'massiveRateLimit': {
                'used': massive_calls_count,
                'limit': MASSIVE_RATE_LIMIT,
                'remaining': MASSIVE_RATE_LIMIT - massive_calls_count,
                'window': f'{MASSIVE_RATE_WINDOW}s'
            },
            'activeSource': active_source,
            'fallbackAvailable': serpapi_available or alphavantage_available or massive_available
        }
        
        return jsonify({
            'success': True,
            'stocks': results,
            'timestamp': datetime.now().isoformat(),
            'apiStatus': api_status
        })
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error in scan: {error_msg}")
        
        # Check if it's a rate limit error
        if "RATE_LIMIT_ERROR" in error_msg or "429" in error_msg or "Too Many Requests" in error_msg:
            return jsonify({
                'success': False,
                'error': 'Rate limited by Yahoo Finance. Please wait.',
                'rateLimited': True
            }), 429
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock(symbol):
    """Get detailed data for a specific stock"""
    try:
        timeframe = request.args.get('timeframe', '5m')
        stock_data = scanner.get_stock_data(symbol, timeframe)
        
        if stock_data:
            return jsonify({
                'success': True,
                'stock': stock_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Stock not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news/<symbol>', methods=['GET'])
def get_news(symbol):
    """Get cached news for a specific stock (fetched at 4 AM)"""
    try:
        with cache_lock:
            news = news_cache.get(symbol.upper(), [])
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'news': news,
            'count': len(news),
            'fetchedToday': news_fetched_today,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/symbols', methods=['GET'])
def get_symbols():
    """Get list of all active symbols (auto-discovered)"""
    with active_symbols_lock:
        active_list = sorted(list(active_symbols))
    
    return jsonify({
        'success': True,
        'symbols': active_list,
        'count': len(active_list),
        'seedSymbols': SEED_SYMBOLS,
        'discoveryPool': len(DISCOVERY_POOL),
        'autoDiscovery': True
    })

@app.route('/api/unlock', methods=['POST'])
def force_unlock():
    """Force unlock Yahoo Finance (admin endpoint)"""
    global use_yahoo_locked, yahoo_locked_until
    
    use_yahoo_locked = False
    yahoo_locked_until = None
    
    logging.info("🔓 FORCE UNLOCK: Yahoo Finance manually unlocked via API")
    
    return jsonify({
        'success': True,
        'message': 'Yahoo Finance unlocked',
        'yahooLocked': False
    })

@app.route('/api/symbols', methods=['POST'])
def add_symbol():
    """Add a new symbol to track"""
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        
        if symbol and symbol not in scanner.symbols:
            scanner.symbols.append(symbol)
            return jsonify({
                'success': True,
                'message': f'Added {symbol} to scanner'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid or duplicate symbol'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/proxy/status', methods=['GET'])
def get_proxy_status():
    """Get ScraperAPI proxy status"""
    proxy_active = should_use_proxy()
    
    status = {
        'proxyMode': proxy_active,
        'proxyCallsUsed': proxy_calls_used,
        'proxyCallsLimit': SCRAPERAPI_FREE_LIMIT,
        'proxyCallsRemaining': SCRAPERAPI_FREE_LIMIT - proxy_calls_used,
        'scraperAPIConfigured': SCRAPERAPI_KEY != 'YOUR_FREE_API_KEY'
    }
    
    if proxy_active and proxy_mode_until:
        status['proxyUntil'] = proxy_mode_until.isoformat()
        status['proxyTimeRemaining'] = str(proxy_mode_until - datetime.now())
    
    return jsonify(status)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Start news scheduler in background thread
    news_thread = threading.Thread(target=news_scheduler, daemon=True)
    news_thread.start()
    logging.info("News scheduler started. Will fetch news at 4 AM daily.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

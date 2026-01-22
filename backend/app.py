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
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Interactive Brokers API Configuration
try:
    from ib_insync import IB, Stock, util
    IBKR_AVAILABLE = True
except ImportError:
    IBKR_AVAILABLE = False
    logging.warning("⚠️ ib_insync not installed. Install with: pip install ib-insync")

# IBKR Connection Settings
IBKR_HOST = os.getenv('IBKR_HOST', '127.0.0.1')
IBKR_PORT = int(os.getenv('IBKR_PORT', '7497'))  # 7497 = paper trading, 7496 = live
IBKR_CLIENT_ID = int(os.getenv('IBKR_CLIENT_ID', '1'))
IBKR_USERNAME = os.getenv('IBKR_USERNAME', 'userconti')
IBKR_PASSWORD = os.getenv('IBKR_PASSWORD', 'mbnadc21234')
IBKR_CONNECTED = False
IBKR_INSTANCE = None
IBKR_LOCK = threading.Lock()

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Helper function to generate REALISTIC synthetic candles with DISTINCT patterns per timeframe
def generate_synthetic_candles(symbol: str, previous_close: float, current_price: float, timeframe: str = '5m'):
    """Generate synthetic candles that VISIBLY DIFFER by timeframe - uses fractal-like patterns"""
    import random
    import math
    
    # Timeframe configuration: (num_candles, interval_minutes, lookback_hours, volatility_scale)
    timeframe_config = {
        # Intraday (minutes)
        '1m': (60, 1, 1, 0.003),       # High freq, low volatility
        '2m': (60, 2, 1, 0.004),       # 2-minute candles
        '5m': (60, 5, 5, 0.008),       # Medium freq, medium volatility
        '15m': (60, 15, 5, 0.01),      # 15-minute candles
        '30m': (60, 30, 5, 0.012),     # 30-minute candles
        '90m': (60, 90, 5, 0.015),     # 90-minute candles
        # Hourly
        '1h': (24, 60, 24, 0.02),      # Low freq, higher volatility
        # Daily
        '24h': (30, 1440, 720, 0.05),  # Very low freq, highest volatility
        # Weekly
        '1week': (52, 10080, 8736, 0.06),  # 52 weeks = 1 year
        # Monthly/Quarterly
        '1month': (30, 43200, 21600, 0.08),  # 30 monthly candles = 30 months
        '3month': (20, 129600, 51840, 0.1),  # 20 quarterly candles = 5 years
        # Longer periods
        '6month': (60, 43200, 43200, 0.12),  # 60 daily candles over 6 months
        '1year': (252, 1440, 8760, 0.15),    # 252 trading days = 1 year
        '2year': (504, 1440, 17520, 0.18),    # 504 trading days = 2 years
        '5year': (1260, 1440, 43800, 0.2),    # 1260 trading days = 5 years
        '10year': (2520, 1440, 87600, 0.25), # 2520 trading days = 10 years
        # Special
        'ytd': (252, 1440, 8760, 0.15),       # Year-to-date (same as 1year)
        'max': (5000, 1440, 438000, 0.3),     # Maximum history (large dataset)
    }
    
    num_candles, interval_mins, lookback_hours, volatility = timeframe_config.get(timeframe, (60, 5, 5, 0.008))
    
    candles = []
    base_time = datetime.now() - timedelta(hours=lookback_hours)
    change_amount = current_price - previous_close
    
    # Generate price path with DIFFERENT characteristics per timeframe
    prices = []
    for i in range(num_candles):
        progress = i / num_candles
        
        # Base trend (linear progression)
        trend = previous_close + (change_amount * progress)
        
        # Add MULTI-SCALE noise (different per timeframe)
        # Longer timeframes have MORE dramatic swings
        cycle1 = math.sin(i * 0.1 * (1/volatility)) * (previous_close * volatility * 0.5)
        cycle2 = math.sin(i * 0.3 * (1/volatility)) * (previous_close * volatility * 0.3)
        random_walk = random.uniform(-1, 1) * (previous_close * volatility)
        
        price = trend + cycle1 + cycle2 + random_walk
        prices.append(max(price, previous_close * 0.5))  # Prevent negative prices
    
    # Smooth prices slightly to avoid jaggedness
    smoothed_prices = []
    window = max(1, num_candles // 20)
    for i in range(len(prices)):
        start = max(0, i - window)
        end = min(len(prices), i + window + 1)
        avg = sum(prices[start:end]) / (end - start)
        smoothed_prices.append(avg)
    
    # Generate candles from price path
    for i in range(num_candles):
        open_price = smoothed_prices[i]
        close_price = smoothed_prices[min(i+1, num_candles-1)] if i < num_candles-1 else open_price
        
        # Add intrabar volatility (different scale per timeframe)
        intrabar_range = abs(open_price) * volatility * random.uniform(0.5, 1.5)
        high_price = max(open_price, close_price) + intrabar_range
        low_price = min(open_price, close_price) - intrabar_range
        
        # Volume increases with longer timeframes
        base_volume = 500000 * (1 + lookback_hours / 10)
        volume = int(base_volume * random.uniform(0.5, 2.0))
        
        candles.append({
            'time': (base_time + timedelta(minutes=i*interval_mins)).isoformat(),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
    
    return candles

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

# Massive.com (Polygon.io) Configuration (Fourth fallback - high frequency backup)
MASSIVE_KEY = 'D7IAUg_tLjplp07HtPFarTo6MX5uXgYw'  # Massive.com API key ✅
MASSIVE_BASE_URL = 'https://api.massive.com'  # Polygon.io rebranded to Massive.com
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

# Daily discovered stocks for demo/simulation learning
daily_discovered_stocks = []  # Stores all unique stocks found today
daily_discovered_date = None  # Track which day these stocks are from
daily_discovered_lock = threading.Lock()

# Starting symbols to scan - SMART SCALING
# 10 stocks when Yahoo/SerpAPI/AlphaVantage available (20s scans, high quota)
# Auto-reduces to 5 stocks when only Massive.com available (60s scans, 5/min limit)
SEED_SYMBOLS = [
    'GME', 'AMC', 'TSLA', 'AMD', 'PLTR',
    'SOFI', 'NIO', 'LCID', 'ATER', 'BBIG'  # Top 10 volatile stocks
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

def fetch_stock_from_serpapi(symbol: str, timeframe: str = '5m') -> Dict[str, Any]:
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
                # Generate synthetic candles for requested timeframe
                logging.info(f"📊 Generating synthetic {timeframe} candles for {symbol} (no graph data from SerpAPI)")
                candles = generate_synthetic_candles(symbol, previous_close, current_price, timeframe)
            
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
                'dataSource': 'SerpAPI',  # Tag data source
                'source': f'SerpAPI (Synthetic {timeframe} candles - current price: ${current_price})',
                'isRealData': False
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

def fetch_stock_from_alphavantage(symbol: str, timeframe: str = '5m') -> Dict[str, Any]:
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
        
        # Generate synthetic candles for requested timeframe (AlphaVantage free tier has strict rate limits for intraday data)
        logging.info(f"📊 Generating synthetic {timeframe} candles for {symbol} (saving AlphaVantage intraday quota)")
        candles = generate_synthetic_candles(symbol, previous_close, current_price, timeframe)
        
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
            'dataSource': 'AlphaVantage',
            'source': f'AlphaVantage (Synthetic {timeframe} candles - current price: ${current_price})',
            'isRealData': False
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

def fetch_stock_from_massive(symbol: str, timeframe: str = '5m') -> Dict[str, Any]:
    """Fetch stock data from Massive.com (Polygon.io) as fourth fallback (5 calls/minute)"""
    track_massive_usage()
    
    if MASSIVE_KEY == 'YOUR_MASSIVE_API_KEY':
        logging.error("❌ Massive.com key not configured! Get free key from https://massive.com")
        return None
    
    try:
        logging.info(f"🔍 Fetching {symbol} from Massive.com (Polygon.io)...")
        
        # Massive.com (Polygon.io) API - Get Previous Close for price data
        prev_close_url = f"https://api.massive.com/v2/aggs/ticker/{symbol}/prev"
        params = {'apiKey': MASSIVE_KEY}
        
        response = requests.get(prev_close_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if data exists
        if data.get('status') != 'OK' or not data.get('results'):
            logging.warning(f"⚠️ Massive.com returned no data for {symbol}")
            return None
        
        # Extract data from Polygon.io format
        result = data['results'][0] if isinstance(data['results'], list) else data['results']
        current_price = float(result.get('c', 0))  # Close price
        open_price = float(result.get('o', current_price))  # Open
        day_high = float(result.get('h', current_price))  # High
        day_low = float(result.get('l', current_price))  # Low
        volume = int(result.get('v', 1000000))  # Volume
        previous_close = float(result.get('c', current_price))  # Use close as prev close
        
        change_amount = current_price - previous_close
        change_percent = (change_amount / previous_close) * 100 if previous_close > 0 else 0
        
        logging.info(f"✅ Successfully fetched {symbol} from Massive.com: ${current_price} ({change_percent:+.2f}%)")
        
        # Generate synthetic candles for requested timeframe (rate limit is tight at 5/min, save quota)
        logging.info(f"📊 Generating synthetic {timeframe} candles for {symbol} (saving Massive.com quota)")
        candles = generate_synthetic_candles(symbol, previous_close, current_price, timeframe)
        
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
            'source': f'Massive.com (Synthetic {timeframe} candles)',
            'isRealData': False,
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

def connect_ibkr():
    """Connect to Interactive Brokers TWS/IB Gateway"""
    global IBKR_CONNECTED, IBKR_INSTANCE
    
    if not IBKR_AVAILABLE:
        return False
    
    with IBKR_LOCK:
        if IBKR_CONNECTED and IBKR_INSTANCE and IBKR_INSTANCE.isConnected():
            return True
        
        try:
            if IBKR_INSTANCE is None:
                IBKR_INSTANCE = IB()
            
            if not IBKR_INSTANCE.isConnected():
                logging.info(f"🔌 Connecting to Interactive Brokers at {IBKR_HOST}:{IBKR_PORT}...")
                IBKR_INSTANCE.connect(IBKR_HOST, IBKR_PORT, clientId=IBKR_CLIENT_ID)
                IBKR_CONNECTED = True
                logging.info("✅ Connected to Interactive Brokers!")
                return True
            else:
                IBKR_CONNECTED = True
                return True
        except Exception as e:
            logging.warning(f"⚠️ Could not connect to Interactive Brokers: {e}")
            logging.info("💡 Make sure TWS or IB Gateway is running and API is enabled")
            IBKR_CONNECTED = False
            return False

def is_market_open() -> bool:
    """Check if US stock market is currently open (9:30 AM - 4:00 PM ET, Mon-Fri)"""
    from datetime import datetime, time
    
    try:
        if pytz:
            # US Eastern Time (market timezone)
            et = pytz.timezone('US/Eastern')
            now_et = datetime.now(et)
            current_time = now_et.time()
            current_day = now_et.weekday()  # 0=Monday, 6=Sunday
            
            logging.info(f"🕐 Market status check: ET={now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}, Day={current_day}, Time={current_time}")
        else:
            # Fallback without pytz (less accurate - uses local time)
            now_et = datetime.now()
            current_time = now_et.time()
            current_day = now_et.weekday()
            logging.warning("⚠️ pytz not available - using local time (may be inaccurate)")
        
        # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        market_open_time = time(9, 30)
        market_close_time = time(16, 0)
        
        # Check if it's a weekday (Monday=0, Friday=4)
        if current_day >= 5:  # Saturday (5) or Sunday (6)
            logging.info("📴 Market is CLOSED (Weekend)")
            return False
        
        # Check if within market hours
        is_open = market_open_time <= current_time <= market_close_time
        if is_open:
            logging.info("✅ Market is OPEN")
        else:
            logging.info(f"📴 Market is CLOSED (Current: {current_time}, Hours: {market_open_time}-{market_close_time})")
        
        return is_open
    except Exception as e:
        logging.error(f"❌ Error determining market status: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False  # Assume closed if can't determine (safer)

def fetch_from_ibkr(symbol: str, timeframe: str = '5m') -> Dict[str, Any]:
    """Fetch stock data from Interactive Brokers API (DEFAULT)"""
    if not IBKR_AVAILABLE:
        return None
    
    if not connect_ibkr():
        return None
    
    market_open = is_market_open()
    
    try:
        # Map timeframe to IBKR duration and bar size
        # Extend duration to include yesterday's data when market is closed or for 24h timeframe
        timeframe_map = {
            '1m': ('2 D', '1 min'),      # 2 days to include yesterday
            '2m': ('2 D', '2 mins'),
            '5m': ('2 D', '5 mins'),     # 2 days to include yesterday
            '15m': ('2 D', '15 mins'),
            '30m': ('2 D', '30 mins'),
            '90m': ('2 D', '1 hour'),
            '1h': ('2 D', '1 hour'),     # 2 days to include yesterday
            '24h': ('2 D', '1 hour'),    # 2 days to include yesterday
            '1week': ('1 W', '1 day'),
            '1month': ('1 M', '1 day'),
            '3month': ('3 M', '1 day'),
            '6month': ('6 M', '1 day'),
            '1year': ('1 Y', '1 day'),
            '2year': ('2 Y', '1 day'),
            '5year': ('5 Y', '1 day'),
            '10year': ('10 Y', '1 day'),
            'ytd': ('1 Y', '1 day'),
            'max': ('10 Y', '1 day')
        }
        
        duration, bar_size = timeframe_map.get(timeframe, ('2 D', '5 mins'))  # Default to 2 days
        
        # Create stock contract
        contract = Stock(symbol, 'SMART', 'USD')
        
        # Request historical data - include yesterday's data
        if not market_open:
            logging.info(f"📊 Market is CLOSED - Fetching historical data for {symbol} {timeframe} (including yesterday)...")
        else:
            logging.info(f"📊 Fetching {symbol} {timeframe} data from Interactive Brokers (Market OPEN, including yesterday)...")
        
        # For 24h timeframe, extend duration to get yesterday's data too
        if timeframe == '24h':
            duration = '2 D'  # Get 2 days to include yesterday
            logging.info(f"📊 Extended duration to 2 days to include yesterday's data for {symbol}")
        
        bars = IBKR_INSTANCE.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=market_open  # Only use regular trading hours if market is open
        )
        
        if not bars:
            logging.warning(f"⚠️ No data returned from IBKR for {symbol}")
            return None
        
        # Convert to DataFrame
        df = util.df(bars)
        
        if df.empty:
            logging.warning(f"⚠️ Empty DataFrame from IBKR for {symbol}")
            return None
        
        # Get current quote with bid/ask data
        IBKR_INSTANCE.reqMktData(contract, '', False, False)
        ticker = IBKR_INSTANCE.ticker(contract)
        IBKR_INSTANCE.sleep(1)  # Wait for data
        
        current_price = float(ticker.last) if ticker.last else float(df['close'].iloc[-1])
        previous_close = float(df['close'].iloc[0]) if len(df) > 0 else current_price
        
        # Get bid/ask spread data (if available)
        bid_price = float(ticker.bid) if ticker.bid else None
        ask_price = float(ticker.ask) if ticker.ask else None
        spread = (ask_price - bid_price) if (bid_price and ask_price) else None
        spread_percent = (spread / bid_price * 100) if (bid_price and spread and bid_price > 0) else None
        
        # Get real-time volume (current day)
        current_volume = int(ticker.volume) if ticker.volume else None
        day_high = float(ticker.high) if ticker.high else float(df['high'].max()) if len(df) > 0 else current_price
        day_low = float(ticker.low) if ticker.low else float(df['low'].min()) if len(df) > 0 else current_price
        
        # Convert to candles format
        candles = []
        for idx, row in df.iterrows():
            candles.append({
                'time': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                'open': round(float(row['open']), 2),
                'high': round(float(row['high']), 2),
                'low': round(float(row['low']), 2),
                'close': round(float(row['close']), 2),
                'volume': int(row['volume'])
            })
        
        change_amount = current_price - previous_close
        change_percent = (change_amount / previous_close * 100) if previous_close > 0 else 0
        
        # Get contract details for additional info
        contract_details = IBKR_INSTANCE.reqContractDetails(contract)
        name = symbol
        if contract_details:
            name = contract_details[0].longName if contract_details[0].longName else symbol
        
        # Always fetch 24h data for AI study (if not already fetching 24h)
        chart_data = {timeframe: candles}
        candles_24h = []
        
        if timeframe != '24h':
            try:
                logging.info(f"📊 Fetching 24h data for {symbol} from IBKR (AI study)...")
                # Request 24h data with 1-hour bars
                hist_24h = IBKR_INSTANCE.reqHistoricalData(
                    contract,
                    endDateTime='',
                    durationStr='1 D',
                    barSizeSetting='1 hour',
                    whatToShow='TRADES',
                    useRTH=True
                )
                IBKR_INSTANCE.sleep(0.5)  # Wait for data
                
                if hist_24h and len(hist_24h) > 0:
                    df_24h = util.df(hist_24h)
                    if not df_24h.empty:
                        for idx, row in df_24h.iterrows():
                            candles_24h.append({
                                'time': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                                'open': round(float(row['open']), 2),
                                'high': round(float(row['high']), 2),
                                'low': round(float(row['low']), 2),
                                'close': round(float(row['close']), 2),
                                'volume': int(row['volume'])
                            })
                        chart_data['24h'] = candles_24h
                        logging.info(f"✅ Added 24h data to {symbol} ({len(candles_24h)} candles)")
                    else:
                        logging.warning(f"⚠️ Empty DataFrame for 24h data of {symbol}")
                else:
                    logging.warning(f"⚠️ No 24h bars returned from IBKR for {symbol}")
            except Exception as e:
                logging.error(f"❌ Error fetching 24h data for {symbol}: {e}")
                import traceback
                logging.error(traceback.format_exc())
        else:
            # If requesting 24h, also add it to chartData
            chart_data['24h'] = candles
            candles_24h = candles
        
        stock_data = {
            'symbol': symbol,
            'name': name,
            'currentPrice': round(current_price, 2),
            'previousClose': round(previous_close, 2),
            'openPrice': round(float(df['open'].iloc[-1]), 2) if len(df) > 0 else round(current_price, 2),
            'dayHigh': round(day_high, 2),
            'dayLow': round(day_low, 2),
            'volume': int(df['volume'].sum()) if len(df) > 0 else 0,
            'currentVolume': current_volume,  # Real-time volume from ticker
            'avgVolume': int(df['volume'].mean()) if len(df) > 0 else 0,
            'bidPrice': round(bid_price, 2) if bid_price else None,
            'askPrice': round(ask_price, 2) if ask_price else None,
            'spread': round(spread, 2) if spread else None,
            'spreadPercent': round(spread_percent, 2) if spread_percent else None,
            'changeAmount': round(change_amount, 2),
            'changePercent': round(change_percent, 2),
            'float': 0,  # IBKR doesn't provide float directly
            'marketCap': 0,  # Calculate if needed
            'candles': candles,
            'chartData': chart_data,  # Always includes 24h data
            'lastUpdated': datetime.now().isoformat(),
            'signal': 'BUY' if change_percent > 3 else ('SELL' if change_percent < -3 else 'HOLD'),
            'dataSource': 'Interactive Brokers',
            'source': f'Interactive Brokers ({timeframe} - {len(candles)} candles, 24h data included)',
            'isRealData': True,
            'marketStatus': 'OPEN' if market_open else 'CLOSED',
            'hasBidAsk': bid_price is not None and ask_price is not None  # Indicates real-time data available
        }
        
        logging.info(f"✅ Successfully fetched {symbol} from Interactive Brokers: ${current_price} ({change_percent:+.2f}%) - {len(candles)} candles, 24h data: {len(chart_data.get('24h', []))} candles")
        return stock_data
        
    except Exception as e:
        logging.error(f"❌ Error fetching {symbol} from Interactive Brokers: {e}")
        return None

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
        """
        Get stock data - DEFAULT: Interactive Brokers, Fallback: Yahoo Finance
        Always fetches 24h data for AI study
        """
        # Try Interactive Brokers FIRST (default)
        ibkr_data = fetch_from_ibkr(symbol, timeframe)
        if ibkr_data:
            # Ensure 24h data is included
            if timeframe != '24h' and '24h' not in ibkr_data.get('chartData', {}):
                logging.info(f"📊 Fetching 24h data for {symbol} from IBKR...")
                ibkr_24h = fetch_from_ibkr(symbol, '24h')
                if ibkr_24h and ibkr_24h.get('candles'):
                    ibkr_data['chartData']['24h'] = ibkr_24h['candles']
            return ibkr_data
        
        # Fallback to Yahoo Finance if IBKR unavailable
        logging.info(f"🔄 IBKR unavailable, falling back to other APIs for {symbol}")
        try:
            # SMART AUTO-SWITCHING LOGIC (Fallback APIs)
            # Priority 1: Try Massive.com (best for real-time: 5 calls/min)
            if should_use_massive():
                logging.info(f"⚡ Using Massive.com for {symbol} (PRIMARY API - 5/min)")
                try:
                    massive_data = fetch_stock_from_massive(symbol, timeframe)
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
                    serpapi_data = fetch_stock_from_serpapi(symbol, timeframe)
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
            '24h': '1d',  # Changed to 1d to get last 24 hours
            '1month': '2y'  # 2 years to get enough monthly candles
        }
        
        interval_map = {
            '1m': '1m',
            '3m': '2m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '24h': '1h',  # Changed to 1h for 24h timeframe (24 candles = 24 hours)
            '1month': '1mo'  # Monthly candles
        }
        
        period = period_map.get(timeframe, '5d')
        interval = interval_map.get(timeframe, '5m')
        
        logging.info(f"📊 Fetching history for {symbol}: period={period}, interval={interval}")
        hist = ticker.history(period=period, interval=interval)
        logging.info(f"📈 History received for {symbol}: {len(hist)} candles")
        
        # For non-24h timeframes, also fetch 24h data for AI study
        if timeframe != '24h':
            try:
                logging.info(f"📊 Also fetching 24h data for {symbol} (AI study)...")
                hist_24h = ticker.history(period='1d', interval='1h')
                if not hist_24h.empty and len(hist_24h) > 0:
                    candles_24h = []
                    for idx, row in hist_24h.iterrows():
                        candles_24h.append({
                            'time': idx.isoformat(),
                            'open': round(float(row['Open']), 2),
                            'high': round(float(row['High']), 2),
                            'low': round(float(row['Low']), 2),
                            'close': round(float(row['Close']), 2),
                            'volume': int(row['Volume'])
                        })
                    logging.info(f"✅ Fetched {len(candles_24h)} candles of 24h data for {symbol}")
            except Exception as e:
                logging.warning(f"⚠️ Could not fetch 24h data for {symbol}: {e}")
                candles_24h = []
        
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
            
        # Always fetch 24h data for AI study (regardless of requested timeframe)
        candles_24h = []
        if timeframe != '24h':
            try:
                logging.info(f"📊 Fetching 24h data for {symbol} (AI study)...")
                hist_24h = ticker.history(period='1d', interval='1h')
                if not hist_24h.empty and len(hist_24h) > 0:
                    for idx, row in hist_24h.iterrows():
                        candles_24h.append({
                            'time': idx.isoformat(),
                            'open': round(float(row['Open']), 2),
                            'high': round(float(row['High']), 2),
                            'low': round(float(row['Low']), 2),
                            'close': round(float(row['Close']), 2),
                            'volume': int(row['Volume'])
                        })
                    logging.info(f"✅ Fetched {len(candles_24h)} candles of 24h data for {symbol}")
            except Exception as e:
                logging.warning(f"⚠️ Could not fetch 24h data for {symbol}: {e}")
        
        # Prepare chart data with 24h data included
        chart_data = {timeframe: candles}
        if candles_24h:
            chart_data['24h'] = candles_24h
            logging.info(f"✅ Added 24h data to chartData for {symbol} ({len(candles_24h)} candles)")
        elif timeframe == '24h':
            chart_data['24h'] = candles
        
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
        
        # Build scan list: SMART SCALING based on API availability
        import random
        with active_symbols_lock:
            scan_symbols = list(active_symbols)
        
        # IBKR ONLY MODE - No other APIs
        ibkr_available = IBKR_AVAILABLE and connect_ibkr()
        
        if not ibkr_available:
            logging.error(f"❌ Interactive Brokers unavailable - cannot scan stocks")
            logging.error(f"💡 Make sure TWS/IB Gateway is running and logged in as {IBKR_USERNAME}")
            return []
        
        logging.info(f"🔍 Scanning {len(scan_symbols)} symbols (API: Interactive Brokers ONLY)")
        
        results = []
        newly_added = []
        
        for symbol in scan_symbols:
            # Get primary timeframe data (this already includes 24h data from get_stock_data)
            stock_data = self.get_stock_data(symbol, timeframe)
            
            if stock_data is None:
                continue
            
            # Ensure 24h data is ALWAYS included for AI study
            if 'chartData' not in stock_data:
                stock_data['chartData'] = {}
            
            if '24h' not in stock_data['chartData']:
                logging.info(f"📊 Ensuring 24h data for {symbol} (AI study requirement)...")
                try:
                    # Fetch 24h data specifically
                    stock_24h = fetch_from_ibkr(symbol, '24h')
                    if stock_24h and stock_24h.get('candles'):
                        stock_data['chartData']['24h'] = stock_24h['candles']
                        logging.info(f"✅ Added 24h data to {symbol} ({len(stock_24h['candles'])} candles)")
                    else:
                        # Use existing candles if available
                        if stock_data.get('candles'):
                            stock_data['chartData']['24h'] = stock_data['candles']
                            logging.info(f"✅ Using existing candles as 24h data for {symbol}")
                except Exception as e:
                    logging.warning(f"⚠️ Could not fetch 24h data for {symbol}: {e}")
                    # Still add existing candles if available
                    if stock_data.get('candles'):
                        stock_data['chartData']['24h'] = stock_data['candles']
            
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
                
                # Ensure chartData has current timeframe
                if timeframe not in stock_data['chartData']:
                    stock_data['chartData'][timeframe] = stock_data.get('candles', [])
                
                # Mark that 24h data is available for AI study
                stock_data['has24hData'] = '24h' in stock_data.get('chartData', {}) and len(stock_data['chartData'].get('24h', [])) > 0
                
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
    global daily_discovered_stocks, daily_discovered_date
    
    try:
        criteria = request.json
        results = scanner.filter_stocks(criteria)
        
        # Track daily discovered stocks for demo learning
        with daily_discovered_lock:
            today = datetime.now().date()
            
            # Reset daily stocks if it's a new day
            if daily_discovered_date != today:
                logging.info(f"📅 New day detected - resetting daily discovered stocks")
                daily_discovered_stocks = []
                daily_discovered_date = today
            
            # Add newly discovered stocks to today's list with FULL chart data
            for stock in results:
                # Check if stock already in today's list
                if not any(s['symbol'] == stock['symbol'] for s in daily_discovered_stocks):
                    # Ensure stock has 24h data for AI study
                    if 'chartData' not in stock:
                        stock['chartData'] = {}
                    
                    if '24h' not in stock.get('chartData', {}):
                        # Fetch 24h data specifically for AI study
                        try:
                            logging.info(f"📊 Ensuring 24h data for {stock['symbol']} (AI study requirement)...")
                            stock_24h = fetch_from_ibkr(stock['symbol'], '24h')
                            if stock_24h:
                                if stock_24h.get('candles'):
                                    stock['chartData']['24h'] = stock_24h['candles']
                                    logging.info(f"✅ Added 24h data to {stock['symbol']} ({len(stock_24h['candles'])} candles)")
                                # Also ensure 5m data for detailed view
                                if '5m' not in stock['chartData']:
                                    stock_5m = fetch_from_ibkr(stock['symbol'], '5m')
                                    if stock_5m and stock_5m.get('candles'):
                                        stock['chartData']['5m'] = stock_5m['candles']
                        except Exception as e:
                            logging.warning(f"⚠️ Could not fetch 24h data for {stock['symbol']}: {str(e)}")
                    
                    # Mark that 24h data is available
                    stock['has24hData'] = '24h' in stock.get('chartData', {}) and len(stock.get('chartData', {}).get('24h', [])) > 0
                    
                    # Store the stock with 24h data for AI study
                    daily_discovered_stocks.append(stock)
                    logging.info(f"📊 Added {stock['symbol']} to today's discovered stocks with 24h data for AI study (total: {len(daily_discovered_stocks)})")
        
        # IBKR ONLY MODE - API Status
        ibkr_connected = IBKR_AVAILABLE and IBKR_CONNECTED and (IBKR_INSTANCE and IBKR_INSTANCE.isConnected() if IBKR_INSTANCE else False)
        
        api_status = {
            'activeSource': 'Interactive Brokers' if ibkr_connected else 'Not Connected',
            'ibkrConnected': ibkr_connected,
            'ibkrHost': IBKR_HOST,
            'ibkrPort': IBKR_PORT,
            'ibkrUsername': IBKR_USERNAME,
            'fallbackAvailable': False,  # No fallbacks - IBKR only
            'recommendedInterval': 5,  # IBKR has no rate limits, can scan frequently
            'mode': 'IBKR_ONLY'
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
        
        # Rate limit errors removed - IBKR only mode has no rate limits
        # No rate limit checking needed
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/market-movers', methods=['GET'])
def get_market_movers():
    """Fetch real market movers from Interactive Brokers ONLY"""
    try:
        movers_type = request.args.get('type', 'gainers')  # gainers, losers, active
        
        if not IBKR_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Interactive Brokers API not available. Install ib-insync: pip install ib-insync'
            }), 500
        
        if not connect_ibkr():
            return jsonify({
                'success': False,
                'error': f'Cannot connect to Interactive Brokers. Make sure TWS/IB Gateway is running and logged in as {IBKR_USERNAME}'
            }), 500
        
        # Use IBKR to get market movers
        # Get popular symbols and fetch their data
        popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'NFLX', 'INTC',
                          'GME', 'AMC', 'PLTR', 'SOFI', 'NIO', 'LCID', 'ATER', 'BBIG', 'SPY', 'QQQ']
        
        stocks = []
        
        # Fetch ALL popular symbols with 24h data for AI study
        for symbol in popular_symbols:  # Process all symbols
            try:
                # Fetch from IBKR with 24h timeframe (ensures 24h data for AI study)
                logging.info(f"📊 Fetching {symbol} with 24h data for AI study...")
                stock_data = fetch_from_ibkr(symbol, '24h')
                if not stock_data:
                    logging.warning(f"⚠️ No data for {symbol}, skipping...")
                    continue
                
                # Ensure 24h data is in chartData
                if '24h' not in stock_data.get('chartData', {}):
                    if stock_data.get('candles'):
                        stock_data['chartData']['24h'] = stock_data['candles']
                        logging.info(f"✅ Added 24h data to chartData for {symbol}")
                
                # Also fetch 5m data for detailed view
                if '5m' not in stock_data.get('chartData', {}):
                    try:
                        stock_5m = fetch_from_ibkr(symbol, '5m')
                        if stock_5m and stock_5m.get('candles'):
                            stock_data['chartData']['5m'] = stock_5m['candles']
                            logging.info(f"✅ Added 5m data to chartData for {symbol}")
                    except Exception as e:
                        logging.warning(f"⚠️ Could not fetch 5m data for {symbol}: {e}")
                
                # Filter based on movers type (but still include all for study)
                change_percent = stock_data.get('changePercent', 0)
                
                # Add all stocks for study, but mark them by type
                stocks.append({
                    'symbol': stock_data['symbol'],
                    'name': stock_data['name'],
                    'currentPrice': stock_data['currentPrice'],
                    'previousClose': stock_data['previousClose'],
                    'changeAmount': stock_data['changeAmount'],
                    'changePercent': stock_data['changePercent'],
                    'volume': stock_data['volume'],
                    'avgVolume': stock_data['avgVolume'],
                    'float': stock_data.get('float', 0),
                    'dayHigh': stock_data['dayHigh'],
                    'dayLow': stock_data['dayLow'],
                    'openPrice': stock_data['openPrice'],
                    'candles': stock_data.get('candles', []),  # 24h candles as primary
                    'chartData': stock_data.get('chartData', {}),  # Includes both 24h and 5m
                    'source': f'Interactive Brokers - Real 24h Data for AI Study',
                    'isHot': abs(change_percent) > 5,
                    'signal': stock_data.get('signal', 'HOLD'),
                    'has24hData': '24h' in stock_data.get('chartData', {}),
                    'has5mData': '5m' in stock_data.get('chartData', {})
                })
                
            except Exception as e:
                logging.warning(f"⚠️ Error processing {symbol} from IBKR: {e}")
                continue
        
        # Sort by change percent, but return ALL stocks for AI study
        if movers_type == 'gainers':
            stocks.sort(key=lambda x: x['changePercent'], reverse=True)
        elif movers_type == 'losers':
            stocks.sort(key=lambda x: x['changePercent'])
        elif movers_type == 'active':
            stocks.sort(key=lambda x: x['volume'], reverse=True)
        
        # Filter by type if needed, but prioritize showing all with 24h data
        filtered_stocks = stocks
        if movers_type == 'gainers':
            filtered_stocks = [s for s in stocks if s['changePercent'] >= 0]
        elif movers_type == 'losers':
            filtered_stocks = [s for s in stocks if s['changePercent'] <= 0]
        # 'active' shows all
        
        logging.info(f"✅ Returning {len(filtered_stocks)} stocks with 24h data for AI study")
        
        return jsonify({
            'success': True,
            'stocks': filtered_stocks,  # Return ALL stocks with 24h data
            'count': len(filtered_stocks),
            'type': movers_type,
            'source': 'Interactive Brokers - All Stocks with 24h Data for AI Study',
            'allHave24hData': all(s.get('has24hData', False) for s in filtered_stocks)
        })
        
    except Exception as e:
        logging.error(f"❌ Error in get_market_movers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/daily-discovered', methods=['GET'])
def get_daily_discovered():
    """Get today's discovered stocks for demo/simulation learning"""
    try:
        with daily_discovered_lock:
            today = datetime.now().date()
            
            # If no stocks discovered yet today, return empty list
            if daily_discovered_date != today or not daily_discovered_stocks:
                return jsonify({
                    'success': True,
                    'stocks': [],
                    'count': 0,
                    'date': today.isoformat(),
                    'message': 'No stocks discovered yet today. Run live scanner first.'
                })
            
            return jsonify({
                'success': True,
                'stocks': daily_discovered_stocks,
                'count': len(daily_discovered_stocks),
                'date': daily_discovered_date.isoformat(),
                'message': f'{len(daily_discovered_stocks)} stocks discovered today'
            })
    except Exception as e:
        logging.error(f"Error fetching daily discovered stocks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock(symbol):
    """Get detailed data for a specific stock - ONLY Interactive Brokers (includes yesterday's data)"""
    try:
        timeframe = request.args.get('timeframe', '5m')
        include_yesterday = request.args.get('includeYesterday', 'true').lower() == 'true'
        market_open = is_market_open()
        
        # ONLY use Interactive Brokers - no fallbacks
        if not market_open:
            logging.info(f"📊 Market is CLOSED - Fetching historical data for {symbol} {timeframe} (including yesterday: {include_yesterday})")
        else:
            logging.info(f"📊 Fetching {timeframe} chart data for {symbol} from Interactive Brokers ONLY (Market OPEN, including yesterday: {include_yesterday})")
        
        stock_data = scanner.get_stock_data(symbol, timeframe)
        
        if stock_data:
            candle_count = len(stock_data.get('candles', []))
            market_status = stock_data.get('marketStatus', 'OPEN' if market_open else 'CLOSED')
            logging.info(f"✅ Got {timeframe} data from IBKR for {symbol} ({candle_count} candles, Market: {market_status})")
            stock_data['source'] = 'Interactive Brokers (Real Data)'
            stock_data['isRealData'] = True
            stock_data['marketStatus'] = market_status
            return jsonify({
                'success': True,
                'stock': stock_data,
                'marketStatus': market_status
            })
        else:
            logging.error(f"❌ No data available from IBKR for {symbol} {timeframe}")
            return jsonify({
                'success': False,
                'error': f'Interactive Brokers unavailable for {symbol}. Make sure TWS/IB Gateway is running and logged in.',
                'help': f'1. Start TWS or IB Gateway\n2. Log in as {IBKR_USERNAME}\n3. Enable API: Configure > API > Settings\n4. Set port: {IBKR_PORT}',
                'marketStatus': 'CLOSED' if not market_open else 'UNKNOWN'
            }), 503
    except Exception as e:
        logging.error(f"❌ Error in get_stock endpoint: {str(e)}")
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

@app.route('/api/preload-stocks', methods=['GET'])
def preload_stocks():
    """Preload popular stocks with historical data for AI trend analysis (works even when market is closed)"""
    try:
        # Popular stocks for AI to analyze trends
        popular_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'NFLX', 'INTC',
            'GME', 'AMC', 'PLTR', 'SOFI', 'NIO', 'LCID', 'SPY', 'QQQ', 'ARKK', 'TQQQ',
            'SPCE', 'RBLX', 'HOOD', 'COIN', 'RIVN', 'F', 'GM', 'BAC', 'JPM', 'WMT'
        ]
        
        if not IBKR_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Interactive Brokers API not available. Install ib-insync: pip install ib-insync'
            }), 500
        
        if not connect_ibkr():
            return jsonify({
                'success': False,
                'error': f'Cannot connect to Interactive Brokers. Make sure TWS/IB Gateway is running and logged in as {IBKR_USERNAME}'
            }), 503
        
        preloaded_stocks = []
        
        for symbol in popular_symbols:
            try:
                logging.info(f"📊 Preloading {symbol} with historical data for AI analysis...")
                # Fetch 24h data (includes yesterday) for trend analysis
                stock_data = fetch_from_ibkr(symbol, '24h')
                if stock_data:
                    # Also fetch 5m for detailed view
                    if '5m' not in stock_data.get('chartData', {}):
                        stock_5m = fetch_from_ibkr(symbol, '5m')
                        if stock_5m and stock_5m.get('candles'):
                            stock_data['chartData']['5m'] = stock_5m['candles']
                    
                    # Ensure 24h data is in chartData
                    if '24h' not in stock_data.get('chartData', {}):
                        stock_data['chartData']['24h'] = stock_data.get('candles', [])
                    
                    stock_data['has24hData'] = len(stock_data.get('chartData', {}).get('24h', [])) > 0
                    stock_data['has5mData'] = len(stock_data.get('chartData', {}).get('5m', [])) > 0
                    stock_data['preloaded'] = True
                    stock_data['source'] = 'Interactive Brokers - Preloaded for AI Analysis'
                    
                    preloaded_stocks.append(stock_data)
                    logging.info(f"✅ Preloaded {symbol} - {len(stock_data.get('candles', []))} candles")
            except Exception as e:
                logging.warning(f"⚠️ Could not preload {symbol}: {e}")
                continue
        
        logging.info(f"✅ Preloaded {len(preloaded_stocks)} stocks for AI trend analysis")
        
        return jsonify({
            'success': True,
            'stocks': preloaded_stocks,
            'count': len(preloaded_stocks),
            'source': 'Interactive Brokers - Preloaded Historical Data',
            'marketStatus': 'CLOSED' if not is_market_open() else 'OPEN',
            'note': 'These stocks are preloaded with historical data for AI trend analysis, available even when market is closed'
        })
        
    except Exception as e:
        logging.error(f"❌ Error in preload_stocks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import random
from typing import List, Dict, Any
import logging
import requests
import os
from dotenv import load_dotenv

# Ollama AI Integration
try:
    from ollama_service import (
        analyze_candlesticks_with_ollama,
        check_ollama_connection,
        teach_ollama_pattern
    )
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("⚠️ Ollama service not available. Install ollama_service.py")

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
IBKR_PORT = int(os.getenv('IBKR_PORT', '4001'))  # 4001 = default IB Gateway port, 7497 = paper trading, 7496 = live
# Use a unique client ID based on process ID, timestamp, and microseconds to avoid conflicts
import os as os_sys
# Generate highly unique client ID using:
# - Process ID (unique per process)
# - Timestamp in microseconds (high precision)
# - Random component (1-999)
# - Combined hash to ensure uniqueness
import hashlib
_current_time = time.time()
_time_microseconds = int(_current_time * 1000000) % 1000000  # Use microseconds for better uniqueness
_process_id = os_sys.getpid()
_random_component = random.randint(1, 999)
# Create a hash from all components and map to 1-999 range
_unique_string = f"{_process_id}_{_time_microseconds}_{_random_component}"
_hash_value = int(hashlib.md5(_unique_string.encode()).hexdigest()[:8], 16)
DEFAULT_CLIENT_ID = (hash_value % 998) + 1  # Ensures range 1-999, never 0
IBKR_CLIENT_ID = int(os.getenv('IBKR_CLIENT_ID', str(DEFAULT_CLIENT_ID)))
logging.info(f"🔑 [IBKR] Generated Client ID: {IBKR_CLIENT_ID} (PID: {_process_id}, Time: {_time_microseconds}μs, Random: {_random_component})")
IBKR_USERNAME = os.getenv('IBKR_USERNAME', 'userconti')
IBKR_PASSWORD = os.getenv('IBKR_PASSWORD', 'mbnadc21234')
IBKR_CONNECTED = False
IBKR_INSTANCE = None
IBKR_LOCK = threading.Lock()

# Market Data Subscription Status (Updated: Jan 26, 2026)
# Current active subscriptions from IBKR portal
MARKET_DATA_SUBSCRIPTIONS = {
    'level1': {
        'nasdaq_network_c': True,  # NASDAQ (Network C/UTP)(NP,L1) - $1.50/month
        'nyse_network_a': True,     # NYSE (Network A/CTA)(NP,L1) - $1.50/month
        'nyse_network_b': True,    # NYSE American, BATS, ARCA, IEX, Regional (NP,L1) - $1.50/month
        'us_securities_bundle': True,  # US Securities Snapshot and Futures Value Bundle (NP,L1) - $10.00/month (waived if $30+ commissions)
        'us_real_time_streaming': True,  # US Real-Time Non Consolidated Streaming Quotes (IBKR-PRO) - Fee Waived
        'enabled': True
    },
    'level2': {
        'nasdaq_totalview': True,  # NASDAQ TotalView-OpenView (NP,L2) - $16.50/month (Level 2 for BookMap)
        'nasdaq_totalview_eds': True,  # NASDAQ TotalView-OpenView EDS (NP,L2) - $1.00/month
        'enabled': True,
        'bookmap_compatible': True  # Level 2 data works with BookMap for order flow analysis
    },
    'additional': {
        'nyse_arca_imbalances': True,  # NYSE ARCA Order Imbalances - $1.00/month
        'nyse_mkt_imbalances': True,    # NYSE MKT Order Imbalances - $1.00/month
        'nyse_imbalances': True,        # NYSE Order Imbalances - $1.00/month
    },
    'subscriber_status': 'Non-Professional',  # NP status confirmed
    'total_monthly_cost': 35.00,  # USD/month (some fees may be waived)
    'activated_date': '2026-01-26',
    'features': [
        'US Securities Snapshot and Futures Value Bundle (SMART routing compatible)',
        'Level 1 quotes for all major US exchanges',
        'Level 2 order book data (NASDAQ TotalView)',
        'BookMap integration ready',
        'Enhanced order flow analysis',
        'Real-time market depth',
        'Order imbalances data',
        'Non-Consolidated streaming quotes'
    ]
}
logging.info("📊 [MARKET DATA] Current subscriptions detected:")
logging.info(f"   ✅ US Securities Snapshot and Futures Value Bundle (SMART routing)")
logging.info(f"   ✅ NASDAQ TotalView-OpenView (Level 2) - BookMap compatible")
logging.info(f"   ✅ All Level 1 networks: NASDAQ, NYSE, Regional exchanges")
logging.info(f"   ✅ Subscriber status: Non-Professional")
logging.info(f"   💰 Total cost: ${MARKET_DATA_SUBSCRIPTIONS['total_monthly_cost']}/month (some fees may be waived)")

# Auto-adjustable scanner delay (increases by 1s on errors)
SCANNER_DELAY = 12  # Starting delay in seconds
SCANNER_DELAY_LOCK = threading.Lock()
LAST_ERROR_TIME = None
ERROR_COUNT = 0

app = Flask(__name__)
CORS(app)
# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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

# News: IBKR ONLY - no external news APIs

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
# News: IBKR ONLY - no external news caching needed
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

# News fetching: IBKR ONLY - news is fetched directly from IBKR when scanning stocks
# No external news APIs needed

# News fetching: IBKR ONLY - news is fetched directly from IBKR when scanning stocks
# No external news APIs or scheduled news fetching needed

def connect_ibkr():
    """Connect to Interactive Brokers TWS/IB Gateway"""
    global IBKR_CONNECTED, IBKR_INSTANCE
    
    if not IBKR_AVAILABLE:
        logging.error("❌ [IBKR] ib_insync not available - install with: pip install ib_insync")
        return False
    
    with IBKR_LOCK:
        # Check if already connected and verify connection is still alive
        if IBKR_INSTANCE:
            try:
                if IBKR_INSTANCE.isConnected():
                    IBKR_CONNECTED = True
                    logging.debug("✅ [IBKR] Already connected and verified")
                    return True
                else:
                    # Connection lost, reset state
                    logging.warning("⚠️ [IBKR] Connection lost, will reconnect")
                    IBKR_CONNECTED = False
            except Exception as e:
                logging.warning(f"⚠️ [IBKR] Connection check failed: {e}, will reconnect")
                IBKR_CONNECTED = False
                IBKR_INSTANCE = None
        
        try:
            if IBKR_INSTANCE is None:
                logging.info(f"🔌 [IBKR] Initializing IB instance...")
                IBKR_INSTANCE = IB()
                # Start the event loop for ib_insync (required for async operations)
                util.startLoop()
                logging.info("✅ [IBKR] IB instance initialized")
            
            if not IBKR_INSTANCE.isConnected():
                logging.info(f"🔌 [IBKR] Connecting to {IBKR_HOST}:{IBKR_PORT} (Initial Client ID: {IBKR_CLIENT_ID})...")
                logging.info(f"🔌 [IBKR] Username: {IBKR_USERNAME}")
                logging.info(f"🔌 [IBKR] Process ID: {os_sys.getpid()}")
                
                # Try to connect with current client ID, if it fails try alternative IDs
                max_retries = 15  # Increased retries for better success rate
                connected = False
                current_client_id = IBKR_CLIENT_ID
                tried_ids = set()  # Track tried IDs to avoid duplicates
                
                for attempt in range(max_retries):
                    try:
                        IBKR_INSTANCE.connect(IBKR_HOST, IBKR_PORT, clientId=current_client_id, timeout=10)
                        IBKR_CONNECTED = True
                        connected = True
                        logging.info("✅ [IBKR] Successfully connected to Interactive Brokers!")
                        logging.info(f"✅ [IBKR] Connection details - Host: {IBKR_HOST}, Port: {IBKR_PORT}, Client ID: {current_client_id}")
                        # Update global client ID if we used a different one
                        if current_client_id != IBKR_CLIENT_ID:
                            logging.info(f"ℹ️ [IBKR] Using Client ID {current_client_id} (original {IBKR_CLIENT_ID} was in use)")
                        # Log Level 2 subscription status
                        if MARKET_DATA_SUBSCRIPTIONS['level2']['enabled']:
                            logging.info("📊 [MARKET DATA] Level 2 subscriptions active:")
                            logging.info("   ✅ NASDAQ TotalView-OpenView (Level 2) - BookMap compatible")
                            logging.info("   ✅ Level 1 networks: NASDAQ, NYSE, Regional exchanges")
                            logging.info("   💡 Order flow analysis and market depth available")
                        return True
                    except Exception as connect_error:
                        error_msg = str(connect_error).lower()
                        error_code = getattr(connect_error, 'code', None)
                        # Check for client ID conflict errors (error code 326 or various error messages)
                        is_client_id_error = (
                            error_code == 326 or
                            "client id is already in use" in error_msg or
                            "clientid" in error_msg or
                            "already in use" in error_msg or
                            "326" in error_msg or
                            "unable to connect as the client id" in error_msg
                        )
                        
                        if is_client_id_error:
                            # Try random available client ID (not sequential to avoid conflicts)
                            tried_ids.add(current_client_id)
                            # Generate random client ID between 1-999, avoiding already tried ones
                            candidate_found = False
                            for _ in range(100):  # Try up to 100 random IDs
                                candidate_id = random.randint(1, 999)
                                if candidate_id not in tried_ids:
                                    current_client_id = candidate_id
                                    candidate_found = True
                                    break
                            
                            if not candidate_found:
                                # If we've tried too many, use sequential fallback starting from a random point
                                start_id = random.randint(1, 999)
                                for offset in range(999):
                                    candidate_id = ((start_id + offset) % 999) + 1
                                    if candidate_id not in tried_ids:
                                        current_client_id = candidate_id
                                        break
                            
                            logging.warning(f"⚠️ [IBKR] Client ID {current_client_id if 'current_client_id' in locals() else 'unknown'} conflict detected (attempt {attempt + 1}/{max_retries})")
                            logging.warning(f"⚠️ [IBKR] Error: {error_msg[:200]}")
                            logging.info(f"🔄 [IBKR] Retrying with Client ID: {current_client_id}...")
                            time.sleep(0.5 + (attempt * 0.1))  # Increasing delay with each retry
                        else:
                            # Different error, re-raise
                            logging.error(f"❌ [IBKR] Connection error (not client ID): {error_msg[:200]}")
                            raise
                
                if not connected:
                    raise Exception(f"Failed to connect after {max_retries} attempts with different client IDs. Tried IDs: {sorted(tried_ids)}")
            else:
                IBKR_CONNECTED = True
                logging.info("✅ [IBKR] Already connected (verified)")
                return True
        except ConnectionRefusedError as e:
            error_msg = f"Connection refused to {IBKR_HOST}:{IBKR_PORT}"
            logging.error(f"❌ [IBKR] {error_msg}")
            logging.error(f"❌ [IBKR] Error details: {str(e)}")
            logging.error("💡 [IBKR] Make sure TWS or IB Gateway is running")
            logging.error("💡 [IBKR] Check: Configure > API > Settings > Enable ActiveX and Socket Clients")
            logging.error(f"💡 [IBKR] Verify port {IBKR_PORT} is correct (7497 for TWS paper, 4001 for IB Gateway)")
            IBKR_CONNECTED = False
            return False
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logging.error(f"❌ [IBKR] Connection failed: {error_type}")
            logging.error(f"❌ [IBKR] Error message: {error_msg}")
            logging.error(f"💡 [IBKR] Make sure TWS or IB Gateway is running and API is enabled")
            logging.error(f"💡 [IBKR] Check: Configure > API > Settings > Enable ActiveX and Socket Clients")
            if "already connected" in error_msg.lower():
                logging.warning("⚠️ [IBKR] Already connected to another client - check Client ID")
            IBKR_CONNECTED = False
            return False

# Keepalive thread to maintain IBKR connection
def keepalive_ibkr():
    """Periodically check and maintain IBKR connection"""
    while True:
        try:
            time.sleep(30)  # Check every 30 seconds
            if IBKR_AVAILABLE:
                with IBKR_LOCK:
                    if IBKR_INSTANCE:
                        try:
                            if not IBKR_INSTANCE.isConnected():
                                # Connection lost, try to reconnect
                                logging.warning("⚠️ [IBKR KEEPALIVE] Connection lost, attempting reconnect...")
                                global IBKR_CONNECTED
                                IBKR_CONNECTED = False
                                connect_ibkr()
                        except Exception as e:
                            logging.warning(f"⚠️ [IBKR KEEPALIVE] Error checking connection: {e}")
                            IBKR_CONNECTED = False
        except Exception as e:
            logging.error(f"❌ [IBKR KEEPALIVE] Error: {e}")

def get_scanner_delay() -> int:
    """Get current scanner delay (auto-adjusted based on errors)"""
    global SCANNER_DELAY
    with SCANNER_DELAY_LOCK:
        return SCANNER_DELAY

def _adjust_delay_on_error(error_type: str):
    """Automatically increase scanner delay by 1 second on errors (max 60s)"""
    global SCANNER_DELAY, LAST_ERROR_TIME, ERROR_COUNT
    with SCANNER_DELAY_LOCK:
        ERROR_COUNT += 1
        LAST_ERROR_TIME = datetime.now()
        
        if SCANNER_DELAY < 60:  # Max 60 seconds
            SCANNER_DELAY += 1
            logging.info(f"⏱️ Auto-adjusted scanner delay to {SCANNER_DELAY}s (error: {error_type}, total errors: {ERROR_COUNT})")
        else:
            logging.warning(f"⚠️ Scanner delay at maximum (60s) - error: {error_type}")

def is_market_open() -> bool:
    """Check if US stock market is currently open (includes premarket: 4:00 AM - 4:00 PM ET, Mon-Fri)"""
    from datetime import datetime, time
    
    try:
        try:
            import pytz
        except ImportError:
            pytz = None
        
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
        
        # Market hours: 
        # - Premarket: 4:00 AM - 9:30 AM ET
        # - Regular: 9:30 AM - 4:00 PM ET
        # - After hours: 4:00 PM - 8:00 PM ET (optional, not included here)
        premarket_start = time(4, 0)
        regular_open = time(9, 30)
        market_close = time(16, 0)
        
        # Check if it's a weekday (Monday=0, Friday=4)
        if current_day >= 5:  # Saturday (5) or Sunday (6)
            logging.info("📴 Market is CLOSED (Weekend)")
            return False
        
        # Check if within market hours (premarket OR regular hours)
        is_premarket = premarket_start <= current_time < regular_open
        is_regular = regular_open <= current_time <= market_close
        is_open = is_premarket or is_regular
        
        if is_premarket:
            logging.info(f"🌅 Market is OPEN (PREMARKET: {current_time} - Regular hours start at {regular_open})")
        elif is_regular:
            logging.info(f"✅ Market is OPEN (REGULAR HOURS: {current_time})")
        else:
            logging.info(f"📴 Market is CLOSED (Current: {current_time}, Premarket: {premarket_start}-{regular_open}, Regular: {regular_open}-{market_close})")
        
        return is_open
    except Exception as e:
        logging.error(f"❌ Error determining market status: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False  # Assume closed if can't determine (safer)

def is_premarket() -> bool:
    """Check if currently in premarket hours (4:00 AM - 9:30 AM ET, Mon-Fri)"""
    from datetime import datetime, time
    
    try:
        try:
            import pytz
        except ImportError:
            pytz = None
        
        if pytz:
            et = pytz.timezone('US/Eastern')
            now_et = datetime.now(et)
            current_time = now_et.time()
            current_day = now_et.weekday()
        else:
            now_et = datetime.now()
            current_time = now_et.time()
            current_day = now_et.weekday()
        
        # Check if it's a weekday
        if current_day >= 5:
            return False
        
        # Premarket: 4:00 AM - 9:30 AM ET
        premarket_start = time(4, 0)
        regular_open = time(9, 30)
        
        return premarket_start <= current_time < regular_open
    except Exception as e:
        logging.error(f"❌ Error determining premarket status: {e}")
        return False

def fetch_realtime_ibkr(symbol: str) -> Dict[str, Any]:
    """Fetch near real-time stock data using 1-minute historical bars (works with Snapshot Bundle)"""
    import time
    fetch_start = time.time()
    logging.info(f"📡 [IBKR REALTIME] Fetching near real-time data for {symbol}...")
    
    if not IBKR_AVAILABLE:
        logging.warning(f"⚠️ [IBKR REALTIME] [{symbol}] IBKR not available")
        return None
    
    if not connect_ibkr():
        logging.warning(f"⚠️ [IBKR REALTIME] [{symbol}] IBKR not connected")
        return None
    
    logging.info(f"✅ [IBKR REALTIME] [{symbol}] IBKR connected, using 1-minute historical bars (Snapshot Bundle compatible)...")
    
    try:
        # Create stock contract
        contract = Stock(symbol, 'SMART', 'USD')
        
        # Use 5-minute historical bars instead of streaming (works with Snapshot Bundle, faster)
        # Get the most recent 5-minute bar which is close to real-time
        logging.info(f"📡 [IBKR REALTIME] [{symbol}] Requesting 5-minute historical bars (faster than 1-min)...")
        in_premarket = is_premarket()
        use_rth = not in_premarket  # False during premarket to get premarket data
        
        # Try to get real-time market data first (fastest method)
        try:
            logging.info(f"📡 [IBKR REALTIME] [{symbol}] Trying real-time market data (fastest)...")
            ticker = IBKR_INSTANCE.reqMktData(contract, '', False, False)
            IBKR_INSTANCE.sleep(3)  # Wait 3 seconds for data to arrive
            
            # Check if we got valid data
            if ticker:
                current_price = None
                bid_price = None
                ask_price = None
                volume = 0
                
                # Try to get last price
                if hasattr(ticker, 'last') and ticker.last:
                    try:
                        current_price = float(ticker.last)
                    except (ValueError, TypeError):
                        pass
                
                # Try bid/ask
                if hasattr(ticker, 'bid') and ticker.bid:
                    try:
                        bid_price = float(ticker.bid)
                    except (ValueError, TypeError):
                        pass
                        
                if hasattr(ticker, 'ask') and ticker.ask:
                    try:
                        ask_price = float(ticker.ask)
                    except (ValueError, TypeError):
                        pass
                
                # Try volume
                if hasattr(ticker, 'volume') and ticker.volume:
                    try:
                        volume = int(ticker.volume)
                    except (ValueError, TypeError):
                        pass
                
                # Use bid/ask midpoint if no last price
                if not current_price and bid_price and ask_price:
                    current_price = (bid_price + ask_price) / 2
                elif not current_price and bid_price:
                    current_price = bid_price
                elif not current_price and ask_price:
                    current_price = ask_price
                
                if current_price:
                    logging.info(f"✅ [IBKR REALTIME] [{symbol}] Got real-time quote: ${current_price:.2f}")
                    # Cancel market data subscription
                    try:
                        IBKR_INSTANCE.cancelMktData(contract)
                    except:
                        pass
                    
                    # Get contract name
                    try:
                        contract_details = IBKR_INSTANCE.reqContractDetails(contract)
                        name = contract_details[0].longName if contract_details and len(contract_details) > 0 else symbol
                    except:
                        name = symbol
                    
                    # Use real-time data - create minimal stock data
                    return {
                        'symbol': symbol,
                        'name': name,
                        'currentPrice': round(current_price, 2),
                        'bidPrice': round(bid_price, 2) if bid_price else None,
                        'askPrice': round(ask_price, 2) if ask_price else None,
                        'volume': volume,
                        'currentVolume': volume,
                        'dayHigh': current_price,  # Approximate
                        'dayLow': current_price,   # Approximate
                        'openPrice': current_price,  # Approximate
                        'previousClose': current_price,  # Will try to get later
                        'changePercent': 0.0,  # Will calculate if we get previous close
                        'changeAmount': 0.0,
                        'realtimeOnly': True,
                        'candles': [],  # No candles for real-time only
                        'chartData': {},
                        'float': 0,
                        'avgVolume': None
                    }
        except Exception as mkt_error:
            logging.warning(f"⚠️ [IBKR REALTIME] [{symbol}] Real-time market data failed: {mkt_error}, trying historical bars...")
        
        # Fallback to historical bars if real-time fails
        try:
            bars = IBKR_INSTANCE.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr='1 D',  # Get 1 day of data (IBKR format)
                barSizeSetting='5 mins',  # Use 5-minute bars (faster, less likely to timeout)
                whatToShow='TRADES',
                useRTH=use_rth
            )
            IBKR_INSTANCE.sleep(0.3)  # Reduced wait time for faster scanning
            
            if not bars or len(bars) == 0:
                logging.warning(f"⚠️ [IBKR REALTIME] [{symbol}] No 5-minute bars received")
                return None
        except Exception as hist_error:
            logging.warning(f"⚠️ [IBKR REALTIME] [{symbol}] Historical data request failed: {hist_error}")
            return None
        
        # Get the most recent bar (last one)
        df = util.df(bars)
        if df.empty:
            logging.warning(f"⚠️ [IBKR REALTIME] [{symbol}] Empty dataframe from historical data")
            return None
        
        # Use the most recent bar for current price
        latest_bar = df.iloc[-1]
        ticker_last = latest_bar['close']  # Use close of most recent 1-min bar
        ticker_high = latest_bar['high']
        ticker_low = latest_bar['low']
        ticker_volume = latest_bar['volume']
        
        # For bid/ask, we'll use the close price as approximation (Snapshot Bundle doesn't provide streaming bid/ask)
        ticker_bid = ticker_last
        ticker_ask = ticker_last
        
        # Check if we have valid price data (not NaN)
        import math
        has_valid_price = (ticker_last and not math.isnan(float(ticker_last))) if ticker_last is not None else False
        
        if not has_valid_price:
            elapsed = time.time() - fetch_start
            logging.warning(f"⚠️ [IBKR REALTIME] [{symbol}] No valid price data after {elapsed:.2f}s")
            return None
        
        elapsed = time.time() - fetch_start
        logging.info(f"✅ [IBKR REALTIME] [{symbol}] Data received in {elapsed:.2f}s (from 5-minute bars)")
        
        # Safely log price data
        price_str = f"${ticker_last:.2f}" if (ticker_last and not math.isnan(float(ticker_last))) else "N/A"
        logging.info(f"📊 [IBKR REALTIME] [{symbol}] Price: {price_str} (from 5-min bar)")
        
        # Get real-time prices - handle NaN values
        import math
        
        def safe_float(value):
            """Safely convert to float, handling NaN"""
            if value is None:
                return None
            try:
                val = float(value)
                if math.isnan(val) or math.isinf(val):
                    return None
                return val
            except (ValueError, TypeError):
                return None
        
        def safe_int(value):
            """Safely convert to int, handling NaN"""
            if value is None:
                return None
            try:
                val = float(value)
                if math.isnan(val) or math.isinf(val):
                    return None
                return int(val)
            except (ValueError, TypeError):
                return None
        
        current_price = safe_float(ticker_last) if ticker_last is not None else None
        bid_price = safe_float(ticker_bid) if ticker_bid is not None else None
        ask_price = safe_float(ticker_ask) if ticker_ask is not None else None
        spread = (ask_price - bid_price) if (bid_price and ask_price and bid_price != ask_price) else None
        spread_percent = (spread / bid_price * 100) if (bid_price and spread and bid_price > 0) else None
        
        # Get volume and day stats from 1-minute bar
        current_volume = safe_int(ticker_volume) if ticker_volume is not None else None
        day_high = safe_float(ticker_high) if ticker_high is not None else None
        day_low = safe_float(ticker_low) if ticker_low is not None else None
        
        # If we don't have a valid current price, we can't proceed
        if current_price is None:
            elapsed = time.time() - fetch_start
            logging.warning(f"⚠️ [IBKR REALTIME] [{symbol}] No valid price data after {elapsed:.2f}s")
            return None
        
        # Get contract details for name
        contract_details = IBKR_INSTANCE.reqContractDetails(contract)
        name = symbol
        if contract_details:
            name = contract_details[0].longName if contract_details[0].longName else symbol
        
        # For fast screening, skip previous close fetch (too slow)
        # Just use current price as previous close (change will be 0%, but stock will still show)
        previous_close = current_price
        logging.debug(f"📊 [IBKR REALTIME] [{symbol}] Using current price as previous close for fast screening")
        
        change_amount = (current_price - previous_close) if (current_price and previous_close) else 0
        change_percent = (change_amount / previous_close * 100) if previous_close > 0 else 0
        
        market_open = is_market_open()
        total_elapsed = time.time() - fetch_start
        
        result = {
            'symbol': symbol,
            'name': name,
            'currentPrice': round(current_price, 2) if current_price else None,
            'previousClose': round(previous_close, 2) if previous_close else None,
            'dayHigh': round(day_high, 2) if day_high else None,
            'dayLow': round(day_low, 2) if day_low else None,
            'currentVolume': current_volume,
            'bidPrice': round(bid_price, 2) if bid_price else None,
            'askPrice': round(ask_price, 2) if ask_price else None,
            'spread': round(spread, 2) if spread else None,
            'spreadPercent': round(spread_percent, 2) if spread_percent else None,
            'changeAmount': round(change_amount, 2),
            'changePercent': round(change_percent, 2),
            'candles': [],  # No candles for real-time only
            'chartData': {},  # Will be filled if historical data needed
            'lastUpdated': datetime.now().isoformat(),
            'signal': 'BUY' if change_percent > 3 else ('SELL' if change_percent < -3 else 'HOLD'),
            'dataSource': 'Interactive Brokers',
            'source': 'Interactive Brokers (Real-time Screening)',
            'isRealData': True,
            'marketStatus': 'PREMARKET' if is_premarket() else ('OPEN' if market_open else 'CLOSED'),
            'hasBidAsk': bid_price is not None and ask_price is not None,
            'realtimeOnly': True,  # Flag to indicate this is real-time only
            'float': 0,  # Not available in real-time
            'avgVolume': None  # Would need historical data
        }
        
        logging.info(f"✅ [IBKR REALTIME] [{symbol}] Real-time data complete in {total_elapsed:.2f}s")
        logging.info(f"📊 [IBKR REALTIME] [{symbol}] Final data: price=${result['currentPrice']}, change={result['changePercent']}%, volume={result['currentVolume']}")
        
        return result
    except Exception as e:
        import traceback
        elapsed = time.time() - fetch_start
        logging.error(f"❌ [IBKR REALTIME] [{symbol}] Error after {elapsed:.2f}s: {e}")
        logging.error(f"❌ [IBKR REALTIME] [{symbol}] Traceback:\n{traceback.format_exc()}")
        return None

def fetch_from_ibkr(symbol: str, timeframe: str = '5m') -> Dict[str, Any]:
    """Fetch stock data from Interactive Brokers API (DEFAULT - Full historical data)"""
    try:
        if not IBKR_AVAILABLE:
            logging.debug(f"⚠️ [IBKR] IBKR not available for {symbol}")
            return None
        
        if not connect_ibkr():
            logging.debug(f"⚠️ [IBKR] Could not connect to IBKR for {symbol}")
            return None
    except Exception as connect_error:
        logging.error(f"❌ [IBKR] Error checking IBKR availability for {symbol}: {connect_error}")
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
            '4h': ('1 W', '4 hours'),   # 1 week for 4h timeframe
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
        in_premarket = is_premarket()
        if not market_open:
            logging.info(f"📊 Market is CLOSED - Fetching historical data for {symbol} {timeframe} (including yesterday)...")
        elif in_premarket:
            logging.info(f"🌅 Market is PREMARKET - Fetching {symbol} {timeframe} data from Interactive Brokers (premarket hours)...")
        else:
            logging.info(f"📊 Fetching {symbol} {timeframe} data from Interactive Brokers (Market OPEN, including yesterday)...")
        
        # For 24h timeframe, extend duration to get yesterday's data too
        if timeframe == '24h':
            duration = '2 D'  # Get 2 days to include yesterday
            logging.info(f"📊 Extended duration to 2 days to include yesterday's data for {symbol}")
        
        # During premarket, use useRTH=False to get premarket data
        # During regular hours, use useRTH=True for regular trading hours only
        # When market is closed, use useRTH=True to get last regular session data
        use_rth = not in_premarket  # False during premarket to get premarket data, True otherwise
        
        bars = IBKR_INSTANCE.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=use_rth  # False during premarket to include premarket data
        )
        
        if not bars:
            logging.warning(f"⚠️ No data returned from IBKR for {symbol}")
            _adjust_delay_on_error("No data returned")
            return None
        
        # Convert to DataFrame
        df = util.df(bars)
        
        if df.empty:
            logging.warning(f"⚠️ Empty DataFrame from IBKR for {symbol}")
            _adjust_delay_on_error("Empty DataFrame")
            return None
        
        # Get current quote with bid/ask data
        IBKR_INSTANCE.reqMktData(contract, '', False, False)
        ticker = IBKR_INSTANCE.ticker(contract)
        IBKR_INSTANCE.sleep(0.3)  # Further reduced wait time for faster scanning
        
        # Helper function to safely convert values, handling NaN
        import math
        def safe_float_convert(value, default=None):
            """Safely convert to float, handling NaN"""
            if value is None:
                return default
            try:
                val = float(value)
                if math.isnan(val) or math.isinf(val):
                    return default
                return val
            except (ValueError, TypeError):
                return default
        
        def safe_int_convert(value, default=None):
            """Safely convert to int, handling NaN"""
            if value is None:
                return default
            try:
                val = float(value)
                if math.isnan(val) or math.isinf(val):
                    return default
                return int(val)
            except (ValueError, TypeError):
                return default
        
        # Get current price - prefer ticker.last, fallback to historical close
        ticker_price = safe_float_convert(ticker.last) if ticker.last else None
        hist_close = safe_float_convert(df['close'].iloc[-1]) if len(df) > 0 else None
        current_price = ticker_price if ticker_price else hist_close
        
        if current_price is None:
            logging.error(f"❌ [IBKR] [{symbol}] No valid price data available")
            return None
        
        previous_close = safe_float_convert(df['close'].iloc[0]) if len(df) > 0 else current_price
        
        # Get bid/ask spread data (if available)
        bid_price = safe_float_convert(ticker.bid) if ticker.bid else None
        ask_price = safe_float_convert(ticker.ask) if ticker.ask else None
        spread = (ask_price - bid_price) if (bid_price and ask_price) else None
        spread_percent = (spread / bid_price * 100) if (bid_price and spread and bid_price > 0) else None
        
        # Get real-time volume (current day)
        current_volume = safe_int_convert(ticker.volume) if ticker.volume else None
        ticker_high = safe_float_convert(ticker.high) if ticker.high else None
        ticker_low = safe_float_convert(ticker.low) if ticker.low else None
        hist_high = safe_float_convert(df['high'].max()) if len(df) > 0 else None
        hist_low = safe_float_convert(df['low'].min()) if len(df) > 0 else None
        day_high = ticker_high if ticker_high else (hist_high if hist_high else current_price)
        day_low = ticker_low if ticker_low else (hist_low if hist_low else current_price)
        
        # Convert to candles format - handle NaN values
        candles = []
        for idx, row in df.iterrows():
            try:
                open_val = safe_float_convert(row['open'], 0)
                high_val = safe_float_convert(row['high'], 0)
                low_val = safe_float_convert(row['low'], 0)
                close_val = safe_float_convert(row['close'], 0)
                vol_val = safe_int_convert(row['volume'], 0)
                
                # Skip candles with invalid data
                if open_val == 0 and high_val == 0 and low_val == 0 and close_val == 0:
                    continue
                
                candles.append({
                    'time': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    'open': round(open_val, 2),
                    'high': round(high_val, 2),
                    'low': round(low_val, 2),
                    'close': round(close_val, 2),
                    'volume': vol_val
                })
            except Exception as e:
                logging.warning(f"⚠️ [IBKR] [{symbol}] Error converting candle data: {e}")
                continue
        
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
                # During premarket, include premarket data (useRTH=False)
                in_premarket = is_premarket()
                hist_24h = IBKR_INSTANCE.reqHistoricalData(
                    contract,
                    endDateTime='',
                    durationStr='1 D',
                    barSizeSetting='1 hour',
                    whatToShow='TRADES',
                    useRTH=not in_premarket  # False during premarket to include premarket data
                )
                IBKR_INSTANCE.sleep(0.5)  # Wait for data
                
                if hist_24h and len(hist_24h) > 0:
                    df_24h = util.df(hist_24h)
                    if not df_24h.empty:
                        for idx, row in df_24h.iterrows():
                            try:
                                open_val = safe_float_convert(row['open'], 0)
                                high_val = safe_float_convert(row['high'], 0)
                                low_val = safe_float_convert(row['low'], 0)
                                close_val = safe_float_convert(row['close'], 0)
                                vol_val = safe_int_convert(row['volume'], 0)
                                
                                # Skip invalid candles
                                if open_val == 0 and high_val == 0 and low_val == 0 and close_val == 0:
                                    continue
                                
                                candles_24h.append({
                                    'time': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                                    'open': round(open_val, 2),
                                    'high': round(high_val, 2),
                                    'low': round(low_val, 2),
                                    'close': round(close_val, 2),
                                    'volume': vol_val
                                })
                            except Exception as e:
                                logging.warning(f"⚠️ [IBKR] [{symbol}] Error converting 24h candle: {e}")
                                continue
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
        
        # Float data: IBKR doesn't provide float, and we're IBKR-only (no other APIs)
        # Float filter is disabled anyway, so we don't need to fetch it
        float_shares = 0
        float_source = None
        
        # Fetch IBKR news for this stock
        ibkr_news = []
        try:
            # Get contract details first to get conId
            if contract_details and len(contract_details) > 0:
                con_id = contract_details[0].contract.conId
                logging.info(f"📰 Fetching IBKR news for {symbol} (conId: {con_id})...")
                
                # Request news headlines
                news_headlines = IBKR_INSTANCE.reqNewsHeadlines(
                    con_id,
                    '',
                    ''
                )
                IBKR_INSTANCE.sleep(0.5)  # Wait for news data
                
                if news_headlines and len(news_headlines) > 0:
                    for headline in news_headlines[:5]:  # Limit to 5 most recent
                        try:
                            # Format news item
                            news_item = {
                                'title': headline.headline if hasattr(headline, 'headline') else '',
                                'time': headline.time.isoformat() if hasattr(headline, 'time') and headline.time else datetime.now().isoformat(),
                                'provider': headline.providerCode if hasattr(headline, 'providerCode') else 'IBKR',
                                'articleId': headline.articleId if hasattr(headline, 'articleId') else '',
                                'source': 'Interactive Brokers',
                                'url': f"https://www.interactivebrokers.com/en/index.php?f=news&id={headline.articleId}" if hasattr(headline, 'articleId') else None
                            }
                            ibkr_news.append(news_item)
                        except Exception as e:
                            logging.debug(f"Error formatting news headline for {symbol}: {e}")
                            continue
                    
                    logging.info(f"✅ Found {len(ibkr_news)} IBKR news items for {symbol}")
                else:
                    logging.debug(f"ℹ️ No IBKR news headlines found for {symbol}")
            else:
                logging.debug(f"ℹ️ Could not get contract details for {symbol} - skipping IBKR news")
        except Exception as e:
            logging.debug(f"⚠️ Could not fetch IBKR news for {symbol}: {e}")
            # IBKR news is optional, continue without it
        
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
            'float': int(float_shares) if float_shares and float_shares > 0 else 0,  # From Massive.com only (IBKR doesn't provide)
            'floatSource': float_source if float_source else None,  # Track which source provided float (Massive.com or None)
            'marketCap': 0,  # Calculate if needed
            'candles': candles,
            'chartData': chart_data,  # Always includes 24h data
            'lastUpdated': datetime.now().isoformat(),
            'signal': 'BUY' if change_percent > 3 else ('SELL' if change_percent < -3 else 'HOLD'),
            'dataSource': 'Interactive Brokers',
            'source': f'Interactive Brokers ({timeframe} - {len(candles)} candles, 24h data included)',
            'isRealData': True,
            'marketStatus': 'PREMARKET' if is_premarket() else ('OPEN' if market_open else 'CLOSED'),
            'hasBidAsk': bid_price is not None and ask_price is not None,  # Indicates real-time data available
            'ibkrNews': ibkr_news,  # IBKR news headlines
            'hasNews': len(ibkr_news) > 0,
            'newsCount': len(ibkr_news)
        }
        
        logging.info(f"✅ Successfully fetched {symbol} from Interactive Brokers: ${current_price} ({change_percent:+.2f}%) - {len(candles)} candles, 24h data: {len(chart_data.get('24h', []))} candles")
        return stock_data
        
    except Exception as e:
        error_msg = str(e).lower()
        logging.error(f"❌ Error fetching {symbol} from Interactive Brokers: {e}")
        
        # Check for rate limit or pacing violation errors
        if any(keyword in error_msg for keyword in ['rate limit', 'pacing violation', '60 requests', 'throttle', 'too many requests', '429']):
            _adjust_delay_on_error("Rate limit/pacing violation detected")
        
        return None

class StockScanner:
    def __init__(self):
        # Note: symbols are now managed globally in active_symbols (auto-expands)
        self.symbols = SEED_SYMBOLS  # Not used anymore, kept for compatibility
        self.min_price = 1.0
        self.max_price = 6.0
        self.max_float = 10_000_000  # 10M shares
        self.min_gain_percent = 10.0
        self.volume_multiplier = 4.0
        
    def get_stock_data(self, symbol: str, timeframe: str = '5m') -> Dict[str, Any]:
        """
        Get stock data - DEFAULT: Interactive Brokers, Fallback: Yahoo Finance
        Always fetches 24h data for AI study
        """
        # Try Interactive Brokers FIRST (default)
        try:
            ibkr_data = fetch_from_ibkr(symbol, timeframe)
        except Exception as ibkr_error:
            logging.error(f"❌ [GET_STOCK_DATA] fetch_from_ibkr failed for {symbol}: {ibkr_error}")
            import traceback
            logging.error(traceback.format_exc())
            ibkr_data = None
        
        if ibkr_data:
            # Skip 24h data fetch during search to speed up (can cause timeouts)
            # 24h data can be fetched later when viewing stock details
            # Only add 24h if it's already in the data (from previous fetch)
            if '24h' not in ibkr_data.get('chartData', {}):
                # Use existing candles as 24h data if available (fast)
                if ibkr_data.get('candles') and len(ibkr_data.get('candles', [])) > 0:
                    if 'chartData' not in ibkr_data:
                        ibkr_data['chartData'] = {}
                    ibkr_data['chartData']['24h'] = ibkr_data['candles']
                    logging.debug(f"📊 Using existing candles as 24h data for {symbol} (fast mode)")
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
        import time
        filter_start = time.time()
        
        logging.info(f"🔍 [SCANNER] ===== FILTER_STOCKS START =====")
        
        min_price = criteria.get('minPrice', self.min_price)
        max_price = criteria.get('maxPrice', self.max_price)
        max_float = criteria.get('maxFloat', self.max_float)
        min_gain = criteria.get('minGainPercent', self.min_gain_percent)
        vol_multiplier = criteria.get('volumeMultiplier', self.volume_multiplier)
        timeframe = criteria.get('chartTimeframe', '5m')
        display_count = criteria.get('displayCount', 5)
        
        logging.info(f"🔍 [SCANNER] Filter criteria:")
        logging.info(f"   - Price: ${min_price} - ${max_price}")
        logging.info(f"   - Max Float: {max_float:,}")
        logging.info(f"   - Min Gain: {min_gain}%")
        logging.info(f"   - Volume Multiplier: {vol_multiplier}x")
        logging.info(f"   - Timeframe: {timeframe}")
        logging.info(f"   - Display Count: {display_count}")
        
        # Build scan list: SMART SCALING based on API availability
        import random
        with active_symbols_lock:
            scan_symbols = list(active_symbols)
        
        # Limit to first 3 symbols to get more results (with increased timeout)
        if len(scan_symbols) > 3:
            scan_symbols = scan_symbols[:3]
            logging.info(f"🔍 [SCANNER] Limited scan to 3 symbols to balance speed and results")
        
        logging.info(f"🔍 [SCANNER] Scanning {len(scan_symbols)} symbols: {', '.join(scan_symbols)}")
        
        # IBKR ONLY MODE - No other APIs
        # Note: Connection check is already done in scan_stocks() endpoint before calling filter_stocks()
        # Just verify connection status here without retrying (to avoid duplicate warnings)
        logging.info(f"🔍 [SCANNER] Verifying IBKR connection status...")
        
        # Safely check IBKR connection status
        ibkr_available = False
        try:
            if IBKR_AVAILABLE and IBKR_CONNECTED and IBKR_INSTANCE:
                try:
                    ibkr_available = IBKR_INSTANCE.isConnected()
                except Exception as check_error:
                    logging.warning(f"⚠️ [SCANNER] Error checking IBKR connection: {check_error}")
                    ibkr_available = False
        except Exception as e:
            logging.warning(f"⚠️ [SCANNER] Error accessing IBKR instance: {e}")
            ibkr_available = False
        
        if not ibkr_available:
            logging.error(f"❌ [SCANNER] IBKR not available - connection should have been established in scan_stocks()")
            logging.error(f"💡 Make sure TWS/IB Gateway is running and logged in as {IBKR_USERNAME}")
            return []
        
        logging.info(f"✅ [SCANNER] IBKR is connected and ready")
        
        # OPTION 2: Real-time Screening (DEFAULT) - Fast, 10-20 stocks per minute
        logging.info(f"🔍 [SCANNER] Starting REAL-TIME screening (10-20 stocks/min)")
        
        results = []
        newly_added = []
        symbol_count = 0
        
        for symbol in scan_symbols:
            symbol_count += 1
            symbol_start = time.time()
            logging.info(f"🔍 [SCANNER] [{symbol_count}/{len(scan_symbols)}] Processing {symbol}...")
            
            # Add timeout protection for each symbol (max 60 seconds per symbol to allow for slow IBKR responses)
            stock_data = None
            try:
                # Use real-time screening first (FAST - reqMktData)
                try:
                    logging.info(f"📡 [SCANNER] [{symbol}] Fetching real-time data (fast mode)...")
                    stock_data = fetch_realtime_ibkr(symbol)
                    if stock_data:
                        logging.info(f"✅ [SCANNER] [{symbol}] Real-time data received")
                except Exception as rt_error:
                    logging.warning(f"⚠️ [SCANNER] [{symbol}] Real-time fetch failed: {rt_error}")
                
                # If real-time fails, fall back to full historical data (with timeout)
                if not stock_data:
                    logging.info(f"📊 [SCANNER] [{symbol}] Real-time unavailable, trying historical data...")
                    try:
                        stock_data = self.get_stock_data(symbol, timeframe)
                        if stock_data:
                            logging.info(f"✅ [SCANNER] [{symbol}] Historical data received")
                    except Exception as hist_error:
                        logging.warning(f"⚠️ [SCANNER] [{symbol}] Historical data fetch failed: {hist_error}")
                        
            except Exception as symbol_error:
                symbol_elapsed = time.time() - symbol_start
                logging.error(f"❌ [SCANNER] [{symbol}] Error after {symbol_elapsed:.2f}s: {symbol_error}")
                # Continue to next symbol - don't fail entire scan
                continue
            
            if stock_data is None:
                continue
            
            # For real-time only data, we need to handle volume differently
            # Real-time doesn't have avgVolume, so we'll skip volume multiplier check for real-time
            is_realtime_only = stock_data.get('realtimeOnly', False)
            
            # If real-time only data, use it as-is (don't try to fetch historical - too slow)
            # Accept real-time data even without full historical to show stocks faster
            if is_realtime_only:
                # Set defaults for missing fields
                if 'changePercent' not in stock_data or stock_data.get('changePercent') is None:
                    # Estimate change if we have previous close
                    if stock_data.get('previousClose') and stock_data.get('currentPrice'):
                        change = stock_data['currentPrice'] - stock_data['previousClose']
                        stock_data['changePercent'] = (change / stock_data['previousClose'] * 100) if stock_data['previousClose'] > 0 else 0.0
                        stock_data['changeAmount'] = change
                    else:
                        stock_data['changePercent'] = 0.0
                        stock_data['changeAmount'] = 0.0
                
                # Set defaults for missing required fields
                stock_data.setdefault('openPrice', stock_data.get('currentPrice', 0))
                stock_data.setdefault('dayHigh', stock_data.get('currentPrice', 0))
                stock_data.setdefault('dayLow', stock_data.get('currentPrice', 0))
                stock_data.setdefault('volume', 0)
                stock_data.setdefault('avgVolume', 0)
                stock_data.setdefault('float', 0)
                stock_data.setdefault('candles', [])
                stock_data.setdefault('chartData', {})
                
                logging.info(f"✅ [SCANNER] [{symbol}] Using real-time data (fast mode, no historical fetch)")
            
            # Ensure 24h data is ALWAYS included for AI study (if not real-time only)
            if not is_realtime_only:
                if 'chartData' not in stock_data:
                    stock_data['chartData'] = {}
                
                # Skip 24h data fetch during scan to speed up (can be fetched later if needed)
                # This significantly speeds up the scan process
                if '24h' not in stock_data['chartData']:
                    # Use existing candles as 24h data if available (faster)
                    if stock_data.get('candles'):
                        stock_data['chartData']['24h'] = stock_data['candles']
                        logging.debug(f"📊 Using existing candles as 24h data for {symbol} (fast mode)")
                    # Don't fetch 24h data during scan - too slow
                    # Can be fetched later when viewing stock details
            
            # Apply filters
            logging.info(f"🔍 [SCANNER] [{symbol}] Applying filters...")
            price_check = stock_data.get('currentPrice') and min_price <= stock_data['currentPrice'] <= max_price
            logging.info(f"🔍 [SCANNER] [{symbol}] Price check: ${stock_data.get('currentPrice')} in range ${min_price}-${max_price} = {price_check}")
            
            # Float check: DISABLED - not scanning for float
            float_check = True  # Always pass float check (float filter disabled)
            logging.info(f"🔍 [SCANNER] [{symbol}] Float check: DISABLED (always passes)")
            
            gain_check = stock_data.get('changePercent', 0) >= min_gain
            logging.info(f"🔍 [SCANNER] [{symbol}] Gain check: {stock_data.get('changePercent', 0)}% >= {min_gain}% = {gain_check}")
            
            # Volume check: skip if real-time only and no avgVolume, or check if available
            # For real-time data, always pass volume check (we don't have avgVolume)
            if is_realtime_only:
                volume_check = True  # Always pass for real-time data
                logging.info(f"🔍 [SCANNER] [{symbol}] Volume check: PASSED (real-time data, no avgVolume available)")
            else:
                avg_vol = stock_data.get('avgVolume', 0) or 0
                current_vol = stock_data.get('volume', 0) or stock_data.get('currentVolume', 0) or 0
                volume_check = current_vol >= (avg_vol * vol_multiplier) if avg_vol > 0 else True
                logging.info(f"🔍 [SCANNER] [{symbol}] Volume check: {current_vol:,} >= {avg_vol:,} * {vol_multiplier} = {volume_check}")
            
            all_checks = price_check and float_check and gain_check and volume_check
            logging.info(f"🔍 [SCANNER] [{symbol}] All filters: price={price_check}, float={float_check}, gain={gain_check}, volume={volume_check} = {all_checks}")
            
            if all_checks:
                symbol_elapsed = time.time() - symbol_start
                logging.info(f"✅ [SCANNER] [{symbol}] QUALIFIED! (took {symbol_elapsed:.2f}s)")
                logging.info(f"✅ [SCANNER] [{symbol}] Stock data: {stock_data['name']}, ${stock_data.get('currentPrice')}, {stock_data.get('changePercent')}%")
                
                # Stock qualifies! Add to active symbols if new
                with active_symbols_lock:
                    if symbol not in active_symbols:
                        active_symbols.add(symbol)
                        newly_added.append(symbol)
                        logging.info(f"🆕 [SCANNER] NEW MOVER DISCOVERED: {symbol} - {stock_data['name']} (+{stock_data['changePercent']:.2f}%)")
                    else:
                        logging.info(f"✅ [SCANNER] [{symbol}] Already in active symbols list")
                
                # Calculate signal
                if stock_data['changePercent'] > 15 and stock_data['volume'] > stock_data['avgVolume'] * 3:
                    stock_data['signal'] = 'BUY'
                elif stock_data['changePercent'] < -5:
                    stock_data['signal'] = 'SELL'
                else:
                    stock_data['signal'] = 'HOLD'
                
                stock_data['isHot'] = stock_data['volume'] > stock_data['avgVolume'] * 5
                
                # Check if this stock has news (IBKR ONLY - no external news sources)
                ibkr_news = stock_data.get('ibkrNews', [])
                stock_data['hasNews'] = len(ibkr_news) > 0
                stock_data['newsCount'] = len(ibkr_news)
                stock_data['allNews'] = ibkr_news  # IBKR news only
                stock_data['ibkrNewsCount'] = len(ibkr_news)
                
                # Ensure chartData has current timeframe
                if timeframe not in stock_data['chartData']:
                    stock_data['chartData'][timeframe] = stock_data.get('candles', [])
                
                # Mark that 24h data is available for AI study
                stock_data['has24hData'] = '24h' in stock_data.get('chartData', {}) and len(stock_data['chartData'].get('24h', [])) > 0
                
                results.append(stock_data)
            else:
                symbol_elapsed = time.time() - symbol_start
                logging.info(f"❌ [SCANNER] [{symbol}] Did not qualify (took {symbol_elapsed:.2f}s)")
        
        # Sort by change percent (highest first)
        results.sort(key=lambda x: x['changePercent'], reverse=True)
        
        # Log summary
        total_elapsed = time.time() - filter_start
        with active_symbols_lock:
            total_active = len(active_symbols)
        
        logging.info(f"🔍 [SCANNER] ===== FILTER_STOCKS COMPLETE =====")
        logging.info(f"🔍 [SCANNER] Total time: {total_elapsed:.2f}s")
        logging.info(f"🔍 [SCANNER] Symbols processed: {len(scan_symbols)}")
        logging.info(f"🔍 [SCANNER] Stocks qualified: {len(results)}")
        logging.info(f"🔍 [SCANNER] New symbols added: {len(newly_added)}")
        logging.info(f"🔍 [SCANNER] Total active symbols: {total_active}")
        
        if newly_added:
            logging.info(f"🎯 [SCANNER] Scan complete: {len(results)} qualifying stocks | {len(newly_added)} NEW symbols added: {', '.join(newly_added)}")
        else:
            logging.info(f"🎯 [SCANNER] Scan complete: {len(results)} qualifying stocks | Total active symbols: {total_active}")
        
        return results[:display_count]

scanner = StockScanner()

@app.route('/api/scan', methods=['POST'])
def scan_stocks():
    """Scan stocks with given criteria"""
    global daily_discovered_stocks, daily_discovered_date
    import time
    scan_start = time.time()
    
    logging.info(f"🔍 [SCANNER API] ===== SCAN REQUEST RECEIVED =====")
    
    try:
        # CRITICAL: Ensure IBKR is connected before scanning
        logging.info(f"🔍 [SCANNER API] Checking IBKR connection status...")
        
        # Check current connection status
        ibkr_currently_connected = (
            IBKR_AVAILABLE and 
            IBKR_CONNECTED and 
            IBKR_INSTANCE and 
            IBKR_INSTANCE.isConnected() if IBKR_INSTANCE else False
        )
        
        if not ibkr_currently_connected:
            logging.warning(f"⚠️ [SCANNER API] IBKR not connected, attempting to connect...")
            
            # Attempt to connect with retries
            max_connection_retries = 3
            connection_successful = False
            
            for conn_attempt in range(max_connection_retries):
                logging.info(f"🔌 [SCANNER API] IBKR connection attempt {conn_attempt + 1}/{max_connection_retries}...")
                connection_successful = connect_ibkr()
                
                if connection_successful:
                    # Verify connection is actually active
                    if IBKR_INSTANCE and IBKR_INSTANCE.isConnected():
                        logging.info(f"✅ [SCANNER API] IBKR connected successfully!")
                        connection_successful = True
                        break
                    else:
                        logging.warning(f"⚠️ [SCANNER API] Connection returned True but instance not connected, retrying...")
                        connection_successful = False
                
                if conn_attempt < max_connection_retries - 1:
                    time.sleep(2)  # Wait before retry
            
            if not connection_successful:
                error_msg = "IBKR connection failed. Please ensure IB Gateway or TWS is running and API is enabled."
                logging.error(f"❌ [SCANNER API] {error_msg}")
                return jsonify({
                    'error': error_msg,
                    'details': {
                        'ibkrAvailable': IBKR_AVAILABLE,
                        'ibkrConnected': False,
                        'ibkrHost': IBKR_HOST,
                        'ibkrPort': IBKR_PORT,
                        'suggestion': 'Check: Configure > API > Settings > Enable ActiveX and Socket Clients'
                    }
                }), 503  # Service Unavailable
        else:
            logging.info(f"✅ [SCANNER API] IBKR already connected, proceeding with scan...")
        
        criteria = request.json
        logging.info(f"🔍 [SCANNER API] Scan criteria received:")
        logging.info(f"   - minPrice: {criteria.get('minPrice')}")
        logging.info(f"   - maxPrice: {criteria.get('maxPrice')}")
        logging.info(f"   - maxFloat: {criteria.get('maxFloat')}")
        logging.info(f"   - minGainPercent: {criteria.get('minGainPercent')}")
        logging.info(f"   - volumeMultiplier: {criteria.get('volumeMultiplier')}")
        logging.info(f"   - displayCount: {criteria.get('displayCount')}")
        logging.info(f"   - chartTimeframe: {criteria.get('chartTimeframe')}")
        
        logging.info(f"🔍 [SCANNER API] Calling scanner.filter_stocks()...")
        filter_start = time.time()
        
        # Add timeout protection for scan (max 280 seconds to allow frontend 300s timeout)
        try:
            results = scanner.filter_stocks(criteria)
        except Exception as scan_error:
            scan_elapsed = time.time() - filter_start
            logging.error(f"❌ [SCANNER API] filter_stocks failed after {scan_elapsed:.2f}s: {scan_error}")
            import traceback
            logging.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Scan failed: {str(scan_error)}',
                'stocks': [],
                'timestamp': datetime.now().isoformat()
            }), 500
        
        filter_elapsed = time.time() - filter_start
        logging.info(f"✅ [SCANNER API] filter_stocks completed in {filter_elapsed:.2f}s, returned {len(results)} stocks")
        
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
                    
                    # Skip 24h data fetch during scan to speed up (can cause timeouts)
                    # 24h data can be fetched later when viewing stock details
                    if '24h' not in stock.get('chartData', {}):
                        # Use existing candles as 24h data if available (fast)
                        if stock.get('candles') and len(stock.get('candles', [])) > 0:
                            stock['chartData']['24h'] = stock['candles']
                            logging.debug(f"📊 Using existing candles as 24h data for {stock['symbol']} (fast mode)")
                        # Don't fetch 24h data during scan - too slow and causes timeouts
                    
                    # Mark that 24h data is available
                    stock['has24hData'] = '24h' in stock.get('chartData', {}) and len(stock.get('chartData', {}).get('24h', [])) > 0
                    
                    # Store the stock with 24h data for AI study
                    # AI ONLY learns from stocks that pass scanner filters
                    daily_discovered_stocks.append(stock)
                    logging.info(f"📊 Added {stock['symbol']} to today's discovered stocks for AI learning (scanner pick only, total: {len(daily_discovered_stocks)})")
        
        # IBKR ONLY MODE - API Status (verify connection is still active)
        ibkr_connected = IBKR_AVAILABLE and IBKR_CONNECTED and (IBKR_INSTANCE and IBKR_INSTANCE.isConnected() if IBKR_INSTANCE else False)
        
        # Final verification - if somehow disconnected during scan, log warning
        if not ibkr_connected:
            logging.warning(f"⚠️ [SCANNER API] IBKR connection lost during scan, but scan completed")
        
        total_elapsed = time.time() - scan_start
        logging.info(f"✅ [SCANNER API] Scan completed in {total_elapsed:.2f}s")
        logging.info(f"✅ [SCANNER API] Returning {len(results)} stocks to frontend")
        
        api_status = {
            'activeSource': 'Interactive Brokers (Real-time Screening)' if ibkr_connected else 'Not Connected',
            'ibkrConnected': ibkr_connected,
            'ibkrHost': IBKR_HOST,
            'ibkrPort': IBKR_PORT,
            'ibkrUsername': IBKR_USERNAME,
            'fallbackAvailable': False,  # No fallbacks - IBKR only
            'recommendedInterval': get_scanner_delay(),  # Auto-adjusted based on errors (starts at 12s, increases by 1s on errors)
            'currentDelay': get_scanner_delay(),
            'autoAdjusted': True,
            'mode': 'IBKR_REALTIME_SCREENING',  # Option 2: Real-time screening (default)
            'scanSpeed': '10-20 stocks per minute',
            'method': 'reqMktData (real-time quotes)'
        }
        
        logging.info(f"✅ [SCANNER API] IBKR Status: connected={ibkr_connected}, port={IBKR_PORT}")
        logging.info(f"✅ [SCANNER API] ===== SCAN REQUEST SUCCESS =====")
        
        return jsonify({
            'success': True,
            'stocks': results,
            'timestamp': datetime.now().isoformat(),
            'apiStatus': api_status
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        total_elapsed = time.time() - scan_start
        logging.error(f"❌ [SCANNER API] ===== SCAN REQUEST ERROR =====")
        logging.error(f"❌ [SCANNER API] Error after {total_elapsed:.2f}s: {error_msg}")
        logging.error(f"❌ [SCANNER API] Full traceback:\n{traceback.format_exc()}")
        
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
    import time
    request_start = time.time()
    logging.info(f"🔍 [SEARCH API] ===== NEW SEARCH REQUEST =====")
    logging.info(f"🔍 [SEARCH API] Received request for symbol: {symbol}")
    
    try:
        timeframe = request.args.get('timeframe', '5m')
        include_yesterday = request.args.get('includeYesterday', 'true').lower() == 'true'
        market_open = is_market_open()
        
        logging.info(f"🔍 [SEARCH API] Request params: timeframe={timeframe}, market_open={market_open}")
        
        # ONLY use Interactive Brokers - no fallbacks
        if not market_open:
            logging.info(f"📊 Market is CLOSED - Fetching historical data for {symbol} {timeframe} (including yesterday: {include_yesterday})")
        else:
            logging.info(f"📊 Fetching {timeframe} chart data for {symbol} from Interactive Brokers ONLY (Market OPEN, including yesterday: {include_yesterday})")
        
        # Check IBKR connection first
        logging.info(f"🔍 [SEARCH API] Checking IBKR connection for {symbol}...")
        logging.info(f"🔍 [SEARCH API] IBKR_AVAILABLE: {IBKR_AVAILABLE}, IBKR_CONNECTED: {IBKR_CONNECTED}")
        
        if not IBKR_AVAILABLE:
            logging.error(f"❌ [SEARCH API] IBKR not available - cannot fetch {symbol}")
            return jsonify({
                'success': False,
                'error': f'Interactive Brokers API not available. Install ib-insync: pip install ib-insync',
                'help': f'1. Install ib-insync: pip install ib-insync\n2. Restart the backend',
                'marketStatus': 'CLOSED' if not market_open else 'UNKNOWN'
            }), 503
        
        if not connect_ibkr():
            logging.error(f"❌ [SEARCH API] IBKR not connected - cannot fetch {symbol}")
            return jsonify({
                'success': False,
                'error': f'Interactive Brokers is not connected. Make sure TWS/IB Gateway is running and logged in.',
                'help': f'1. Start TWS or IB Gateway\n2. Log in as {IBKR_USERNAME}\n3. Enable API: Configure > API > Settings\n4. Set port: {IBKR_PORT}',
                'marketStatus': 'CLOSED' if not market_open else 'UNKNOWN'
            }), 503
        
        logging.info(f"✅ [SEARCH API] IBKR is connected, fetching stock data for {symbol}...")
        import time
        fetch_start = time.time()
        
        # Add timeout protection for search (max 100 seconds to allow frontend 120s timeout)
        try:
            stock_data = scanner.get_stock_data(symbol, timeframe)
        except Exception as search_error:
            fetch_elapsed = time.time() - fetch_start
            logging.error(f"❌ [SEARCH API] get_stock_data failed after {fetch_elapsed:.2f}s: {search_error}")
            import traceback
            error_traceback = traceback.format_exc()
            logging.error(f"❌ [SEARCH API] Full traceback:\n{error_traceback}")
            # Return error response instead of raising (outer handler will catch if needed)
            return jsonify({
                'success': False,
                'error': f'Error fetching {symbol}: {str(search_error)}',
                'help': f'1. Check if {symbol} is a valid stock symbol\n2. Verify IBKR connection\n3. Try again in a moment',
                'marketStatus': 'UNKNOWN'
            }), 500
        
        fetch_elapsed = time.time() - fetch_start
        logging.info(f"⏱️ [SEARCH API] Stock data fetch took {fetch_elapsed:.2f} seconds for {symbol}")
        
        if stock_data:
            candle_count = len(stock_data.get('candles', []))
            market_status = stock_data.get('marketStatus', 'PREMARKET' if is_premarket() else ('OPEN' if market_open else 'CLOSED'))
            total_elapsed = time.time() - request_start
            logging.info(f"✅ [SEARCH API] Got {timeframe} data from IBKR for {symbol} ({candle_count} candles, Market: {market_status})")
            logging.info(f"✅ [SEARCH API] Total request time: {total_elapsed:.2f} seconds")
            logging.info(f"✅ [SEARCH API] Stock data keys: {list(stock_data.keys())}")
            stock_data['source'] = 'Interactive Brokers (Real Data)'
            stock_data['isRealData'] = True
            stock_data['marketStatus'] = market_status
            
            response_data = {
                'success': True,
                'stock': stock_data,
                'marketStatus': market_status
            }
            logging.info(f"✅ [SEARCH API] Returning success response for {symbol}")
            return jsonify(response_data)
        else:
            total_elapsed = time.time() - request_start
            logging.error(f"❌ [SEARCH API] No data available from IBKR for {symbol} {timeframe} (took {total_elapsed:.2f}s)")
            logging.error(f"❌ [SEARCH API] scanner.get_stock_data returned None")
            return jsonify({
                'success': False,
                'error': f'No data available for {symbol}. The symbol may not be tradeable through IBKR, or IBKR may not have market data for this symbol. Please verify the symbol is correct and try again.',
                'help': f'1. Verify {symbol} is a valid stock symbol\n2. Check if {symbol} is tradeable through IBKR\n3. Ensure IBKR has market data subscription for {symbol}',
                'marketStatus': 'CLOSED' if not market_open else 'UNKNOWN'
            }), 404
    except Exception as e:
        error_msg = str(e)
        total_elapsed = time.time() - request_start
        logging.error(f"❌ [SEARCH API] Error in get_stock endpoint for {symbol} after {total_elapsed:.2f}s: {error_msg}")
        import traceback
        logging.error(f"❌ [SEARCH API] Full traceback:\n{traceback.format_exc()}")
        
        # Check for specific error types
        if 'No security definition' in error_msg or 'Invalid symbol' in error_msg:
            logging.error(f"❌ [SEARCH API] Invalid symbol error for {symbol}")
            return jsonify({
                'success': False,
                'error': f'Symbol {symbol} not found or invalid. Please verify the symbol is correct.',
                'help': f'1. Check if {symbol} is a valid stock symbol\n2. Try searching for a different symbol'
            }), 404
        elif 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
            logging.error(f"❌ [SEARCH API] Timeout error for {symbol}")
            return jsonify({
                'success': False,
                'error': f'Request timed out while fetching {symbol}. IBKR may be slow or the symbol may not be available. Please try again.',
                'help': f'1. Wait a moment and try again\n2. Check if IBKR is connected\n3. Verify {symbol} is a valid symbol'
            }), 504
        
        logging.error(f"❌ [SEARCH API] Generic error for {symbol}: {error_msg}")
        return jsonify({
            'success': False,
            'error': f'Error fetching {symbol}: {error_msg}'
        }), 500

@app.route('/api/stock/<symbol>/live', methods=['GET'])
def get_live_stock_data(symbol):
    """Get live/real-time data for a single stock (streaming updates)"""
    try:
        if not IBKR_AVAILABLE or not connect_ibkr():
            return jsonify({
                'success': False,
                'error': 'IBKR not connected'
            }), 503
        
        # Use real-time market data for live updates
        stock_data = fetch_realtime_ibkr(symbol)
        
        if stock_data:
            return jsonify({
                'success': True,
                'stock': stock_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No live data available for {symbol}'
            }), 404
            
    except Exception as e:
        logging.error(f"❌ [LIVE DATA] Error fetching live data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/<symbol>/max-position', methods=['GET'])
def get_max_position_size(symbol):
    """Calculate max position size for a stock based on account balance"""
    try:
        if not IBKR_AVAILABLE or not connect_ibkr():
            return jsonify({
                'success': False,
                'error': 'IBKR not connected'
            }), 503
        
        # Get account balance
        from ibkr_trading import get_account_balance
        account_balance = get_account_balance()
        
        if account_balance <= 0:
            return jsonify({
                'success': False,
                'error': 'Could not get account balance'
            }), 400
        
        # Get current stock price
        stock_data = fetch_realtime_ibkr(symbol)
        if not stock_data or not stock_data.get('currentPrice'):
            return jsonify({
                'success': False,
                'error': f'Could not get current price for {symbol}'
            }), 404
        
        current_price = stock_data['currentPrice']
        
        # Calculate max position size (use 50% of account balance for safety)
        max_position_value = account_balance * 0.5  # 50% of account
        max_shares = int(max_position_value / current_price) if current_price > 0 else 0
        max_position_value_actual = max_shares * current_price
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'accountBalance': account_balance,
            'currentPrice': current_price,
            'maxShares': max_shares,
            'maxPositionValue': max_position_value_actual,
            'maxPositionPercent': 50,  # 50% of account
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"❌ [MAX POSITION] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news/<symbol>', methods=['GET'])
def get_news(symbol):
    """Get news for a specific stock from IBKR (IBKR ONLY - no external news)"""
    # News is fetched directly from IBKR when scanning/fetching stock data
    # This endpoint returns empty since we don't cache news separately
    return jsonify({
        'success': True,
        'symbol': symbol.upper(),
        'news': [],
        'count': 0,
        'message': 'News is fetched directly from IBKR when scanning stocks',
        'source': 'IBKR ONLY',
        'timestamp': datetime.now().isoformat()
    })

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
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400
        
        # Add to active_symbols (the actual list used for scanning)
        with active_symbols_lock:
            if symbol not in active_symbols:
                active_symbols.add(symbol)
                logging.info(f"✅ [SYMBOLS] Added {symbol} to active_symbols (total: {len(active_symbols)})")
                return jsonify({
                    'success': True,
                    'message': f'Added {symbol} to scanner',
                    'symbol': symbol,
                    'totalSymbols': len(active_symbols)
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'{symbol} is already in scanner',
                    'symbol': symbol,
                    'totalSymbols': len(active_symbols)
                })
    except Exception as e:
        logging.error(f"Error adding symbol: {e}")
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
    """Preload stocks - ONLY from scanner results (AI does not scan independently)"""
    # AI learning ONLY uses stocks from scanner - redirect to daily-discovered
    logging.info(f"📊 Preload stocks requested - returning ONLY scanner-discovered stocks (AI does not scan independently)")
    
    with daily_discovered_lock:
        today = datetime.now().date()
        
        if daily_discovered_date != today or not daily_discovered_stocks:
            return jsonify({
                'success': True,
                'stocks': [],
                'count': 0,
                'source': 'Scanner Results Only',
                'marketStatus': 'PREMARKET' if is_premarket() else ('OPEN' if is_market_open() else 'CLOSED'),
                'note': 'No stocks discovered by scanner yet. Run a scan first. AI only learns from scanner picks.',
                'message': 'AI learning only uses stocks discovered by scanner - no independent scanning'
            })
        
        logging.info(f"✅ Returning {len(daily_discovered_stocks)} stocks from scanner results (AI only learns from scanner picks)")
        
        return jsonify({
            'success': True,
            'stocks': daily_discovered_stocks,
            'count': len(daily_discovered_stocks),
            'source': 'Scanner Results Only',
            'marketStatus': 'PREMARKET' if is_premarket() else ('OPEN' if is_market_open() else 'CLOSED'),
            'note': 'AI learning only uses stocks discovered by scanner - no independent scanning',
            'date': daily_discovered_date.isoformat()
        })

# In-memory log storage for connection log (last 200 entries)
connection_logs = []
connection_logs_lock = threading.Lock()
MAX_LOG_ENTRIES = 200

class ConnectionLogHandler(logging.Handler):
    """Custom logging handler to capture logs for connection log display"""
    def emit(self, record):
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'message': self.format(record),
                'module': record.module,
                'funcName': record.funcName,
                'lineno': record.lineno
            }
            with connection_logs_lock:
                connection_logs.append(log_entry)
                # Keep only last MAX_LOG_ENTRIES
                if len(connection_logs) > MAX_LOG_ENTRIES:
                    connection_logs.pop(0)
        except Exception:
            pass  # Don't break logging if handler fails

# Add custom handler to root logger (after basicConfig)
log_handler = ConnectionLogHandler()
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(message)s')
log_handler.setFormatter(log_formatter)
# Get root logger and add handler
root_logger = logging.getLogger()
root_logger.addHandler(log_handler)

# Keepalive thread to maintain IBKR connection
def keepalive_ibkr():
    """Periodically check and maintain IBKR connection"""
    while True:
        try:
            time.sleep(30)  # Check every 30 seconds
            if IBKR_AVAILABLE:
                with IBKR_LOCK:
                    if IBKR_INSTANCE:
                        try:
                            if not IBKR_INSTANCE.isConnected():
                                # Connection lost, try to reconnect
                                logging.warning("⚠️ [IBKR KEEPALIVE] Connection lost, attempting reconnect...")
                                global IBKR_CONNECTED
                                IBKR_CONNECTED = False
                                connect_ibkr()
                        except Exception as e:
                            logging.warning(f"⚠️ [IBKR KEEPALIVE] Error checking connection: {e}")
                            IBKR_CONNECTED = False
        except Exception as e:
            logging.error(f"❌ [IBKR KEEPALIVE] Error: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed connection info"""
    try:
        # Verify connection is still alive (with proper error handling)
        ibkr_connected = False
        connection_error = None
        
        if IBKR_AVAILABLE:
            if IBKR_INSTANCE:
                try:
                    # Safely check connection status (non-blocking - just check, don't reconnect)
                    is_connected = IBKR_INSTANCE.isConnected()
                    if is_connected:
                        ibkr_connected = True
                        IBKR_CONNECTED = True
                    else:
                        # Connection lost - just report it, don't try to reconnect (that blocks)
                        IBKR_CONNECTED = False
                        connection_error = "IBKR instance exists but not connected. Check TWS/IB Gateway is running and API is enabled."
                except Exception as e:
                    logging.warning(f"⚠️ [HEALTH] Error checking IBKR connection: {e}")
                    IBKR_CONNECTED = False
                    connection_error = f"Error checking connection: {str(e)}"
            else:
                connection_error = "IBKR instance not initialized. Check ib_insync is installed and TWS/IB Gateway is running."
        else:
            connection_error = "IBKR not available (ib_insync not installed)"
        
        # Get connection error details if disconnected
        if IBKR_AVAILABLE and not ibkr_connected and not connection_error:
            try:
                if IBKR_INSTANCE:
                    connection_error = "IBKR instance exists but not connected. Check TWS/IB Gateway is running and API is enabled."
                else:
                    connection_error = "IBKR instance not initialized. Check ib_insync is installed and TWS/IB Gateway is running."
            except Exception as e:
                connection_error = f"Error checking connection: {str(e)}"
    
        return jsonify({
            'status': 'healthy',
            'ibkrAvailable': IBKR_AVAILABLE,
            'ibkrConnected': ibkr_connected,
            'ibkrHost': IBKR_HOST,
            'ibkrPort': IBKR_PORT,
            'ibkrUsername': IBKR_USERNAME,
            'connectionError': connection_error,
            'marketDataSubscriptions': MARKET_DATA_SUBSCRIPTIONS,
            'level2Available': MARKET_DATA_SUBSCRIPTIONS['level2']['enabled'],
            'bookmapReady': MARKET_DATA_SUBSCRIPTIONS['level2']['bookmap_compatible'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        # Catch any unexpected errors in health check
        logging.error(f"❌ [HEALTH] Health check error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'error': str(e),
            'ibkrAvailable': IBKR_AVAILABLE,
            'ibkrConnected': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent connection logs for display in connection log panel"""
    try:
        with connection_logs_lock:
            # Filter for relevant logs (IBKR, Scanner, API, Connection)
            # Exclude routine polling requests (GET /api/health, GET /api/logs)
            relevant_logs = []
            for log in connection_logs[-100:]:  # Last 100 entries
                message = log.get('message', '').lower()
                
                # Skip routine HTTP polling requests (they clutter the logs)
                # Check both the message and the formatted record message
                if '"GET /api/health' in message or '"GET /api/logs' in message or 'GET /api/health' in message or 'GET /api/logs' in message:
                    continue
                
                # Include logs with relevant keywords
                if any(keyword in message for keyword in ['ibkr', 'scanner', 'connection', 'connect', 'error', 'failed', 'api', 'scan', 'stock', 'ollama', 'warning', 'success']):
                    relevant_logs.append(log)
            
            return jsonify({
                'success': True,
                'logs': relevant_logs[-50:],  # Return last 50 relevant logs
                'count': len(relevant_logs)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'logs': []
        }), 500

@app.route('/api/logs', methods=['DELETE'])
def clear_logs():
    """Clear all connection logs"""
    try:
        with connection_logs_lock:
            connection_logs.clear()
            logging.info("🗑️ [LOGS] Connection logs cleared by user")
        return jsonify({
            'success': True,
            'message': 'Logs cleared successfully'
        })
    except Exception as e:
        logging.error(f"Error clearing logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== OLLAMA AI ENDPOINTS ====================

@app.route('/api/ollama/status', methods=['GET'])
def ollama_status():
    """Check Ollama connection and available models"""
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'available': False,
            'error': 'Ollama service not available'
        }), 503
    
    try:
        status = check_ollama_connection()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/analyze', methods=['POST'])
def ollama_analyze():
    """Analyze candlestick patterns using Ollama AI"""
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Ollama service not available'
        }), 503
    
    try:
        data = request.json
        symbol = data.get('symbol', '')
        candles = data.get('candles', [])
        current_price = data.get('currentPrice', 0)
        volume = data.get('volume', 0)
        avg_volume = data.get('avgVolume', 0)
        detected_patterns = data.get('detectedPatterns', None)  # Optional: patterns detected by frontend
        
        if not candles:
            return jsonify({
                'success': False,
                'error': 'No candle data provided'
            }), 400
        
        # Fetch Level 2 data if available (REAL order book data)
        level2_data = None
        try:
            from fetch_level2_data import fetch_level2_order_book
            level2_data = fetch_level2_order_book(symbol, num_levels=10)
            if level2_data:
                level2_data['timestamp'] = datetime.now().isoformat()
                logging.info(f"📊 [OLLAMA] Fetched REAL Level 2 data for {symbol}: {level2_data.get('totalBidSize', 0):,} bids, {level2_data.get('totalAskSize', 0):,} asks")
        except Exception as e:
            logging.debug(f"⚠️ [OLLAMA] Could not fetch Level 2 data for {symbol}: {e}")
        
        # Get float data if available in request
        stock_float = data.get('float', None)
        
        result = analyze_candlesticks_with_ollama(
            candles=candles,
            symbol=symbol,
            current_price=current_price,
            volume=volume,
            avg_volume=avg_volume,
            detected_patterns=detected_patterns,
            level2_data=level2_data,  # Pass REAL Level 2 data
            stock_float=stock_float  # Pass float data if available
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ [OLLAMA] Analysis endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/teach', methods=['POST'])
def ollama_teach():
    """Teach Ollama a new candlestick pattern"""
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Ollama service not available'
        }), 503
    
    try:
        data = request.json
        pattern_name = data.get('patternName', '')
        description = data.get('description', '')
        examples = data.get('examples', [])
        
        if not pattern_name or not description:
            return jsonify({
                'success': False,
                'error': 'Pattern name and description required'
            }), 400
        
        result = teach_ollama_pattern(
            pattern_name=pattern_name,
            description=description,
            examples=examples
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ [OLLAMA] Teaching endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/teach-all', methods=['POST'])
def ollama_teach_all():
    """Teach Ollama ALL candlestick patterns from the codebase"""
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Ollama service not available'
        }), 503
    
    if teach_all_patterns_to_ollama is None:
        return jsonify({
            'success': False,
            'error': 'Pattern teaching module not available'
        }), 503
    
    try:
        logging.info("📚 [OLLAMA] Starting comprehensive pattern teaching...")
        result = teach_all_patterns_to_ollama()
        
        if result.get('success'):
            logging.info(f"✅ [OLLAMA] Teaching complete: {result.get('message')}")
        else:
            logging.error(f"❌ [OLLAMA] Teaching failed: {result.get('error')}")
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ [OLLAMA] Teaching all patterns error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/teach-ibkr', methods=['POST'])
def ollama_teach_ibkr():
    """Teach Ollama about IBKR trading capabilities"""
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Ollama service not available'
        }), 503
    
    try:
        from ollama_ibkr_trading import teach_ibkr_trading_to_ollama
        logging.info("📚 [OLLAMA IBKR] Starting IBKR trading knowledge teaching...")
        result = teach_ibkr_trading_to_ollama()
        
        if result.get('success'):
            logging.info(f"✅ [OLLAMA IBKR] Teaching complete: {result.get('message')}")
        else:
            logging.error(f"❌ [OLLAMA IBKR] Teaching failed: {result.get('error')}")
        
        return jsonify(result)
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'IBKR trading teaching module not available'
        }), 503
    except Exception as e:
        logging.error(f"❌ [OLLAMA IBKR] Teaching error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/teach-level2', methods=['POST'])
def ollama_teach_level2():
    """Teach Ollama about Level 2 market data and order flow analysis"""
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Ollama service not available'
        }), 503
    
    try:
        from ollama_level2_teaching import teach_level2_to_ollama
        logging.info("📚 [OLLAMA LEVEL2] Starting Level 2 market data knowledge teaching...")
        result = teach_level2_to_ollama()
        
        if result.get('success'):
            logging.info(f"✅ [OLLAMA LEVEL2] Teaching complete: {result.get('message')}")
        else:
            logging.error(f"❌ [OLLAMA LEVEL2] Teaching failed: {result.get('error')}")
        
        return jsonify(result)
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Level 2 teaching module not available'
        }), 503
    except Exception as e:
        logging.error(f"❌ [OLLAMA LEVEL2] Teaching error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/trade-decision', methods=['POST'])
def ollama_trade_decision():
    """
    Get AI trading decision (BUY/SELL/HOLD) for a stock
    This endpoint will be used when buy/sell functionality is implemented
    """
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Ollama service not available'
        }), 503
    
    try:
        data = request.json
        symbol = data.get('symbol', '')
        candles = data.get('candles', [])
        current_price = data.get('currentPrice', 0)
        volume = data.get('volume', 0)
        avg_volume = data.get('avgVolume', 0)
        account_balance = data.get('accountBalance', 0)  # For future use
        risk_tolerance = data.get('riskTolerance', 'MEDIUM')  # LOW, MEDIUM, HIGH
        
        if not candles:
            return jsonify({
                'success': False,
                'error': 'No candle data provided'
            }), 400
        
        # Get detected patterns if provided
        detected_patterns = data.get('detectedPatterns', None)
        
        # Fetch Level 2 data if available (REAL order book data)
        level2_data = None
        try:
            from fetch_level2_data import fetch_level2_order_book
            level2_data = fetch_level2_order_book(symbol, num_levels=10)
            if level2_data:
                level2_data['timestamp'] = datetime.now().isoformat()
                logging.info(f"📊 [AUTO-TRADE] Fetched REAL Level 2 data for {symbol}: {level2_data.get('totalBidSize', 0):,} bids, {level2_data.get('totalAskSize', 0):,} asks")
        except Exception as e:
            logging.debug(f"⚠️ [AUTO-TRADE] Could not fetch Level 2 data for {symbol}: {e}")
        
        # Get float data if available
        stock_float = data.get('float', None)
        
        # Analyze with Ollama (using REAL data)
        analysis_result = analyze_candlesticks_with_ollama(
            candles=candles,
            symbol=symbol,
            current_price=current_price,
            volume=volume,
            avg_volume=avg_volume,
            detected_patterns=detected_patterns,
            level2_data=level2_data,  # Pass REAL Level 2 data
            stock_float=stock_float  # Pass float data if available
        )
        
        if not analysis_result.get('success'):
            return jsonify(analysis_result), 500
        
        analysis = analysis_result.get('analysis', {})
        signal = analysis.get('signal', 'HOLD')
        
        # Build trading decision (framework for future buy/sell implementation)
        decision = {
            'symbol': symbol,
            'action': signal,  # BUY, SELL, or HOLD
            'confidence': analysis.get('confidence', 'LOW'),
            'reasoning': analysis.get('reasoning', ''),
            'entryPrice': analysis.get('entryPrice'),
            'stopLoss': analysis.get('stopLoss'),
            'takeProfit': analysis.get('takeProfit'),
            'pattern': analysis.get('pattern'),
            'timestamp': datetime.now().isoformat(),
            'readyToExecute': False  # Will be True when buy/sell is implemented
        }
        
        # For now, we only return the decision
        # When buy/sell is implemented, this will trigger actual trades
        if signal == 'BUY' and analysis.get('confidence') == 'HIGH':
            decision['readyToExecute'] = True
            decision['recommendedQuantity'] = calculate_position_size(
                account_balance=account_balance,
                entry_price=analysis.get('entryPrice') or current_price,
                risk_tolerance=risk_tolerance
            )
        
        return jsonify({
            'success': True,
            'decision': decision
        })
    except Exception as e:
        logging.error(f"❌ [OLLAMA] Trade decision error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/chat', methods=['POST'])
def ollama_chat():
    """Chat with Ollama - send messages and get responses"""
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Ollama service not available'
        }), 503
    
    try:
        data = request.json
        message = data.get('message', '').strip()
        model = data.get('model', 'llama3.2')  # Default model
        context = data.get('context', '')  # Optional context about stocks/scanner
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Import ollama client
        import requests as req
        
        OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # Build prompt with context if provided
        prompt = message
        if context:
            prompt = f"Context: {context}\n\nUser: {message}\n\nAssistant:"
        
        # Call Ollama API
        response = req.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                'model': model,
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Ollama API error: {response.status_code}'
            }), 500
        
        result = response.json()
        reply = result.get('response', 'No response from Ollama')
        
        logging.info(f"✅ [OLLAMA CHAT] User: {message[:50]}... | Response: {reply[:50]}...")
        
        return jsonify({
            'success': True,
            'message': reply,
            'model': model
        })
        
    except Exception as e:
        logging.error(f"❌ [OLLAMA CHAT] Error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/execute-trade', methods=['POST'])
def ollama_execute_trade():
    """
    Ollama analyzes and automatically executes trades through IBKR
    This allows Ollama to directly talk to IBKR and execute trades
    """
    if not OLLAMA_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Ollama service not available'
        }), 503
    
    if not TRADING_AVAILABLE or not IBKR_CONNECTED:
        return jsonify({
            'success': False,
            'error': 'IBKR not connected',
            'message': 'Please connect to Interactive Brokers first'
        }), 503
    
    try:
        data = request.json
        symbol = data.get('symbol', '')
        candles = data.get('candles', [])
        current_price = data.get('currentPrice', 0)
        volume = data.get('volume', 0)
        avg_volume = data.get('avgVolume', 0)
        account_balance = data.get('accountBalance', 10000)  # Default $10k if not provided
        risk_tolerance = data.get('riskTolerance', 'MEDIUM')
        auto_execute = data.get('autoExecute', False)  # Safety flag - must be explicitly True
        
        if not candles:
            return jsonify({
                'success': False,
                'error': 'No candle data provided'
            }), 400
        
        # Get detected patterns if provided
        detected_patterns = data.get('detectedPatterns', None)
        
        # Analyze with Ollama
        logging.info(f"🤖 [OLLAMA IBKR] Analyzing {symbol} for trade execution...")
        # Fetch Level 2 data if available (REAL order book data)
        level2_data = None
        try:
            from fetch_level2_data import fetch_level2_order_book
            level2_data = fetch_level2_order_book(symbol, num_levels=10)
            if level2_data:
                level2_data['timestamp'] = datetime.now().isoformat()
                logging.info(f"📊 [TRADE] Fetched REAL Level 2 data for {symbol}: {level2_data.get('totalBidSize', 0):,} bids, {level2_data.get('totalAskSize', 0):,} asks")
        except Exception as e:
            logging.debug(f"⚠️ [TRADE] Could not fetch Level 2 data for {symbol}: {e}")
        
        # Get float data if available
        stock_float = data.get('float', None)
        
        analysis_result = analyze_candlesticks_with_ollama(
            candles=candles,
            symbol=symbol,
            current_price=current_price,
            volume=volume,
            avg_volume=avg_volume,
            detected_patterns=detected_patterns,
            level2_data=level2_data,  # Pass REAL Level 2 data
            stock_float=stock_float  # Pass float data if available
        )
        
        if not analysis_result.get('success'):
            return jsonify(analysis_result), 500
        
        analysis = analysis_result.get('analysis', {})
        signal = analysis.get('signal', 'HOLD')
        confidence = analysis.get('confidence', 'LOW')
        
        # Only execute if signal is BUY/SELL and confidence is HIGH
        if signal == 'HOLD' or confidence != 'HIGH':
            return jsonify({
                'success': True,
                'decision': {
                    'symbol': symbol,
                    'action': signal,
                    'confidence': confidence,
                    'reasoning': analysis.get('reasoning', ''),
                    'executed': False,
                    'message': f'Not executing: {signal} signal with {confidence} confidence (requires HIGH confidence)'
                }
            })
        
        # OLLAMA TRADING CONSTRAINTS
        # 1. Price range filter: Only trade stocks between $1-$6
        entry_price = analysis.get('entryPrice') or current_price
        if entry_price < 1.0 or entry_price > 6.0:
            return jsonify({
                'success': True,
                'decision': {
                    'symbol': symbol,
                    'action': signal,
                    'confidence': confidence,
                    'reasoning': analysis.get('reasoning', ''),
                    'executed': False,
                    'message': f'Price ${entry_price:.2f} outside allowed range ($1.00-$6.00). Ollama only trades stocks between $1-$6.'
                }
            })
        
        # Also check current_price as backup
        if current_price < 1.0 or current_price > 6.0:
            return jsonify({
                'success': True,
                'decision': {
                    'symbol': symbol,
                    'action': signal,
                    'confidence': confidence,
                    'reasoning': analysis.get('reasoning', ''),
                    'executed': False,
                    'message': f'Current price ${current_price:.2f} outside allowed range ($1.00-$6.00). Ollama only trades stocks between $1-$6.'
                }
            })
        
        # Get entry price for all checks
        entry_price = analysis.get('entryPrice') or current_price
        
        # 2. Check daily trade limits
        today = get_today_date()
        can_trade, limit_message = check_daily_trade_limit(today, signal)
        
        if not can_trade:
            return jsonify({
                'success': True,
                'decision': {
                    'symbol': symbol,
                    'action': signal,
                    'confidence': confidence,
                    'reasoning': analysis.get('reasoning', ''),
                    'executed': False,
                    'message': limit_message
                }
            })
        
        # 3. Check if date is enabled for trading (from request)
        enabled_days = data.get('enabledDays', {})
        if today not in enabled_days or not enabled_days[today]:
            return jsonify({
                'success': True,
                'decision': {
                    'symbol': symbol,
                    'action': signal,
                    'confidence': confidence,
                    'reasoning': analysis.get('reasoning', ''),
                    'executed': False,
                    'message': f'Trading not enabled for {today}. Please enable this day in the calendar.'
                }
            })
        
        # 4. Check daily budget
        daily_budget = data.get('dailyTradeBudget', 0)
        if daily_budget <= 0:
            return jsonify({
                'success': True,
                'decision': {
                    'symbol': symbol,
                    'action': signal,
                    'confidence': confidence,
                    'reasoning': analysis.get('reasoning', ''),
                    'executed': False,
                    'message': 'Daily trade budget not set. Please set a budget in the calendar.'
                }
            })
        
        # 5. Check end-of-day cutoff (3:30 PM ET - no new positions)
        now = datetime.now()
        try:
            import pytz
            et = pytz.timezone('US/Eastern')
            now_et = datetime.now(et)
        except ImportError:
            now_et = now
        
        cutoff_time = now_et.replace(hour=15, minute=30, second=0, microsecond=0)  # 3:30 PM ET
        
        if now_et >= cutoff_time:
            return jsonify({
                'success': True,
                'decision': {
                    'symbol': symbol,
                    'action': signal,
                    'confidence': confidence,
                    'reasoning': analysis.get('reasoning', ''),
                    'executed': False,
                    'message': f'Too close to market close (3:30 PM cutoff). Ollama does not open new positions after 3:30 PM ET to ensure positions can close before end of day (4:00 PM).'
                }
            })
        
        # 6. Use full $4,000 per stock (Ollama uses all $4k for each stock it buys)
        MAX_POSITION_VALUE = 4000.0
        
        # Calculate quantity to use full $4,000
        quantity = int(MAX_POSITION_VALUE / entry_price) if entry_price > 0 else 0
        
        # Ensure minimum 1 share
        if quantity < 1:
            return jsonify({
                'success': True,
                'decision': {
                    'symbol': symbol,
                    'action': signal,
                    'confidence': confidence,
                    'reasoning': analysis.get('reasoning', ''),
                    'executed': False,
                    'message': f'Position size too small. Entry price ${entry_price:.2f} with $4,000 budget results in less than 1 share.'
                }
            })
        
        # Calculate actual position value (should be close to $4k)
        position_value = quantity * entry_price
        
        # Log the position size
        logging.info(f"💰 [OLLAMA] Using full $4,000 allocation: {quantity} shares @ ${entry_price:.2f} = ${position_value:.2f}")
        
        # Get stop loss, take profit, and trailing stop from Ollama analysis
        stop_loss = analysis.get('stopLoss')
        take_profit = analysis.get('takeProfit')
        trailing_stop_percent = analysis.get('trailingStopPercent')
        stop_loss_percent = None
        take_profit_percent = None
        
        if stop_loss and entry_price:
            if signal == 'BUY':
                stop_loss_percent = abs((entry_price - stop_loss) / entry_price * 100)
            else:  # SELL
                stop_loss_percent = abs((stop_loss - entry_price) / entry_price * 100)
        
        if take_profit and entry_price:
            if signal == 'BUY':
                take_profit_percent = abs((take_profit - entry_price) / entry_price * 100)
            else:  # SELL
                take_profit_percent = abs((entry_price - take_profit) / entry_price * 100)
        
        # If Ollama didn't specify trailing stop, use a default based on volatility
        if not trailing_stop_percent and stop_loss_percent:
            # Default trailing stop: 1.5x the initial stop loss distance
            trailing_stop_percent = stop_loss_percent * 1.5
        
        # Execute trade if auto_execute is True
        execution_result = None
        if auto_execute:
            # Import trading functions
            from ibkr_trading import place_market_order, place_limit_order
            
            logging.info(f"🚀 [OLLAMA IBKR] Executing {signal} order for {symbol}...")
            
            if signal == 'BUY':
                # Execute BUY order
                if analysis.get('entryPrice') and analysis.get('entryPrice') != current_price:
                    # Use limit order if entry price differs from current
                    execution_result = place_limit_order(
                        symbol=symbol,
                        action='BUY',
                        quantity=quantity,
                        limit_price=entry_price,
                        stop_loss_percent=stop_loss_percent,
                        take_profit_percent=take_profit_percent,
                        trailing_stop_percent=trailing_stop_percent
                    )
                else:
                    # Use market order
                    execution_result = place_market_order(
                        symbol=symbol,
                        action='BUY',
                        quantity=quantity,
                        stop_loss_percent=stop_loss_percent,
                        take_profit_percent=take_profit_percent,
                        trailing_stop_percent=trailing_stop_percent
                    )
            else:  # SELL
                # Execute SELL order
                if analysis.get('entryPrice') and analysis.get('entryPrice') != current_price:
                    # Use limit order if entry price differs from current
                    execution_result = place_limit_order(
                        symbol=symbol,
                        action='SELL',
                        quantity=quantity,
                        limit_price=entry_price,
                        stop_loss_percent=stop_loss_percent,
                        take_profit_percent=take_profit_percent,
                        trailing_stop_percent=trailing_stop_percent
                    )
                else:
                    # Use market order
                    execution_result = place_market_order(
                        symbol=symbol,
                        action='SELL',
                        quantity=quantity,
                        stop_loss_percent=stop_loss_percent,
                        take_profit_percent=take_profit_percent,
                        trailing_stop_percent=trailing_stop_percent
                    )
            
            if execution_result and execution_result.get('success'):
                # Mark trade as used for today
                mark_daily_trade_used(today, signal)
                logging.info(f"✅ [OLLAMA IBKR] Trade executed successfully: {symbol} {signal} x{quantity}")
            else:
                logging.error(f"❌ [OLLAMA IBKR] Trade execution failed: {execution_result.get('error') if execution_result else 'Unknown error'}")
        else:
            logging.info(f"⚠️ [OLLAMA IBKR] Trade ready but autoExecute=False (safety check)")
        
        return jsonify({
            'success': True,
            'decision': {
                'symbol': symbol,
                'action': signal,
                'confidence': confidence,
                'reasoning': analysis.get('reasoning', ''),
                'pattern': analysis.get('pattern'),
                'entryPrice': entry_price,
                'stopLoss': stop_loss,
                'takeProfit': take_profit,
                'quantity': quantity,
                'executed': auto_execute and execution_result and execution_result.get('success'),
                'executionResult': execution_result if auto_execute else None,
                'message': 'Trade executed' if (auto_execute and execution_result and execution_result.get('success')) else 'Trade ready (set autoExecute=true to execute)'
            }
        })
    except Exception as e:
        logging.error(f"❌ [OLLAMA IBKR] Execute trade error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Daily trade tracking (1 buy, 1 sell per day)
DAILY_TRADES: Dict[str, Dict[str, bool]] = {}  # {date: {'buyUsed': bool, 'sellUsed': bool}}
DAILY_TRADES_LOCK = threading.Lock()

def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')

def check_daily_trade_limit(date: str, action: str) -> tuple[bool, str]:
    """
    Check if daily trade limit is reached for a given date and action
    
    Returns:
        (can_trade, message)
    """
    with DAILY_TRADES_LOCK:
        # Clean up old dates (older than 7 days)
        today = datetime.now()
        dates_to_remove = []
        for stored_date in DAILY_TRADES.keys():
            try:
                stored_dt = datetime.strptime(stored_date, '%Y-%m-%d')
                if (today - stored_dt).days > 7:
                    dates_to_remove.append(stored_date)
            except:
                dates_to_remove.append(stored_date)
        
        for date_to_remove in dates_to_remove:
            del DAILY_TRADES[date_to_remove]
        
        # Check current date
        if date not in DAILY_TRADES:
            DAILY_TRADES[date] = {'buyUsed': False, 'sellUsed': False}
        
        trades = DAILY_TRADES[date]
        
        if action == 'BUY':
            if trades['buyUsed']:
                return False, f"Daily buy limit reached for {date}. Only 1 buy allowed per day."
            return True, "Buy available"
        elif action == 'SELL':
            if trades['sellUsed']:
                return False, f"Daily sell limit reached for {date}. Only 1 sell allowed per day."
            return True, "Sell available"
        else:
            return False, f"Invalid action: {action}"

def mark_daily_trade_used(date: str, action: str):
    """Mark a trade as used for a given date"""
    with DAILY_TRADES_LOCK:
        if date not in DAILY_TRADES:
            DAILY_TRADES[date] = {'buyUsed': False, 'sellUsed': False}
        
        if action == 'BUY':
            DAILY_TRADES[date]['buyUsed'] = True
        elif action == 'SELL':
            DAILY_TRADES[date]['sellUsed'] = True

def get_daily_trades_status(date: str) -> Dict[str, bool]:
    """Get daily trade status for a given date"""
    with DAILY_TRADES_LOCK:
        if date not in DAILY_TRADES:
            return {'buyUsed': False, 'sellUsed': False}
        return DAILY_TRADES[date].copy()

def close_all_positions_before_market_close():
    """Close all open positions before market close (3:50 PM ET)"""
    from ibkr_trading import get_open_positions, place_market_order
    from ib_insync import Stock
    
    if not IBKR_AVAILABLE or not IBKR_CONNECTED or not IBKR_INSTANCE:
        return
    
    try:
        positions_result = get_open_positions()
        if not positions_result.get('success'):
            return
        
        positions = positions_result.get('positions', [])
        if not positions:
            return
        
        # Close each position
        for pos in positions:
            symbol = pos.get('symbol')
            quantity = abs(int(pos.get('position', 0)))
            
            if quantity == 0:
                continue
            
            # Determine action (if position is positive, we need to sell)
            action = 'SELL' if pos.get('position', 0) > 0 else 'BUY'
            
            try:
                logging.info(f"🔚 [EOD CLOSE] Closing position: {symbol} {quantity} shares ({action})")
                result = place_market_order(
                    symbol=symbol,
                    action=action,
                    quantity=quantity,
                    stop_loss_percent=None,  # No stop loss on closing orders
                    take_profit_percent=None  # No take profit on closing orders
                )
                
                if result.get('success'):
                    logging.info(f"✅ [EOD CLOSE] Successfully closed {symbol} position")
                else:
                    logging.error(f"❌ [EOD CLOSE] Failed to close {symbol}: {result.get('error')}")
            except Exception as e:
                logging.error(f"❌ [EOD CLOSE] Error closing {symbol}: {e}")
                
    except Exception as e:
        logging.error(f"❌ [EOD CLOSE] Error closing positions: {e}")

def monitor_trailing_stops():
    """Background thread to monitor and update trailing stops, and close positions before market close"""
    from ibkr_trading import update_trailing_stop, ACTIVE_TRADES, TRADING_LOCK
    from ib_insync import Stock
    
    last_eod_check = None
    
    while True:
        try:
            time.sleep(10)  # Check every 10 seconds
            
            if not IBKR_AVAILABLE or not IBKR_CONNECTED or not IBKR_INSTANCE:
                continue
            
            # Check if we need to close positions before market close (3:50 PM ET)
            now = datetime.now()
            market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)  # 4:00 PM ET
            eod_close_time = now.replace(hour=15, minute=50, second=0, microsecond=0)  # 3:50 PM ET
            
            # Check if it's time to close (3:50 PM) and we haven't checked today
            if now >= eod_close_time and now < market_close_time:
                if last_eod_check is None or last_eod_check.date() != now.date():
                    logging.info("🔚 [EOD CLOSE] Market closing soon - closing all positions...")
                    close_all_positions_before_market_close()
                    last_eod_check = now
            
            # Get current positions and update trailing stops
            with TRADING_LOCK:
                active_order_ids = list(ACTIVE_TRADES.keys())
            
            for order_id in active_order_ids:
                try:
                    with TRADING_LOCK:
                        trade_info = ACTIVE_TRADES.get(order_id)
                    if not trade_info:
                        continue
                    
                    symbol = trade_info.get('symbol')
                    if not symbol:
                        continue
                    
                    # Get current market price
                    with IBKR_LOCK:
                        contract = Stock(symbol, 'SMART', 'USD')
                        IBKR_INSTANCE.reqMktData(contract, '', False, False)
                        ticker = IBKR_INSTANCE.ticker(contract)
                        IBKR_INSTANCE.sleep(0.5)
                        
                        current_price = ticker.marketPrice() or ticker.last or 0
                        if current_price == 0:
                            continue
                    
                    # Update trailing stop
                    update_result = update_trailing_stop(order_id, current_price)
                    if update_result:
                        logging.info(f"📈 [TRAILING STOP] Updated stop for {symbol}: ${update_result.get('new_stop_loss'):.2f} (profit locked: {update_result.get('profit_locked'):.2f}%)")
                        
                        # TODO: Update the actual stop loss order in IBKR
                        # This would require finding the stop loss order and modifying it
                        
                except Exception as e:
                    logging.warning(f"⚠️ [TRAILING STOP] Error monitoring order {order_id}: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"❌ [TRAILING STOP] Monitor error: {e}")
            time.sleep(30)  # Wait longer on error

@app.route('/api/trade/account-balance', methods=['GET'])
def get_account_balance_endpoint():
    """Get IBKR account balance"""
    if not TRADING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Trading service not available',
            'balance': 0
        }), 503
    
    if not IBKR_AVAILABLE or not IBKR_CONNECTED:
        return jsonify({
            'success': False,
            'error': 'IBKR not connected',
            'balance': 0
        }), 503
    
    try:
        from ibkr_trading import get_account_balance
        balance = get_account_balance()
        return jsonify({
            'success': True,
            'balance': balance
        })
    except Exception as e:
        logging.error(f"❌ [TRADE] Get account balance error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'balance': 0
        }), 500

@app.route('/api/trade/daily-status', methods=['GET'])
def get_daily_trade_status():
    """Get daily trade status for a date range"""
    try:
        date = request.args.get('date', get_today_date())
        status = get_daily_trades_status(date)
        return jsonify({
            'success': True,
            'date': date,
            'buyUsed': status['buyUsed'],
            'sellUsed': status['sellUsed']
        })
    except Exception as e:
        logging.error(f"❌ [TRADE] Get daily status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trade/daily-status-range', methods=['GET'])
def get_daily_trade_status_range():
    """Get daily trade status for next 5 days"""
    try:
        today = datetime.now()
        status_map = {}
        
        for i in range(5):
            date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
            status = get_daily_trades_status(date)
            status_map[date] = {
                'buyUsed': status['buyUsed'],
                'sellUsed': status['sellUsed']
            }
        
        return jsonify({
            'success': True,
            'status': status_map
        })
    except Exception as e:
        logging.error(f"❌ [TRADE] Get daily status range error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def calculate_position_size(account_balance: float, entry_price: float, risk_tolerance: str) -> int:
    """
    Calculate recommended position size based on risk tolerance
    This is a placeholder for future implementation
    """
    risk_percentages = {
        'LOW': 0.01,      # 1% of account
        'MEDIUM': 0.02,   # 2% of account
        'HIGH': 0.05      # 5% of account
    }
    
    risk_percent = risk_percentages.get(risk_tolerance, 0.02)
    risk_amount = account_balance * risk_percent
    
    if entry_price > 0:
        quantity = int(risk_amount / entry_price)
        return max(1, min(quantity, 1000))  # Cap at 1000 shares
    
    return 0

# ==================== IBKR TRADING ENDPOINTS ====================

@app.route('/api/trade/buy', methods=['POST'])
def trade_buy():
    """Place a BUY order with optional stop loss and take profit"""
    if not TRADING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Trading service not available'
        }), 503
    
    if not IBKR_AVAILABLE or not IBKR_CONNECTED:
        return jsonify({
            'success': False,
            'error': 'IBKR not connected',
            'message': 'Please connect to Interactive Brokers first'
        }), 503
    
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        quantity = int(data.get('quantity', 0))
        order_type = data.get('orderType', 'MARKET').upper()  # MARKET or LIMIT
        limit_price = data.get('limitPrice')
        stop_loss_percent = data.get('stopLossPercent')
        take_profit_percent = data.get('takeProfitPercent')
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400
        
        if quantity <= 0:
            return jsonify({
                'success': False,
                'error': 'Quantity must be greater than 0'
            }), 400
        
        if order_type == 'LIMIT' and not limit_price:
            return jsonify({
                'success': False,
                'error': 'Limit price is required for LIMIT orders'
            }), 400
        
        # Place order
        if order_type == 'MARKET':
            result = place_market_order(
                symbol=symbol,
                action='BUY',
                quantity=quantity,
                stop_loss_percent=stop_loss_percent,
                take_profit_percent=take_profit_percent
            )
        else:  # LIMIT
            result = place_limit_order(
                symbol=symbol,
                action='BUY',
                quantity=quantity,
                limit_price=limit_price,
                stop_loss_percent=stop_loss_percent,
                take_profit_percent=take_profit_percent
            )
        
        if result.get('success'):
            logging.info(f"✅ [TRADE] BUY order placed: {symbol} x{quantity}")
        else:
            logging.error(f"❌ [TRADE] BUY order failed: {result.get('error')}")
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ [TRADE] Buy order error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Error placing buy order: {str(e)}'
        }), 500

@app.route('/api/trade/sell', methods=['POST'])
def trade_sell():
    """Place a SELL order with optional stop loss and take profit"""
    if not TRADING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Trading service not available'
        }), 503
    
    if not IBKR_AVAILABLE or not IBKR_CONNECTED:
        return jsonify({
            'success': False,
            'error': 'IBKR not connected',
            'message': 'Please connect to Interactive Brokers first'
        }), 503
    
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        quantity = int(data.get('quantity', 0))
        order_type = data.get('orderType', 'MARKET').upper()
        limit_price = data.get('limitPrice')
        stop_loss_percent = data.get('stopLossPercent')
        take_profit_percent = data.get('takeProfitPercent')
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400
        
        if quantity <= 0:
            return jsonify({
                'success': False,
                'error': 'Quantity must be greater than 0'
            }), 400
        
        if order_type == 'LIMIT' and not limit_price:
            return jsonify({
                'success': False,
                'error': 'Limit price is required for LIMIT orders'
            }), 400
        
        # Place order
        if order_type == 'MARKET':
            result = place_market_order(
                symbol=symbol,
                action='SELL',
                quantity=quantity,
                stop_loss_percent=stop_loss_percent,
                take_profit_percent=take_profit_percent
            )
        else:  # LIMIT
            result = place_limit_order(
                symbol=symbol,
                action='SELL',
                quantity=quantity,
                limit_price=limit_price,
                stop_loss_percent=stop_loss_percent,
                take_profit_percent=take_profit_percent
            )
        
        if result.get('success'):
            logging.info(f"✅ [TRADE] SELL order placed: {symbol} x{quantity}")
        else:
            logging.error(f"❌ [TRADE] SELL order failed: {result.get('error')}")
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ [TRADE] Sell order error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Error placing sell order: {str(e)}'
        }), 500

@app.route('/api/trade/positions', methods=['GET'])
def get_positions():
    """Get all open positions"""
    if not TRADING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Trading service not available',
            'positions': []
        }), 503
    
    try:
        result = get_open_positions()
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ [TRADE] Get positions error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'positions': []
        }), 500

@app.route('/api/trade/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order status by order ID"""
    if not TRADING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Trading service not available'
        }), 503
    
    try:
        result = get_order_status(order_id)
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ [TRADE] Get order status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trade/cancel/<int:order_id>', methods=['POST'])
def cancel_trade_order(order_id):
    """Cancel an order by order ID"""
    if not TRADING_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Trading service not available'
        }), 503
    
    try:
        result = cancel_order(order_id)
        return jsonify(result)
    except Exception as e:
        logging.error(f"❌ [TRADE] Cancel order error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Start news scheduler in background thread
    # News: IBKR ONLY - no scheduled news fetching needed
    # News is fetched directly from IBKR when scanning stocks
    logging.info("News: IBKR ONLY mode - news fetched directly from IBKR when scanning")
    
    # Connect to IBKR on startup (in background thread to avoid blocking)
    def init_ibkr_connection():
        if IBKR_AVAILABLE:
            logging.info("🔌 [STARTUP] Attempting to connect to IBKR...")
            connect_ibkr()
            
            # Initialize trading service with IBKR instance
            if TRADING_AVAILABLE and IBKR_INSTANCE:
                try:
                    set_ibkr_instance(IBKR_INSTANCE, IBKR_LOCK)
                    logging.info("✅ [TRADING] Trading service initialized")
                except Exception as e:
                    logging.warning(f"⚠️ [TRADING] Failed to initialize trading service: {e}")
            
            # Start keepalive thread to maintain connection (prevents going offline)
            keepalive_thread = threading.Thread(target=keepalive_ibkr, daemon=True)
            keepalive_thread.start()
            logging.info("✅ [IBKR] Keepalive thread started (checks connection every 30s to prevent offline)")
            
            # Start trailing stop monitor thread
            if TRADING_AVAILABLE:
                trailing_stop_thread = threading.Thread(target=monitor_trailing_stops, daemon=True)
                trailing_stop_thread.start()
                logging.info("✅ [TRADING] Trailing stop monitor thread started")
    
    # Start IBKR connection in background thread so it doesn't block server startup
    if IBKR_AVAILABLE:
        ibkr_init_thread = threading.Thread(target=init_ibkr_connection, daemon=True)
        ibkr_init_thread.start()
    
    # Teach Ollama about IBKR trading and Level 2 data on startup
    def teach_ollama_ibkr():
        if OLLAMA_AVAILABLE:
            try:
                # Teach IBKR trading
                from ollama_ibkr_trading import teach_ibkr_trading_to_ollama
                logging.info("📚 [STARTUP] Teaching Ollama about IBKR trading...")
                result = teach_ibkr_trading_to_ollama()
                if result.get('success'):
                    logging.info("✅ [STARTUP] Ollama learned IBKR trading successfully")
                else:
                    logging.warning(f"⚠️ [STARTUP] Ollama IBKR teaching failed: {result.get('error')}")
            except Exception as e:
                logging.warning(f"⚠️ [STARTUP] Could not teach Ollama IBKR: {e}")
            
            try:
                # Teach Level 2 market data
                from ollama_level2_teaching import teach_level2_to_ollama
                logging.info("📚 [STARTUP] Teaching Ollama about Level 2 market data...")
                result = teach_level2_to_ollama()
                if result.get('success'):
                    logging.info("✅ [STARTUP] Ollama learned Level 2 market data successfully")
                else:
                    logging.warning(f"⚠️ [STARTUP] Ollama Level 2 teaching failed: {result.get('error')}")
                
                # Teach relative volume (RVOL)
                from ollama_volume_teaching import teach_relative_volume_to_ollama
                logging.info("📚 [STARTUP] Teaching Ollama about relative volume (RVOL)...")
                result = teach_relative_volume_to_ollama()
                if result.get('success'):
                    logging.info("✅ [STARTUP] Ollama learned relative volume successfully")
                else:
                    logging.warning(f"⚠️ [STARTUP] Ollama relative volume teaching failed: {result.get('error')}")
                
                # Teach stock float
                from ollama_float_teaching import teach_float_to_ollama
                logging.info("📚 [STARTUP] Teaching Ollama about stock float...")
                result = teach_float_to_ollama()
                if result.get('success'):
                    logging.info("✅ [STARTUP] Ollama learned stock float successfully")
                else:
                    logging.warning(f"⚠️ [STARTUP] Ollama float teaching failed: {result.get('error')}")
            except Exception as e:
                logging.warning(f"⚠️ [STARTUP] Could not teach Ollama Level 2: {e}")
    
    # Start Ollama teaching in background thread
    if OLLAMA_AVAILABLE:
        ollama_teach_thread = threading.Thread(target=teach_ollama_ibkr, daemon=True)
        ollama_teach_thread.start()
    
    # Start Flask server immediately
    logging.info("🚀 [STARTUP] Starting Flask server on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)

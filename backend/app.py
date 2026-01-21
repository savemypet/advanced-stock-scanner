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

# Proxy mode tracking
use_proxy_mode = False  # Switch to True when Yahoo blocks us
proxy_mode_until = None  # Timestamp when to switch back to direct
proxy_calls_used = 0  # Track monthly usage
proxy_calls_reset_date = None  # Reset counter monthly

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

def enable_proxy_mode():
    """Enable ScraperAPI proxy mode for 24 hours"""
    global use_proxy_mode, proxy_mode_until
    
    use_proxy_mode = True
    proxy_mode_until = datetime.now() + timedelta(hours=24)
    
    logging.warning("🔒 Yahoo Finance blocked! Enabling ScraperAPI proxy mode for 24 hours")
    logging.info(f"🕐 Proxy mode until: {proxy_mode_until.strftime('%Y-%m-%d %I:%M %p')}")

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
            
            if not summary or not graph_data:
                logging.warning(f"⚠️ SerpAPI returned incomplete data for {symbol}")
                return None
            
            # Parse current price
            current_price_str = summary.get('price', '0')
            current_price = float(current_price_str.replace('$', '').replace(',', ''))
            
            # Parse previous close
            prev_close_str = summary.get('previous_close', '0')
            previous_close = float(prev_close_str.replace('$', '').replace(',', ''))
            
            # Calculate change
            change_amount = current_price - previous_close
            change_percent = (change_amount / previous_close) * 100 if previous_close > 0 else 0
            
            # Build candle data from graph
            candles = []
            for point in graph_data[-60:]:  # Last 60 data points
                candles.append({
                    'time': point.get('date', datetime.now().isoformat()),
                    'open': float(point.get('price', current_price)),
                    'high': float(point.get('price', current_price)) * 1.01,  # Estimate
                    'low': float(point.get('price', current_price)) * 0.99,  # Estimate
                    'close': float(point.get('price', current_price)),
                    'volume': 1000000  # SerpAPI doesn't provide volume, use placeholder
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
        """Fetch real-time stock data from Yahoo Finance (with ScraperAPI fallback)"""
        try:
            # Configure yfinance to use proxy if needed
            if should_use_proxy():
                if SCRAPERAPI_KEY == 'YOUR_FREE_API_KEY':
                    logging.warning("⚠️ Proxy mode active but ScraperAPI key not configured!")
                    logging.warning("📝 Get free key from: https://www.scraperapi.com")
                    logging.warning("🔄 Attempting direct connection...")
                    ticker = yf.Ticker(symbol)
                else:
                    # Create proxy session for yfinance
                    session = requests.Session()
                    session.proxies = {
                        'http': f'{SCRAPERAPI_BASE_URL}?api_key={SCRAPERAPI_KEY}',
                        'https': f'{SCRAPERAPI_BASE_URL}?api_key={SCRAPERAPI_KEY}'
                    }
                    ticker = yf.Ticker(symbol, session=session)
                    track_proxy_usage()
                    logging.debug(f"🔄 Using ScraperAPI proxy for {symbol}")
            else:
                ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            
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
            
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty or len(hist) < 2:
                return None
                
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
                'lastUpdated': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error fetching data for {symbol}: {error_msg}")
            
            # Check for rate limit error
            # Yahoo returns HTML when rate limited, causing "Expecting value" JSON error
            if "429" in error_msg or "Too Many Requests" in error_msg or "Expecting value" in error_msg:
                # Enable ScraperAPI proxy mode if not already active
                if not should_use_proxy():
                    logging.warning(f"🚨 Rate limit detected for {symbol}!")
                    enable_proxy_mode()
                
                # Try SerpAPI as ultimate fallback
                logging.warning(f"🔍 Attempting SerpAPI fallback for {symbol}...")
                try:
                    serpapi_data = fetch_stock_from_serpapi(symbol)
                    if serpapi_data:
                        logging.info(f"✅ Successfully fetched {symbol} from SerpAPI fallback")
                        return serpapi_data
                except Exception as serpapi_error:
                    logging.error(f"❌ SerpAPI fallback also failed for {symbol}: {str(serpapi_error)}")
                
                raise Exception("RATE_LIMIT_ERROR: Yahoo Finance is rate limiting requests")
            
            return None
    
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
        
        # Include proxy status
        proxy_active = should_use_proxy()
        proxy_info = {}
        if proxy_active and proxy_mode_until:
            proxy_info = {
                'proxyMode': True,
                'proxyUntil': proxy_mode_until.isoformat(),
                'proxyCallsUsed': proxy_calls_used,
                'proxyCallsLimit': SCRAPERAPI_FREE_LIMIT
            }
        else:
            proxy_info = {'proxyMode': False}
        
        return jsonify({
            'success': True,
            'stocks': results,
            'timestamp': datetime.now().isoformat(),
            **proxy_info
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

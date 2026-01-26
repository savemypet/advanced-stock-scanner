"""
Fetch Level 2 Order Book Data from Interactive Brokers
Returns real order book depth for analysis
"""
import logging
from typing import Dict, List, Any, Optional

def fetch_level2_order_book(symbol: str, num_levels: int = 10) -> Optional[Dict[str, Any]]:
    """
    Fetch Level 2 order book data from IBKR
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        num_levels: Number of price levels to fetch (default 10)
        
    Returns:
        Dictionary with bids and asks, or None if unavailable
    """
    try:
        from app import IBKR_AVAILABLE, IBKR_INSTANCE, IBKR_LOCK, connect_ibkr
        from ib_insync import Stock
        
        if not IBKR_AVAILABLE:
            logging.debug(f"⚠️ [LEVEL2] IBKR not available for {symbol}")
            return None
        
        # Ensure connected
        if not connect_ibkr():
            logging.debug(f"⚠️ [LEVEL2] Could not connect to IBKR for {symbol}")
            return None
        
        with IBKR_LOCK:
            if not IBKR_INSTANCE or not IBKR_INSTANCE.isConnected():
                logging.debug(f"⚠️ [LEVEL2] IBKR not connected for {symbol}")
                return None
            
            # Create contract
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Request market depth (Level 2)
            # Note: reqMktDepth requires Level 2 subscription
            logging.info(f"📊 [LEVEL2] Requesting order book depth for {symbol}...")
            
            # Subscribe to market depth
            IBKR_INSTANCE.reqMktDepth(contract, num_levels)
            IBKR_INSTANCE.sleep(0.5)  # Wait for data
            
            # Get market depth from ticker
            ticker = IBKR_INSTANCE.ticker(contract)
            
            # Extract bid and ask data
            bids = []
            asks = []
            
            if hasattr(ticker, 'domBids') and ticker.domBids:
                for bid in ticker.domBids[:num_levels]:
                    bids.append({
                        'price': float(bid.price) if bid.price else 0.0,
                        'size': int(bid.size) if bid.size else 0,
                        'marketMaker': bid.marketMaker if hasattr(bid, 'marketMaker') else 'Unknown'
                    })
            
            if hasattr(ticker, 'domAsks') and ticker.domAsks:
                for ask in ticker.domAsks[:num_levels]:
                    asks.append({
                        'price': float(ask.price) if ask.price else 0.0,
                        'size': int(ask.size) if ask.size else 0,
                        'marketMaker': ask.marketMaker if hasattr(ask, 'marketMaker') else 'Unknown'
                    })
            
            if not bids and not asks:
                logging.debug(f"⚠️ [LEVEL2] No order book data available for {symbol}")
                return None
            
            # Calculate totals
            total_bid_size = sum(b['size'] for b in bids)
            total_ask_size = sum(a['size'] for a in asks)
            bid_ask_ratio = total_bid_size / total_ask_size if total_ask_size > 0 else 1.0
            
            level2_data = {
                'symbol': symbol,
                'bids': bids,
                'asks': asks,
                'totalBidSize': total_bid_size,
                'totalAskSize': total_ask_size,
                'bidAskRatio': bid_ask_ratio,
                'bestBid': float(bids[0]['price']) if bids else None,
                'bestAsk': float(asks[0]['price']) if asks else None,
                'spread': float(asks[0]['price'] - bids[0]['price']) if (bids and asks) else None,
                'timestamp': None  # Will be set by caller
            }
            
            logging.info(f"✅ [LEVEL2] Retrieved order book for {symbol}: {len(bids)} bid levels, {len(asks)} ask levels")
            logging.info(f"   Total Bids: {total_bid_size:,} shares, Total Asks: {total_ask_size:,} shares, Ratio: {bid_ask_ratio:.2f}")
            
            return level2_data
            
    except Exception as e:
        logging.warning(f"⚠️ [LEVEL2] Error fetching Level 2 data for {symbol}: {e}")
        return None

def get_level2_summary(level2_data: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of Level 2 data for Ollama analysis
    
    Args:
        level2_data: Level 2 data dictionary
        
    Returns:
        Formatted string summary
    """
    if not level2_data:
        return ""
    
    bids = level2_data.get('bids', [])
    asks = level2_data.get('asks', [])
    total_bid = level2_data.get('totalBidSize', 0)
    total_ask = level2_data.get('totalAskSize', 0)
    ratio = level2_data.get('bidAskRatio', 1.0)
    best_bid = level2_data.get('bestBid')
    best_ask = level2_data.get('bestAsk')
    spread = level2_data.get('spread')
    
    summary = f"""
LEVEL 2 ORDER BOOK SUMMARY:
- Best Bid: ${best_bid:.2f} | Best Ask: ${best_ask:.2f} | Spread: ${spread:.2f}
- Total Bid Size: {total_bid:,} shares
- Total Ask Size: {total_ask:,} shares
- Bid/Ask Ratio: {ratio:.2f} ({'Strong Buying Pressure' if ratio > 2.0 else 'Strong Selling Pressure' if ratio < 0.5 else 'Balanced'})

TOP 5 BID LEVELS (Support):
"""
    
    for i, bid in enumerate(bids[:5], 1):
        summary += f"  {i}. ${bid['price']:.2f} - {bid['size']:,} shares\n"
    
    summary += "\nTOP 5 ASK LEVELS (Resistance):\n"
    for i, ask in enumerate(asks[:5], 1):
        summary += f"  {i}. ${ask['price']:.2f} - {ask['size']:,} shares\n"
    
    return summary

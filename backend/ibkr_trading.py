"""
Interactive Brokers Trading Service
Handles buy/sell orders with stop loss and take profit
"""
import logging
import traceback
import threading
from typing import Dict, Any, Optional
from ib_insync import IB, Stock, MarketOrder, LimitOrder, StopOrder, StopLimitOrder, Order, Trade
from datetime import datetime

# Import IBKR connection from app.py
# This will be set by the main app
IBKR_INSTANCE: Optional[IB] = None
IBKR_LOCK = None  # Will be set by app.py

def set_ibkr_instance(ib_instance: IB, ib_lock):
    """Set the IBKR instance and lock from the main app"""
    global IBKR_INSTANCE, IBKR_LOCK
    IBKR_INSTANCE = ib_instance
    IBKR_LOCK = ib_lock

def place_market_order(
    symbol: str,
    action: str,  # 'BUY' or 'SELL'
    quantity: int,
    stop_loss_percent: Optional[float] = None,
    take_profit_percent: Optional[float] = None,
    trailing_stop_percent: Optional[float] = None
) -> Dict[str, Any]:
    """
    Place a market order with optional stop loss and take profit
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        action: 'BUY' or 'SELL'
        quantity: Number of shares
        stop_loss_percent: Stop loss as percentage (e.g., 2.0 for 2%)
        take_profit_percent: Take profit as percentage (e.g., 5.0 for 5%)
    
    Returns:
        Dict with order details and status
    """
    if not IBKR_INSTANCE or not IBKR_INSTANCE.isConnected():
        return {
            'success': False,
            'error': 'IBKR not connected',
            'message': 'Interactive Brokers is not connected. Please connect first.'
        }
    
    if IBKR_LOCK is None:
        return {
            'success': False,
            'error': 'IBKR lock not initialized',
            'message': 'Trading service not properly initialized'
        }
    
    try:
        with IBKR_LOCK:
            # Create stock contract
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Get current market price
            IBKR_INSTANCE.reqMktData(contract, '', False, False)
            ticker = IBKR_INSTANCE.ticker(contract)
            IBKR_INSTANCE.sleep(0.5)  # Wait for market data
            
            if not ticker.marketPrice():
                # Fallback: use last price
                current_price = ticker.last or ticker.close or 0
                if current_price == 0:
                    return {
                        'success': False,
                        'error': 'No market price available',
                        'message': f'Could not get current price for {symbol}'
                    }
            else:
                current_price = ticker.marketPrice()
            
            logging.info(f"📈 [TRADING] Placing {action} order for {quantity} shares of {symbol} at ${current_price:.2f}")
            
            # Create parent market order
            parent_order = MarketOrder(action, quantity)
            parent_order.transmit = False  # Don't transmit until bracket is ready
            
            # Place parent order
            parent_trade = IBKR_INSTANCE.placeOrder(contract, parent_order)
            parent_order_id = parent_trade.order.orderId
            
            logging.info(f"✅ [TRADING] Parent order placed: Order ID {parent_order_id}")
            
            # Calculate stop loss and take profit prices
            if action == 'BUY':
                if stop_loss_percent:
                    stop_loss_price = current_price * (1 - stop_loss_percent / 100)
                if take_profit_percent:
                    take_profit_price = current_price * (1 + take_profit_percent / 100)
            else:  # SELL
                if stop_loss_percent:
                    stop_loss_price = current_price * (1 + stop_loss_percent / 100)
                if take_profit_percent:
                    take_profit_price = current_price * (1 - take_profit_percent / 100)
            
            # Create bracket orders
            bracket_orders = []
            
            # Take profit order (if specified)
            if take_profit_percent:
                take_profit_order = LimitOrder(
                    'SELL' if action == 'BUY' else 'BUY',
                    quantity,
                    lmtPrice=take_profit_price
                )
                take_profit_order.parentId = parent_order_id
                take_profit_order.transmit = False
                bracket_orders.append(take_profit_order)
                logging.info(f"🎯 [TRADING] Take profit set at ${take_profit_price:.2f} ({take_profit_percent}%)")
            
            # Stop loss order (if specified)
            if stop_loss_percent:
                stop_loss_order = StopOrder(
                    'SELL' if action == 'BUY' else 'BUY',
                    quantity,
                    stopPrice=stop_loss_price
                )
                stop_loss_order.parentId = parent_order_id
                stop_loss_order.transmit = True  # Last order transmits all
                bracket_orders.append(stop_loss_order)
                logging.info(f"🛑 [TRADING] Stop loss set at ${stop_loss_price:.2f} ({stop_loss_percent}%)")
            
            # Place bracket orders
            bracket_trades = []
            for order in bracket_orders:
                trade = IBKR_INSTANCE.placeOrder(contract, order)
                bracket_trades.append(trade)
                logging.info(f"✅ [TRADING] Bracket order placed: {order.action} {order.totalQuantity} @ ${order.auxPrice or order.lmtPrice:.2f}")
            
            # Now transmit the parent order
            parent_order.transmit = True
            IBKR_INSTANCE.placeOrder(contract, parent_order)
            
            # Register for trailing stop if specified
            if trailing_stop_percent and stop_loss_percent:
                register_trade_for_trailing(
                    order_id=parent_order_id,
                    symbol=symbol,
                    action=action,
                    entry_price=current_price,
                    initial_stop_loss=stop_loss_price,
                    trailing_percent=trailing_stop_percent
                )
                logging.info(f"📈 [TRADING] Trailing stop enabled: {trailing_stop_percent}%")
            
            result = {
                'success': True,
                'orderId': parent_order_id,
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'entryPrice': current_price,
                'stopLossPrice': stop_loss_price if stop_loss_percent else None,
                'stopLossPercent': stop_loss_percent,
                'takeProfitPrice': take_profit_price if take_profit_percent else None,
                'takeProfitPercent': take_profit_percent,
                'trailingStopPercent': trailing_stop_percent,
                'timestamp': datetime.now().isoformat(),
                'status': 'Submitted',
                'message': f'{action} order placed for {quantity} shares of {symbol}'
            }
            
            logging.info(f"✅ [TRADING] Order complete: {result['message']}")
            return result
            
    except Exception as e:
        error_msg = f"Error placing {action} order for {symbol}: {str(e)}"
        logging.error(f"❌ [TRADING] {error_msg}")
        logging.error(f"❌ [TRADING] Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'message': error_msg
        }

def place_limit_order(
    symbol: str,
    action: str,
    quantity: int,
    limit_price: float,
    stop_loss_percent: Optional[float] = None,
    take_profit_percent: Optional[float] = None,
    trailing_stop_percent: Optional[float] = None
) -> Dict[str, Any]:
    """
    Place a limit order with optional stop loss and take profit
    
    Args:
        symbol: Stock symbol
        action: 'BUY' or 'SELL'
        quantity: Number of shares
        limit_price: Limit price for the order
        stop_loss_percent: Stop loss as percentage
        take_profit_percent: Take profit as percentage
    
    Returns:
        Dict with order details and status
    """
    if not IBKR_INSTANCE or not IBKR_INSTANCE.isConnected():
        return {
            'success': False,
            'error': 'IBKR not connected',
            'message': 'Interactive Brokers is not connected'
        }
    
    if IBKR_LOCK is None:
        return {
            'success': False,
            'error': 'IBKR lock not initialized'
        }
    
    try:
        with IBKR_LOCK:
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Create parent limit order
            parent_order = LimitOrder(action, quantity, lmtPrice=limit_price)
            parent_order.transmit = False
            
            # Place parent order
            parent_trade = IBKR_INSTANCE.placeOrder(contract, parent_order)
            parent_order_id = parent_trade.order.orderId
            
            logging.info(f"📈 [TRADING] Placing LIMIT {action} order for {quantity} shares of {symbol} at ${limit_price:.2f}")
            
            # Calculate stop loss and take profit prices
            if action == 'BUY':
                if stop_loss_percent:
                    stop_loss_price = limit_price * (1 - stop_loss_percent / 100)
                if take_profit_percent:
                    take_profit_price = limit_price * (1 + take_profit_percent / 100)
            else:  # SELL
                if stop_loss_percent:
                    stop_loss_price = limit_price * (1 + stop_loss_percent / 100)
                if take_profit_percent:
                    take_profit_price = limit_price * (1 - take_profit_percent / 100)
            
            # Create bracket orders
            bracket_orders = []
            
            if take_profit_percent:
                take_profit_order = LimitOrder(
                    'SELL' if action == 'BUY' else 'BUY',
                    quantity,
                    lmtPrice=take_profit_price
                )
                take_profit_order.parentId = parent_order_id
                take_profit_order.transmit = False
                bracket_orders.append(take_profit_order)
            
            if stop_loss_percent:
                stop_loss_order = StopOrder(
                    'SELL' if action == 'BUY' else 'BUY',
                    quantity,
                    stopPrice=stop_loss_price
                )
                stop_loss_order.parentId = parent_order_id
                stop_loss_order.transmit = True
                bracket_orders.append(stop_loss_order)
            
            # Place bracket orders
            for order in bracket_orders:
                IBKR_INSTANCE.placeOrder(contract, order)
            
            # Transmit parent order
            parent_order.transmit = True
            IBKR_INSTANCE.placeOrder(contract, parent_order)
            
            # Register for trailing stop if specified
            if trailing_stop_percent and stop_loss_percent:
                register_trade_for_trailing(
                    order_id=parent_order_id,
                    symbol=symbol,
                    action=action,
                    entry_price=limit_price,
                    initial_stop_loss=stop_loss_price,
                    trailing_percent=trailing_stop_percent
                )
                logging.info(f"📈 [TRADING] Trailing stop enabled: {trailing_stop_percent}%")
            
            result = {
                'success': True,
                'orderId': parent_order_id,
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'limitPrice': limit_price,
                'stopLossPrice': stop_loss_price if stop_loss_percent else None,
                'stopLossPercent': stop_loss_percent,
                'takeProfitPrice': take_profit_price if take_profit_percent else None,
                'takeProfitPercent': take_profit_percent,
                'trailingStopPercent': trailing_stop_percent,
                'timestamp': datetime.now().isoformat(),
                'status': 'Submitted',
                'message': f'LIMIT {action} order placed for {quantity} shares of {symbol} at ${limit_price:.2f}'
            }
            
            logging.info(f"✅ [TRADING] Limit order complete: {result['message']}")
            return result
            
    except Exception as e:
        error_msg = f"Error placing limit {action} order for {symbol}: {str(e)}"
        logging.error(f"❌ [TRADING] {error_msg}")
        return {
            'success': False,
            'error': str(e),
            'message': error_msg
        }

def cancel_order(order_id: int) -> Dict[str, Any]:
    """Cancel an order by order ID"""
    if not IBKR_INSTANCE or not IBKR_INSTANCE.isConnected():
        return {
            'success': False,
            'error': 'IBKR not connected'
        }
    
    try:
        # Find the trade by order ID
        trades = IBKR_INSTANCE.trades()
        for trade in trades:
            if trade.order.orderId == order_id:
                IBKR_INSTANCE.cancelOrder(trade.order)
                logging.info(f"✅ [TRADING] Order {order_id} cancelled")
                return {
                    'success': True,
                    'orderId': order_id,
                    'message': f'Order {order_id} cancelled'
                }
        
        return {
            'success': False,
            'error': 'Order not found',
            'message': f'Order {order_id} not found'
        }
    except Exception as e:
        logging.error(f"❌ [TRADING] Error cancelling order {order_id}: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Error cancelling order: {str(e)}'
        }

def get_order_status(order_id: int) -> Dict[str, Any]:
    """Get status of an order"""
    if not IBKR_INSTANCE or not IBKR_INSTANCE.isConnected():
        return {
            'success': False,
            'error': 'IBKR not connected'
        }
    
    try:
        trades = IBKR_INSTANCE.trades()
        for trade in trades:
            if trade.order.orderId == order_id:
                return {
                    'success': True,
                    'orderId': order_id,
                    'status': trade.orderStatus.status,
                    'filled': trade.orderStatus.filled,
                    'remaining': trade.orderStatus.remaining,
                    'avgFillPrice': trade.orderStatus.avgFillPrice,
                    'message': f'Order {order_id} status: {trade.orderStatus.status}'
                }
        
        return {
            'success': False,
            'error': 'Order not found'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Trailing stop tracking
ACTIVE_TRADES: Dict[int, Dict[str, Any]] = {}  # {order_id: {symbol, entry_price, stop_loss_price, trailing_percent, highest_price}}
TRADING_LOCK = threading.Lock()

def update_trailing_stop(order_id: int, current_price: float) -> Optional[Dict[str, Any]]:
    """
    Update trailing stop loss for an active trade
    
    Args:
        order_id: Parent order ID
        current_price: Current market price
    
    Returns:
        Updated stop loss info or None if no update needed
    """
    if IBKR_LOCK is None:
        return None
    
    with TRADING_LOCK:
        if order_id not in ACTIVE_TRADES:
            return None
        
        trade_info = ACTIVE_TRADES[order_id]
        entry_price = trade_info.get('entry_price', 0)
        trailing_percent = trade_info.get('trailing_percent', 0)
        highest_price = trade_info.get('highest_price', entry_price)
        current_stop = trade_info.get('stop_loss_price', 0)
        action = trade_info.get('action', 'BUY')
        
        if trailing_percent <= 0:
            return None
        
        # Update highest price if current price is higher
        if action == 'BUY' and current_price > highest_price:
            trade_info['highest_price'] = current_price
            highest_price = current_price
            
            # Calculate new stop loss (trailing below highest price)
            new_stop = highest_price * (1 - trailing_percent / 100)
            
            # Only update if new stop is higher than current stop (never lower)
            if new_stop > current_stop:
                trade_info['stop_loss_price'] = new_stop
                return {
                    'order_id': order_id,
                    'symbol': trade_info.get('symbol'),
                    'new_stop_loss': new_stop,
                    'highest_price': highest_price,
                    'profit_locked': ((new_stop - entry_price) / entry_price * 100) if entry_price > 0 else 0
                }
        
        elif action == 'SELL' and current_price < highest_price:
            # For SELL, highest_price is actually lowest_price (best price for short)
            trade_info['highest_price'] = current_price
            highest_price = current_price
            
            # Calculate new stop loss (trailing above lowest price for short)
            new_stop = highest_price * (1 + trailing_percent / 100)
            
            # Only update if new stop is lower than current stop (never higher for shorts)
            if new_stop < current_stop or current_stop == 0:
                trade_info['stop_loss_price'] = new_stop
                return {
                    'order_id': order_id,
                    'symbol': trade_info.get('symbol'),
                    'new_stop_loss': new_stop,
                    'lowest_price': highest_price,
                    'profit_locked': ((entry_price - new_stop) / entry_price * 100) if entry_price > 0 else 0
                }
    
    return None

def register_trade_for_trailing(order_id: int, symbol: str, action: str, entry_price: float, 
                                initial_stop_loss: float, trailing_percent: Optional[float] = None):
    """Register a trade for trailing stop monitoring"""
    with TRADING_LOCK:
        ACTIVE_TRADES[order_id] = {
            'symbol': symbol,
            'action': action,
            'entry_price': entry_price,
            'stop_loss_price': initial_stop_loss,
            'trailing_percent': trailing_percent or 0,
            'highest_price': entry_price,
            'timestamp': datetime.now().isoformat()
        }

def unregister_trade(order_id: int):
    """Remove trade from trailing stop tracking"""
    with TRADING_LOCK:
        if order_id in ACTIVE_TRADES:
            del ACTIVE_TRADES[order_id]

def get_account_balance() -> float:
    """Get account balance from IBKR"""
    if not IBKR_INSTANCE or not IBKR_INSTANCE.isConnected():
        return 0.0
    
    try:
        account_values = IBKR_INSTANCE.accountValues()
        # Look for NetLiquidation or TotalCashValue
        for av in account_values:
            if av.tag == 'NetLiquidation' or av.tag == 'TotalCashValue':
                try:
                    return float(av.value)
                except (ValueError, TypeError):
                    continue
        
        # Fallback: try to get from account summary
        try:
            account_summary = IBKR_INSTANCE.accountSummary()
            for summary in account_summary:
                if summary.tag == 'NetLiquidation':
                    try:
                        return float(summary.value)
                    except (ValueError, TypeError):
                        continue
        except:
            pass
        
        return 0.0
    except Exception as e:
        logging.error(f"❌ [TRADING] Error getting account balance: {e}")
        return 0.0

def get_open_positions() -> Dict[str, Any]:
    """Get all open positions"""
    if not IBKR_INSTANCE or not IBKR_INSTANCE.isConnected():
        return {
            'success': False,
            'error': 'IBKR not connected',
            'positions': []
        }
    
    try:
        positions = IBKR_INSTANCE.positions()
        result = []
        for pos in positions:
            result.append({
                'symbol': pos.contract.symbol,
                'position': pos.position,
                'avgCost': pos.avgCost,
                'marketPrice': pos.marketPrice if hasattr(pos, 'marketPrice') else None,
                'marketValue': pos.position * (pos.marketPrice if hasattr(pos, 'marketPrice') else pos.avgCost)
            })
        
        return {
            'success': True,
            'positions': result,
            'count': len(result)
        }
    except Exception as e:
        logging.error(f"❌ [TRADING] Error getting positions: {e}")
        return {
            'success': False,
            'error': str(e),
            'positions': []
        }

import { useState } from 'react';
import { Stock } from '../types';
import { TrendingUp, TrendingDown, DollarSign, AlertTriangle, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

interface TradingPanelProps {
  stock: Stock;
}

export default function TradingPanel({ stock }: TradingPanelProps) {
  const [quantity, setQuantity] = useState<number>(100);
  const [stopLossPercent, setStopLossPercent] = useState<number>(2.0);
  const [takeProfitPercent, setTakeProfitPercent] = useState<number>(5.0);
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('MARKET');
  const [limitPrice, setLimitPrice] = useState<number>(stock.currentPrice);
  const [loading, setLoading] = useState<'buy' | 'sell' | null>(null);
  const [lastOrder, setLastOrder] = useState<any>(null);

  const handleBuy = async () => {
    if (quantity <= 0) {
      toast.error('Quantity must be greater than 0');
      return;
    }

    if (orderType === 'LIMIT' && (!limitPrice || limitPrice <= 0)) {
      toast.error('Limit price must be greater than 0');
      return;
    }

    setLoading('buy');
    try {
      const response = await axios.post(`${API_BASE_URL}/api/trade/buy`, {
        symbol: stock.symbol,
        quantity,
        orderType: orderType,
        limitPrice: orderType === 'LIMIT' ? limitPrice : undefined,
        stopLossPercent: stopLossPercent > 0 ? stopLossPercent : undefined,
        takeProfitPercent: takeProfitPercent > 0 ? takeProfitPercent : undefined,
      });

      if (response.data.success) {
        setLastOrder(response.data);
        toast.success('Buy order placed successfully!', {
          description: `${quantity} shares of ${stock.symbol} @ ${orderType === 'MARKET' ? 'Market' : `$${limitPrice.toFixed(2)}`}`,
          duration: 5000,
        });
      } else {
        toast.error('Order failed', {
          description: response.data.error || response.data.message,
        });
      }
    } catch (error: any) {
      toast.error('Error placing order', {
        description: error.response?.data?.error || error.message,
      });
    } finally {
      setLoading(null);
    }
  };

  const handleSell = async () => {
    if (quantity <= 0) {
      toast.error('Quantity must be greater than 0');
      return;
    }

    if (orderType === 'LIMIT' && (!limitPrice || limitPrice <= 0)) {
      toast.error('Limit price must be greater than 0');
      return;
    }

    setLoading('sell');
    try {
      const response = await axios.post(`${API_BASE_URL}/api/trade/sell`, {
        symbol: stock.symbol,
        quantity,
        orderType: orderType,
        limitPrice: orderType === 'LIMIT' ? limitPrice : undefined,
        stopLossPercent: stopLossPercent > 0 ? stopLossPercent : undefined,
        takeProfitPercent: takeProfitPercent > 0 ? takeProfitPercent : undefined,
      });

      if (response.data.success) {
        setLastOrder(response.data);
        toast.success('Sell order placed successfully!', {
          description: `${quantity} shares of ${stock.symbol} @ ${orderType === 'MARKET' ? 'Market' : `$${limitPrice.toFixed(2)}`}`,
          duration: 5000,
        });
      } else {
        toast.error('Order failed', {
          description: response.data.error || response.data.message,
        });
      }
    } catch (error: any) {
      toast.error('Error placing order', {
        description: error.response?.data?.error || error.message,
      });
    } finally {
      setLoading(null);
    }
  };

  const riskRewardRatio = takeProfitPercent > 0 && stopLossPercent > 0 
    ? (takeProfitPercent / stopLossPercent).toFixed(2) 
    : 'N/A';

  return (
    <div className="p-4 bg-card border border-border rounded-lg space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <DollarSign className="w-5 h-5 text-primary" />
        <h3 className="font-semibold text-foreground">Trading</h3>
      </div>

      {/* Order Type Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">Order Type</label>
        <div className="flex gap-2">
          <button
            onClick={() => setOrderType('MARKET')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              orderType === 'MARKET'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            Market
          </button>
          <button
            onClick={() => setOrderType('LIMIT')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              orderType === 'LIMIT'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            Limit
          </button>
        </div>
      </div>

      {/* Limit Price (if LIMIT order) */}
      {orderType === 'LIMIT' && (
        <div>
          <label className="block text-sm font-medium mb-2">Limit Price ($)</label>
          <input
            type="number"
            step="0.01"
            value={limitPrice}
            onChange={(e) => setLimitPrice(parseFloat(e.target.value) || 0)}
            className="w-full px-3 py-2 rounded-md bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="0.00"
          />
        </div>
      )}

      {/* Quantity */}
      <div>
        <label className="block text-sm font-medium mb-2">Quantity (Shares)</label>
        <input
          type="number"
          min="1"
          value={quantity}
          onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
          className="w-full px-3 py-2 rounded-md bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="100"
        />
      </div>

      {/* Stop Loss */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Stop Loss (%)
          <span className="text-xs text-muted-foreground ml-2">Optional</span>
        </label>
        <input
          type="number"
          step="0.1"
          min="0"
          max="100"
          value={stopLossPercent}
          onChange={(e) => setStopLossPercent(parseFloat(e.target.value) || 0)}
          className="w-full px-3 py-2 rounded-md bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="2.0"
        />
        {stopLossPercent > 0 && (
          <p className="text-xs text-muted-foreground mt-1">
            Stop Loss: ${(stock.currentPrice * (1 - stopLossPercent / 100)).toFixed(2)}
          </p>
        )}
      </div>

      {/* Take Profit */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Take Profit (%)
          <span className="text-xs text-muted-foreground ml-2">Optional</span>
        </label>
        <input
          type="number"
          step="0.1"
          min="0"
          max="100"
          value={takeProfitPercent}
          onChange={(e) => setTakeProfitPercent(parseFloat(e.target.value) || 0)}
          className="w-full px-3 py-2 rounded-md bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="5.0"
        />
        {takeProfitPercent > 0 && (
          <p className="text-xs text-muted-foreground mt-1">
            Take Profit: ${(stock.currentPrice * (1 + takeProfitPercent / 100)).toFixed(2)}
          </p>
        )}
      </div>

      {/* Risk-Reward Ratio */}
      {stopLossPercent > 0 && takeProfitPercent > 0 && (
        <div className="p-2 bg-muted/50 rounded-md">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Risk-Reward Ratio</span>
            <span className={`text-sm font-bold ${
              parseFloat(riskRewardRatio) >= 2 ? 'text-green-500' :
              parseFloat(riskRewardRatio) >= 1.5 ? 'text-yellow-500' :
              'text-red-500'
            }`}>
              {riskRewardRatio}:1
            </span>
          </div>
          {parseFloat(riskRewardRatio) < 1.5 && (
            <p className="text-xs text-yellow-500 mt-1">
              <AlertTriangle className="w-3 h-3 inline mr-1" />
              Low risk-reward ratio. Consider adjusting targets.
            </p>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2 pt-2">
        <button
          onClick={handleBuy}
          disabled={loading !== null || quantity <= 0}
          className="flex-1 px-4 py-3 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
        >
          {loading === 'buy' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Placing...</span>
            </>
          ) : (
            <>
              <TrendingUp className="w-4 h-4" />
              <span>Buy</span>
            </>
          )}
        </button>
        <button
          onClick={handleSell}
          disabled={loading !== null || quantity <= 0}
          className="flex-1 px-4 py-3 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
        >
          {loading === 'sell' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Placing...</span>
            </>
          ) : (
            <>
              <TrendingDown className="w-4 h-4" />
              <span>Sell</span>
            </>
          )}
        </button>
      </div>

      {/* Last Order Info */}
      {lastOrder && (
        <div className="p-3 bg-muted/50 border border-border rounded-md mt-4">
          <div className="flex items-center gap-2 mb-2">
            {lastOrder.success ? (
              <CheckCircle2 className="w-4 h-4 text-green-500" />
            ) : (
              <XCircle className="w-4 h-4 text-red-500" />
            )}
            <span className="text-sm font-medium">Last Order</span>
          </div>
          <div className="text-xs text-muted-foreground space-y-1">
            <p>Order ID: {lastOrder.orderId}</p>
            <p>Status: {lastOrder.status}</p>
            {lastOrder.entryPrice && <p>Entry: ${lastOrder.entryPrice.toFixed(2)}</p>}
            {lastOrder.stopLossPrice && <p>Stop Loss: ${lastOrder.stopLossPrice.toFixed(2)}</p>}
            {lastOrder.takeProfitPrice && <p>Take Profit: ${lastOrder.takeProfitPrice.toFixed(2)}</p>}
          </div>
        </div>
      )}

      {/* Warning */}
      <div className="p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-md">
        <p className="text-xs text-yellow-600">
          <AlertTriangle className="w-3 h-3 inline mr-1" />
          Trading involves risk. Always use stop loss and proper position sizing.
        </p>
      </div>
    </div>
  );
}

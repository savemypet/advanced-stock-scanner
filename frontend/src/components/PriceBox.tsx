import { Candle } from '../types'
import { formatCurrency } from '../utils/formatters'

interface PriceBoxProps {
  candles: Candle[]
  currentPrice: number
  height?: number
}

export default function PriceBox({ candles, currentPrice, height = 500 }: PriceBoxProps) {
  // Calculate 24h high and low from candles
  const calculate24hLevels = () => {
    if (!candles || candles.length === 0) {
      return { high24h: currentPrice, low24h: currentPrice }
    }
    
    // Get last 24 hours of data (or all if less than 24h)
    const now = new Date().getTime()
    const twentyFourHoursAgo = now - (24 * 60 * 60 * 1000)
    
    const last24hCandles = candles.filter(candle => {
      const candleTime = new Date(candle.time).getTime()
      return candleTime >= twentyFourHoursAgo
    })
    
    if (last24hCandles.length === 0) {
      // Fallback to all candles if no 24h data
      const allHighs = candles.map(c => c.high)
      const allLows = candles.map(c => c.low)
      return {
        high24h: Math.max(...allHighs),
        low24h: Math.min(...allLows)
      }
    }
    
    const high24h = Math.max(...last24hCandles.map(c => c.high))
    const low24h = Math.min(...last24hCandles.map(c => c.low))
    
    return { high24h, low24h }
  }
  
  const { high24h, low24h } = calculate24hLevels()
  const priceRange = high24h - low24h
  const currentPosition = priceRange > 0 
    ? ((currentPrice - low24h) / priceRange) * 100 
    : 50
  
  const isPositive = currentPrice >= (high24h + low24h) / 2
  
  return (
    <div 
      className="w-full bg-gradient-to-br from-gray-900 to-black rounded-lg border border-gray-800 p-6 flex flex-col items-center justify-center"
      style={{ height: `${height}px` }}
    >
      {/* Current Price - Large Display */}
      <div className="text-center mb-8">
        <div className="text-sm text-gray-400 mb-2 font-medium">Current Price</div>
        <div className={`text-5xl sm:text-6xl font-bold mb-2 ${
          isPositive ? 'text-green-400' : 'text-red-400'
        }`}>
          {formatCurrency(currentPrice)}
        </div>
        <div className="text-xs text-gray-500">
          {new Date().toLocaleTimeString()}
        </div>
      </div>
      
      {/* 24h High/Low Box */}
      <div className="w-full max-w-md bg-gray-800/50 rounded-lg border border-gray-700 p-6 space-y-4">
        <div className="text-center mb-4">
          <div className="text-sm font-semibold text-gray-300 mb-1">24 Hour Range</div>
          <div className="text-xs text-gray-500">High and Low Prices</div>
        </div>
        
        {/* 24h High */}
        <div className="flex items-center justify-between p-4 bg-green-500/10 rounded-lg border border-green-500/30">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <div>
              <div className="text-xs text-gray-400">24h High</div>
              <div className="text-xl font-bold text-green-400">
                {formatCurrency(high24h)}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500">+{((high24h - currentPrice) / currentPrice * 100).toFixed(2)}%</div>
            <div className="text-xs text-gray-500">from current</div>
          </div>
        </div>
        
        {/* Price Range Indicator */}
        <div className="relative h-3 bg-gray-700 rounded-full overflow-hidden">
          <div 
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
            style={{ width: '100%' }}
          />
          <div 
            className="absolute top-0 w-1 h-full bg-white shadow-lg z-10"
            style={{ left: `${currentPosition}%`, transform: 'translateX(-50%)' }}
          />
        </div>
        <div className="text-center text-xs text-gray-400">
          Current price position in 24h range
        </div>
        
        {/* 24h Low */}
        <div className="flex items-center justify-between p-4 bg-red-500/10 rounded-lg border border-red-500/30">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div>
              <div className="text-xs text-gray-400">24h Low</div>
              <div className="text-xl font-bold text-red-400">
                {formatCurrency(low24h)}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500">{((low24h - currentPrice) / currentPrice * 100).toFixed(2)}%</div>
            <div className="text-xs text-gray-500">from current</div>
          </div>
        </div>
        
        {/* Range Summary */}
        <div className="pt-4 border-t border-gray-700">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Range:</span>
            <span className="text-white font-semibold">
              {formatCurrency(priceRange)} ({((priceRange / currentPrice) * 100).toFixed(2)}%)
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

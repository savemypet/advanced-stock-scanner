import { Candle } from '../types'
import { formatCurrency } from '../utils/formatters'
import { useState, useEffect, useMemo } from 'react'
import { detectPatterns, getLatestSignal, PatternSignal } from '../utils/candlestickPatterns'

interface PriceBoxProps {
  candles: Candle[]
  currentPrice: number
  height?: number
}

export default function PriceBox({ candles, currentPrice, height = 500 }: PriceBoxProps) {
  const [animatedPrice, setAnimatedPrice] = useState(currentPrice)
  
  // Animate price changes
  useEffect(() => {
    const diff = currentPrice - animatedPrice
    if (Math.abs(diff) > 0.01) {
      const steps = 20
      const stepSize = diff / steps
      let currentStep = 0
      
      const interval = setInterval(() => {
        currentStep++
        if (currentStep >= steps) {
          setAnimatedPrice(currentPrice)
          clearInterval(interval)
        } else {
          setAnimatedPrice(prev => prev + stepSize)
        }
      }, 20)
      
      return () => clearInterval(interval)
    }
  }, [currentPrice])
  
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
  const padding = priceRange * 0.05 // 5% padding on top and bottom
  const totalRange = priceRange + (padding * 2)
  const minPrice = low24h - padding
  const maxPrice = high24h + padding
  
  // Calculate position of current price (0% = bottom/low, 100% = top/high)
  const currentPosition = totalRange > 0 
    ? ((animatedPrice - minPrice) / totalRange) * 100 
    : 50
  
  // Calculate position from top (inverted for display)
  const currentPositionFromTop = 100 - currentPosition
  
  // AI Pattern Detection and Recommendations
  const aiRecommendation = useMemo(() => {
    if (!candles || candles.length === 0) return null
    
    const latestSignal = getLatestSignal(candles)
    if (!latestSignal || (latestSignal.confidence !== 'HIGH' && latestSignal.confidence !== 'MEDIUM')) {
      return null
    }
    
    const signalCandle = candles[latestSignal.candleIndex]
    if (!signalCandle) return null
    
    // Calculate recommended prices
    let recommendedPrice: number
    let priceReason: string
    
    if (latestSignal.signal === 'BUY') {
      // For BUY: recommend entry at current low or slightly below for better entry
      recommendedPrice = Math.min(currentPrice, signalCandle.low)
      // If price is near low, suggest buying now, otherwise suggest waiting for pullback
      if (currentPrice <= signalCandle.low * 1.01) {
        recommendedPrice = currentPrice
        priceReason = 'Buy now at current price'
      } else {
        recommendedPrice = signalCandle.low * 0.998 // Slightly below low for better entry
        priceReason = `Buy on pullback to ${formatCurrency(recommendedPrice)}`
      }
    } else {
      // For SELL: recommend exit at current high or slightly above for better exit
      recommendedPrice = Math.max(currentPrice, signalCandle.high)
      // If price is near high, suggest selling now, otherwise suggest waiting for rally
      if (currentPrice >= signalCandle.high * 0.99) {
        recommendedPrice = currentPrice
        priceReason = 'Sell now at current price'
      } else {
        recommendedPrice = signalCandle.high * 1.002 // Slightly above high for better exit
        priceReason = `Sell on rally to ${formatCurrency(recommendedPrice)}`
      }
    }
    
    return {
      signal: latestSignal.signal,
      confidence: latestSignal.confidence,
      pattern: latestSignal.pattern,
      description: latestSignal.description,
      recommendedPrice,
      priceReason,
      priceDifference: latestSignal.signal === 'BUY' 
        ? ((recommendedPrice - currentPrice) / currentPrice * 100)
        : ((currentPrice - recommendedPrice) / currentPrice * 100)
    }
  }, [candles, currentPrice])
  
  return (
    <div 
      className="w-full bg-gradient-to-br from-gray-900 to-black rounded-lg border border-gray-800 p-4 flex flex-col"
      style={{ height: `${height}px` }}
    >
      {/* Header */}
      <div className="text-center mb-4">
        <div className="text-sm font-semibold text-gray-300 mb-1">24 Hour Price Range</div>
        <div className="text-xs text-gray-500">Price Action</div>
      </div>
      
      {/* Price Scale Box */}
      <div className="flex-1 relative bg-gray-800/50 rounded-lg border border-gray-700 overflow-hidden">
        {/* High - Red at top */}
        <div 
          className="absolute left-0 right-0 flex items-center justify-between px-4 py-2 bg-red-500/20 border-b border-red-500/30"
          style={{ top: 0, height: 'auto' }}
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500"></div>
            <span className="text-xs font-medium text-gray-400">24h High</span>
          </div>
          <span className="text-lg font-bold text-red-400">
            {formatCurrency(high24h)}
          </span>
        </div>
        
        {/* Low - Green at bottom */}
        <div 
          className="absolute left-0 right-0 flex items-center justify-between px-4 py-2 bg-green-500/20 border-t border-green-500/30"
          style={{ bottom: 0, height: 'auto' }}
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className="text-xs font-medium text-gray-400">24h Low</span>
          </div>
          <span className="text-lg font-bold text-green-400">
            {formatCurrency(low24h)}
          </span>
        </div>
        
        {/* White line showing current price - moves with price action */}
        <div 
          className="absolute left-0 right-0 flex items-center justify-between px-4 py-2 bg-white/10 border-y border-white/30 z-10 transition-all duration-200"
          style={{ 
            top: `${currentPositionFromTop}%`,
            transform: 'translateY(-50%)',
            height: 'auto'
          }}
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-white"></div>
            <span className="text-xs font-medium text-gray-300">Current Price</span>
          </div>
          <span className="text-xl font-bold text-white">
            {formatCurrency(animatedPrice)}
          </span>
        </div>
        
        {/* White line indicator */}
        <div 
          className="absolute left-0 right-0 border-t-2 border-white z-10 transition-all duration-200"
          style={{ 
            top: `${currentPositionFromTop}%`,
            transform: 'translateY(-50%)'
          }}
        />
        
        {/* Price scale background gradient */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            background: `linear-gradient(to bottom, 
              rgba(239, 68, 68, 0.3) 0%, 
              rgba(239, 68, 68, 0.1) 20%,
              rgba(34, 197, 94, 0.1) 80%,
              rgba(34, 197, 94, 0.3) 100%)`
          }}
        />
      </div>
      
      {/* AI Recommendation Box */}
      {aiRecommendation && (
        <div className={`mt-4 p-4 rounded-lg border-2 ${
          aiRecommendation.signal === 'BUY'
            ? 'bg-green-500/10 border-green-500/50'
            : 'bg-red-500/10 border-red-500/50'
        }`}>
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-lg">🤖</span>
              <div>
                <div className={`text-sm font-bold ${
                  aiRecommendation.signal === 'BUY' ? 'text-green-400' : 'text-red-400'
                }`}>
                  AI {aiRecommendation.signal} Signal
                </div>
                <div className="text-xs text-gray-400">
                  {aiRecommendation.pattern.replace(/_/g, ' ')} • {aiRecommendation.confidence} Confidence
                </div>
              </div>
            </div>
            <div className={`px-2 py-1 rounded text-xs font-bold ${
              aiRecommendation.confidence === 'HIGH'
                ? aiRecommendation.signal === 'BUY' ? 'bg-green-500/30 text-green-300' : 'bg-red-500/30 text-red-300'
                : 'bg-yellow-500/30 text-yellow-300'
            }`}>
              {aiRecommendation.confidence}
            </div>
          </div>
          
          <div className="mt-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Recommended {aiRecommendation.signal} Price:</span>
              <span className={`text-lg font-bold ${
                aiRecommendation.signal === 'BUY' ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatCurrency(aiRecommendation.recommendedPrice)}
              </span>
            </div>
            
            <div className="text-xs text-gray-300 bg-gray-800/50 p-2 rounded">
              {aiRecommendation.priceReason}
            </div>
            
            {Math.abs(aiRecommendation.priceDifference) > 0.1 && (
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">
                  {aiRecommendation.signal === 'BUY' ? 'Below' : 'Above'} current:
                </span>
                <span className={aiRecommendation.signal === 'BUY' ? 'text-green-400' : 'text-red-400'}>
                  {aiRecommendation.priceDifference > 0 ? '+' : ''}{aiRecommendation.priceDifference.toFixed(2)}%
                </span>
              </div>
            )}
            
            <div className="text-xs text-gray-500 italic mt-2 pt-2 border-t border-gray-700">
              {aiRecommendation.description}
            </div>
          </div>
        </div>
      )}
      
      {/* Footer info */}
      <div className="mt-4 text-center">
        <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
          <span>Range: {formatCurrency(priceRange)}</span>
          <span>•</span>
          <span>{((priceRange / currentPrice) * 100).toFixed(2)}%</span>
        </div>
        {!aiRecommendation && (
          <div className="mt-2 text-xs text-gray-600">
            Analyzing patterns... No strong signal detected yet
          </div>
        )}
      </div>
    </div>
  )
}

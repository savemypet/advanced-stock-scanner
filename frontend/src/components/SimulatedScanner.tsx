import { useState, useEffect } from 'react'
import { Stock, Candle } from '../types'
import StockCard from './StockCard'
import StockDetailModal from './StockDetailModal'
import { RefreshCw } from 'lucide-react'

export default function SimulatedScanner() {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null)
  const [simulatedStocks, setSimulatedStocks] = useState<Stock[]>(generateSimulatedStocks())
  const [isLiveMode, setIsLiveMode] = useState(true)

  // Real-time updates - update every 3 seconds for visible demo movement
  useEffect(() => {
    if (!isLiveMode) return

    const interval = setInterval(() => {
      setSimulatedStocks(prevStocks => updateLiveStocks(prevStocks))
      
      // Update selected stock if modal is open
      setSelectedStock(prevSelected => {
        if (!prevSelected) return null
        const updatedStock = updateSingleStock(prevSelected)
        return updatedStock
      })
    }, 3000) // Update every 3 seconds - reasonable speed to watch

    return () => clearInterval(interval)
  }, [isLiveMode])

  type MovementPattern = 'uptrend' | 'downtrend' | 'breakout' | 'breakdown' | 'consolidation' | 'volatile' | 'pullback' | 'reversal'

  function updateLiveStocks(stocks: Stock[]): Stock[] {
    return stocks.map(stock => updateSingleStock(stock))
  }

  function updateSingleStock(stock: any): any {
    const pattern = stock.pattern || 'uptrend'
    const currentPrice = stock.price
    
    // Get realistic price change based on pattern
    let trend = 0
    let volatility = 0.008
    
    switch (pattern) {
      case 'uptrend':
        trend = 0.003 + Math.random() * 0.002
        volatility = 0.01
        break
      case 'downtrend':
        trend = -0.003 - Math.random() * 0.002
        volatility = 0.012
        break
      case 'breakout':
        trend = 0.006 + Math.random() * 0.004
        volatility = 0.015
        break
      case 'breakdown':
        trend = -0.008 - Math.random() * 0.003
        volatility = 0.016
        break
      case 'consolidation':
        trend = (Math.random() - 0.5) * 0.002
        volatility = 0.005
        break
      case 'volatile':
        trend = (Math.random() - 0.5) * 0.008
        volatility = 0.02
        break
      case 'pullback':
        trend = -0.003
        volatility = 0.012
        break
      case 'reversal':
        trend = 0.004 + Math.random() * 0.003
        volatility = 0.014
        break
    }
    
    const randomNoise = (Math.random() - 0.5) * volatility * 0.5
    const change = trend + randomNoise
    const newPrice = Math.max(0.01, currentPrice * (1 + change))
    
    const changeFromOpen = newPrice - stock.open
    const changePercent = (changeFromOpen / stock.open) * 100
    
    // Update high/low
    const newHigh = Math.max(stock.high, newPrice * (1 + Math.random() * 0.01))
    const newLow = Math.min(stock.low, newPrice * (1 - Math.random() * 0.01))
    
    // Volume increases with volatility
    const priceMove = Math.abs(newPrice - currentPrice) / currentPrice
    const volumeIncrease = Math.floor(stock.avgVolume * (0.8 + priceMove * 100) * (0.5 + Math.random()))
    const newVolume = stock.volume + volumeIncrease
    const volumeMultiplier = newVolume / stock.avgVolume
    
    // Update signal
    let signal: 'BUY' | 'SELL' | 'HOLD' = 'HOLD'
    if (changePercent > 10 && volumeMultiplier > 1.5) {
      signal = 'BUY'
    } else if (changePercent < -5 || volumeMultiplier < 0.7) {
      signal = 'SELL'
    }
    
    // Update chart data if exists
    let chartData = stock.chartData
    if (chartData) {
      const now = Date.now()
      
      // Define intervals in milliseconds (3 seconds per update, so scale accordingly)
      const intervals: Record<string, number> = {
        '1m': 60000,           // 1 minute = 20 updates (60s / 3s)
        '5m': 300000,          // 5 minutes = 100 updates
        '15m': 900000,         // 15 minutes = 300 updates
        '30m': 1800000,        // 30 minutes = 600 updates
        '1h': 3600000,         // 1 hour = 1200 updates
        '4h': 14400000,        // 4 hours = 4800 updates
        '24h': 86400000,       // 24 hours = 28800 updates
        '1week': 604800000,    // 1 week = 7 days
        '1month': 2592000000   // 1 month = 30 days
      }
      
      Object.keys(chartData).forEach(timeframe => {
        const candles = chartData[timeframe]
        const lastCandle = candles[candles.length - 1]
        const candleAge = now - (typeof lastCandle.time === 'number' ? lastCandle.time : Date.now())
        const interval = intervals[timeframe] || 60000
        
        // Check if we should add a NEW candle or UPDATE the current one
        if (candleAge >= interval) {
          // Time to create a NEW candle
          const newCandle: Candle = {
            time: now,
            open: lastCandle.close,
            high: newPrice,
            low: newPrice,
            close: newPrice,
            volume: volumeIncrease
          }
          
          // Add candle and remove oldest to maintain count
          const maxCandles = timeframe === '1m' ? 60 : 
                            timeframe === '5m' ? 60 : 
                            timeframe === '15m' ? 60 : 
                            timeframe === '30m' ? 60 : 
                            timeframe === '1h' ? 24 : 
                            timeframe === '4h' ? 42 :
                            timeframe === '24h' ? 90 :
                            timeframe === '1week' ? 52 :
                            timeframe === '1month' ? 12 : 60
          chartData[timeframe] = [...candles.slice(-(maxCandles - 1)), newCandle]
        } else {
          // UPDATE the current candle with new price data
          const updatedCandle: Candle = {
            ...lastCandle,
            high: Math.max(lastCandle.high, newPrice),
            low: Math.min(lastCandle.low, newPrice),
            close: newPrice,
            volume: lastCandle.volume + volumeIncrease
          }
          
          // Replace the last candle with updated one
          chartData[timeframe] = [...candles.slice(0, -1), updatedCandle]
        }
      })
    }
    
    return {
      ...stock,
      price: newPrice,
      high: newHigh,
      low: newLow,
      volume: newVolume,
      volumeMultiplier,
      changePercent,
      changeAmount: changeFromOpen,
      signal,
      updatedAt: Date.now(),
      chartData
    }
  }

  function generateSimulatedStocks(): Stock[] {
    const now = Date.now()
    
    return [
      {
        symbol: 'DEMO-BREAKOUT',
        name: 'Breakout Pattern → Explosive Move',
        price: 4.82,
        open: 3.15,
        high: 5.10,
        low: 3.05,
        volume: 45600000,
        avgVolume: 5800000,
        float: 6200000,
        marketCap: 29884000,
        changePercent: 53.02,
        volumeMultiplier: 7.86,
        signal: 'BUY',
        isHot: true,
        hasNews: true,
        newsCount: 5,
        pattern: 'breakout' as MovementPattern,
        updatedAt: now
      },
      {
        symbol: 'DEMO-BREAKDOWN',
        name: 'Breakdown → Sharp Drop',
        price: 0.68,
        open: 0.95,
        high: 0.98,
        low: 0.65,
        volume: 22300000,
        avgVolume: 3200000,
        float: 12000000,
        marketCap: 8160000,
        changePercent: -28.42,
        volumeMultiplier: 6.97,
        signal: 'SELL',
        isHot: true,
        hasNews: false,
        pattern: 'breakdown' as MovementPattern,
        updatedAt: now
      },
      {
        symbol: 'DEMO-UPTREND',
        name: 'Steady Uptrend → Higher Highs',
        price: 2.45,
        open: 1.85,
        high: 2.55,
        low: 1.80,
        volume: 15750000,
        avgVolume: 2500000,
        float: 8500000,
        marketCap: 20825000,
        changePercent: 32.43,
        volumeMultiplier: 6.3,
        signal: 'BUY',
        isHot: true,
        hasNews: true,
        newsCount: 3,
        pattern: 'uptrend' as MovementPattern,
        updatedAt: now
      },
      {
        symbol: 'DEMO-PULLBACK',
        name: 'Rally → Healthy Pullback',
        price: 3.67,
        open: 3.20,
        high: 3.85,
        low: 3.10,
        volume: 18200000,
        avgVolume: 2900000,
        float: 9800000,
        marketCap: 35966000,
        changePercent: 14.69,
        volumeMultiplier: 6.28,
        signal: 'BUY',
        isHot: true,
        hasNews: true,
        newsCount: 2,
        pattern: 'pullback' as MovementPattern,
        updatedAt: now
      },
      {
        symbol: 'DEMO-REVERSAL',
        name: 'Downtrend → Bullish Reversal',
        price: 0.18,
        open: 0.08,
        high: 0.22,
        low: 0.07,
        volume: 125000000,
        avgVolume: 18000000,
        float: 85000000,
        marketCap: 15300000,
        changePercent: 125.00,
        volumeMultiplier: 6.94,
        signal: 'BUY',
        isHot: true,
        hasNews: true,
        newsCount: 4,
        pattern: 'reversal' as MovementPattern,
        updatedAt: now
      },
      {
        symbol: 'DEMO-CONSOL',
        name: 'Tight Consolidation → Coiling',
        price: 1.23,
        open: 1.20,
        high: 1.28,
        low: 1.18,
        volume: 8900000,
        avgVolume: 1600000,
        float: 15000000,
        marketCap: 18450000,
        changePercent: 2.50,
        volumeMultiplier: 5.56,
        signal: 'HOLD',
        isHot: false,
        hasNews: false,
        pattern: 'consolidation' as MovementPattern,
        updatedAt: now
      },
      {
        symbol: 'DEMO-VOLATILE',
        name: 'High Volatility → Erratic Swings',
        price: 1.52,
        open: 1.45,
        high: 1.78,
        low: 1.22,
        volume: 32100000,
        avgVolume: 4500000,
        float: 11200000,
        marketCap: 17024000,
        changePercent: 4.83,
        volumeMultiplier: 7.13,
        signal: 'HOLD',
        isHot: true,
        hasNews: true,
        newsCount: 1,
        pattern: 'volatile' as MovementPattern,
        updatedAt: now
      },
      {
        symbol: 'DEMO-DOWNTREND',
        name: 'Bearish Downtrend → Lower Lows',
        price: 0.92,
        open: 1.15,
        high: 1.18,
        low: 0.88,
        volume: 19400000,
        avgVolume: 2800000,
        float: 13500000,
        marketCap: 12420000,
        changePercent: -20.00,
        volumeMultiplier: 6.93,
        signal: 'SELL',
        isHot: true,
        hasNews: false,
        pattern: 'downtrend' as MovementPattern,
        updatedAt: now
      }
    ]
  }

  function generateSimulatedChartData(stock: any): { [key: string]: Candle[] } {
    const basePrice = stock.open
    const pattern = stock.pattern || 'uptrend'
    
    // Generate realistic patterns for each timeframe
    const data1m = generateRealisticCandles(60, basePrice, pattern, stock.volume, '1m')
    const data5m = generateRealisticCandles(60, basePrice, pattern, stock.volume, '5m')
    const data15m = generateRealisticCandles(60, basePrice, pattern, stock.volume, '15m')
    const data30m = generateRealisticCandles(60, basePrice, pattern, stock.volume, '30m')
    const data1h = generateRealisticCandles(24, basePrice, pattern, stock.volume, '1h')
    const data4h = generateRealisticCandles(42, basePrice * 0.9, pattern, stock.volume, '4h')
    const data24h = generateRealisticCandles(90, basePrice * 0.8, pattern, stock.volume, '24h')
    const data1week = generateRealisticCandles(52, basePrice * 0.7, pattern, stock.volume, '1week')
    const data1month = generateRealisticCandles(12, basePrice * 0.6, pattern, stock.volume, '1month')
    
    return {
      '1m': data1m,
      '5m': data5m,
      '15m': data15m,
      '30m': data30m,
      '1h': data1h,
      '4h': data4h,
      '24h': data24h,
      '1week': data1week,
      '1month': data1month
    }
  }

  function generateRealisticCandles(
    count: number,
    basePrice: number,
    pattern: MovementPattern,
    totalVolume: number,
    timeframe: '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '24h' | '1week' | '1month'
  ): Candle[] {
    const candles: Candle[] = []
    let currentPrice = basePrice
    const avgVolume = totalVolume / count
    
    for (let i = 0; i < count; i++) {
      const progress = i / count
      
      let trend = 0
      let volatility = 0.008
      let volumeMultiplier = 1
      
      switch (pattern) {
        case 'uptrend':
          trend = 0.003 + (progress * 0.002)
          volatility = 0.01
          volumeMultiplier = 1 + (progress * 0.5)
          break
          
        case 'downtrend':
          trend = -0.003 - (progress * 0.001)
          volatility = 0.012
          volumeMultiplier = 1 + (progress * 0.3)
          break
          
        case 'breakout':
          if (progress < 0.6) {
            trend = (Math.random() - 0.5) * 0.001
            volatility = 0.005
            volumeMultiplier = 0.8
          } else {
            trend = 0.008 + (progress - 0.6) * 0.01
            volatility = 0.015
            volumeMultiplier = 2 + (progress - 0.6) * 3
          }
          break
          
        case 'breakdown':
          if (progress < 0.5) {
            trend = (Math.random() - 0.5) * 0.001
            volatility = 0.006
            volumeMultiplier = 0.9
          } else {
            trend = -0.01 - (progress - 0.5) * 0.008
            volatility = 0.018
            volumeMultiplier = 1.5 + (progress - 0.5) * 2
          }
          break
          
        case 'consolidation':
          trend = (Math.random() - 0.5) * 0.0015
          volatility = 0.004 + Math.sin(progress * Math.PI * 4) * 0.002
          volumeMultiplier = 0.7 + Math.random() * 0.3
          break
          
        case 'volatile':
          trend = Math.sin(progress * Math.PI * 3) * 0.006
          volatility = 0.02 + Math.random() * 0.015
          volumeMultiplier = 1.2 + Math.random() * 0.8
          break
          
        case 'pullback':
          if (progress < 0.7) {
            trend = 0.004
            volatility = 0.01
            volumeMultiplier = 1.3
          } else {
            trend = -0.006
            volatility = 0.014
            volumeMultiplier = 0.9
          }
          break
          
        case 'reversal':
          if (progress < 0.5) {
            trend = -0.004
            volatility = 0.012
            volumeMultiplier = 1.1
          } else {
            trend = 0.005 + (progress - 0.5) * 0.003
            volatility = 0.015
            volumeMultiplier = 1.5 + (progress - 0.5) * 1.5
          }
          break
      }
      
      const open = currentPrice
      const randomNoise = (Math.random() - 0.5) * volatility * 0.5
      const change = trend + randomNoise
      const close = open * (1 + change)
      
      const wickSize = volatility * (0.3 + Math.random() * 0.7)
      const high = Math.max(open, close) * (1 + wickSize)
      const low = Math.min(open, close) * (1 - wickSize)
      
      const priceMove = Math.abs(close - open) / open
      const volumeBoost = 1 + (priceMove * 50)
      const volume = Math.floor(avgVolume * volumeMultiplier * volumeBoost * (0.7 + Math.random() * 0.6))
      
      const timeMultiplier = timeframe === '1month' ? 30 * 24 * 60 * 60 * 1000 :
                            timeframe === '1week' ? 7 * 24 * 60 * 60 * 1000 :
                            timeframe === '24h' ? 24 * 60 * 60 * 1000 :
                            timeframe === '4h' ? 4 * 60 * 60 * 1000 :
                            timeframe === '1h' ? 60 * 60 * 1000 :
                            timeframe === '30m' ? 30 * 60 * 1000 :
                            timeframe === '15m' ? 15 * 60 * 1000 :
                            timeframe === '5m' ? 5 * 60 * 1000 : 60 * 1000
      const time = Date.now() - ((count - i) * timeMultiplier)
      
      candles.push({
        time,
        open: Math.max(0.01, open),
        high: Math.max(0.01, high),
        low: Math.max(0.01, low),
        close: Math.max(0.01, close),
        volume
      })
      
      currentPrice = close
    }
    
    // Calculate moving averages
    candles.forEach((candle, index) => {
      if (index >= 19) {
        const ma20Sum = candles.slice(index - 19, index + 1).reduce((sum, c) => sum + c.close, 0)
        candle.ma20 = ma20Sum / 20
      }
      if (index >= 49) {
        const ma50Sum = candles.slice(index - 49, index + 1).reduce((sum, c) => sum + c.close, 0)
        candle.ma50 = ma50Sum / 50
      }
      if (index >= 199 && timeframe === '24h') {
        const ma200Sum = candles.slice(index - 199, index + 1).reduce((sum, c) => sum + c.close, 0)
        candle.ma200 = ma200Sum / 200
      }
    })
    
    return candles
  }

  const handleStockClick = (stock: Stock) => {
    // Generate chart data on demand
    const chartData = generateSimulatedChartData(stock)
    const stockWithCharts = { ...stock, chartData }
    setSelectedStock(stockWithCharts as any)
  }

  const handleRefresh = () => {
    setSimulatedStocks(generateSimulatedStocks())
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
              🎮 Simulated Scanner Demo
              {isLiveMode && (
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/20 border border-green-500/30 rounded text-xs text-green-400">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  LIVE
                </span>
              )}
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              {isLiveMode 
                ? '📡 Live updating every minute - watch the charts move in real-time!'
                : 'Click any stock to see Bookmap-style volume charts'
              }
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsLiveMode(!isLiveMode)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isLiveMode 
                  ? 'bg-green-500/20 hover:bg-green-500/30 text-green-300 border border-green-500/30' 
                  : 'bg-gray-500/20 hover:bg-gray-500/30 text-gray-300 border border-gray-500/30'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${isLiveMode ? 'bg-green-500' : 'bg-gray-500'}`}></span>
              {isLiveMode ? 'Live' : 'Paused'}
            </button>
            <button
              onClick={handleRefresh}
              className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-xs text-muted-foreground mb-1">📊 Features Demo</div>
          <div className="text-sm font-semibold">Bookmap Volume</div>
          <div className="text-xs text-muted-foreground mt-1">
            ✅ Buy/Sell Split • ✅ VWAP • ✅ Delta
          </div>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-3">
          <div className="text-xs text-muted-foreground mb-1">🎯 Test Scenarios</div>
          <div className="text-sm font-semibold">6 Stock Patterns</div>
          <div className="text-xs text-muted-foreground mt-1">
            Bullish • Bearish • High Vol • Consolidation
          </div>
        </div>
        
        <div className={`bg-card border rounded-lg p-3 ${
          isLiveMode ? 'border-green-500/30 bg-green-500/5' : 'border-border'
        }`}>
          <div className="text-xs text-muted-foreground mb-1">⚡ Live Simulation</div>
          <div className="text-sm font-semibold flex items-center gap-2">
            {isLiveMode && <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>}
            Auto-Updating
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {isLiveMode ? 'Updates every 3 seconds - charts show proper timeframe intervals' : 'Paused - click Live to resume'}
          </div>
        </div>
      </div>

      {/* Stock List */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-foreground">Demo Stocks:</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {simulatedStocks.map((stock) => (
            <div key={stock.symbol} onClick={() => handleStockClick(stock)}>
              <StockCard stock={stock} />
            </div>
          ))}
        </div>
      </div>

      {/* Stock Detail Modal */}
      {selectedStock && (
        <StockDetailModal
          stock={selectedStock}
          onClose={() => setSelectedStock(null)}
        />
      )}
    </div>
  )
}

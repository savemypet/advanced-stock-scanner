import { useMemo } from 'react'
import { Candle } from '../types'
import {
  ComposedChart,
  Bar,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Label,
  ReferenceDot,
  ReferenceLine,
  ReferenceArea,
} from 'recharts'
import { detectPatterns } from '../utils/candlestickPatterns'

interface TradingViewChartProps {
  candles: Candle[]
  height?: number
}

export default function TradingViewChart({ candles, height = 600 }: TradingViewChartProps) {
  // Calculate previous 24h high/low resistance levels
  const resistanceLevels = useMemo(() => {
    if (!candles || candles.length === 0) return null
    
    // Get last 24 hours of data (or all if less than 24h)
    const now = new Date().getTime()
    const twentyFourHoursAgo = now - (24 * 60 * 60 * 1000)
    
    const last24hCandles = candles.filter(candle => {
      const candleTime = new Date(candle.time).getTime()
      return candleTime >= twentyFourHoursAgo
    })
    
    if (last24hCandles.length === 0) return null
    
    // Calculate 24h high and low
    const high24h = Math.max(...last24hCandles.map(c => c.high))
    const low24h = Math.min(...last24hCandles.map(c => c.low))
    
    // Current price (latest close)
    const currentPrice = candles[candles.length - 1]?.close || 0
    
    // Calculate support/resistance zones (with some buffer)
    const priceRange = high24h - low24h
    const zoneBuffer = priceRange * 0.02 // 2% buffer for zone thickness
    
    return {
      high24h,
      low24h,
      currentPrice,
      highZone: {
        top: high24h + zoneBuffer,
        bottom: high24h - zoneBuffer,
        middle: high24h,
      },
      lowZone: {
        top: low24h + zoneBuffer,
        bottom: low24h - zoneBuffer,
        middle: low24h,
      },
      // Additional resistance levels based on Fibonacci retracements
      fib618: low24h + (high24h - low24h) * 0.618,
      fib50: low24h + (high24h - low24h) * 0.5,
      fib382: low24h + (high24h - low24h) * 0.382,
    }
  }, [candles])
  
  const chartData = useMemo(() => {
    if (!candles || candles.length === 0) {
      return { mainData: [], volumeData: [], signals: [], trendBands: [] }
    }
    
    // Calculate moving averages and trend bands
    const mainData = candles.map((candle, index) => {
      const date = new Date(candle.time)
      const isGreen = candle.close >= candle.open
      
      // Calculate EMA for trend bands (Ichimoku-style cloud)
      const period9 = Math.max(0, index - 8)
      const period26 = Math.max(0, index - 25)
      const period52 = Math.max(0, index - 51)
      
      const slice9 = candles.slice(period9, index + 1)
      const slice26 = candles.slice(period26, index + 1)
      
      // Tenkan-sen (Conversion Line) - 9 period
      const tenkan = slice9.length > 0 
        ? (Math.max(...slice9.map(c => c.high)) + Math.min(...slice9.map(c => c.low))) / 2
        : null
      
      // Kijun-sen (Base Line) - 26 period
      const kijun = slice26.length > 0
        ? (Math.max(...slice26.map(c => c.high)) + Math.min(...slice26.map(c => c.low))) / 2
        : null
      
      // Senkou Span A (Leading Span A) - average of tenkan and kijun, shifted forward
      const senkouA = tenkan && kijun ? (tenkan + kijun) / 2 : null
      
      // Senkou Span B (Leading Span B) - 52 period average, shifted forward
      const slice52 = candles.slice(period52, index + 1)
      const senkouB = slice52.length > 0
        ? (Math.max(...slice52.map(c => c.high)) + Math.min(...slice52.map(c => c.low))) / 2
        : null
      
      return {
        time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        fullTime: candle.time,
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        open: candle.open,
        close: candle.close,
        high: candle.high,
        low: candle.low,
        volume: candle.volume,
        isGreen,
        bodyTop: Math.max(candle.open, candle.close),
        bodyBottom: Math.min(candle.open, candle.close),
        bodyHeight: Math.abs(candle.close - candle.open),
        wickTop: candle.high,
        wickBottom: candle.low,
        ma20: candle.ma20,
        ma50: candle.ma50,
        ma200: candle.ma200,
        tenkan,
        kijun,
        senkouA,
        senkouB,
        cloudColor: senkouA && senkouB ? (senkouA > senkouB ? 'bullish' : 'bearish') : null,
      }
    })
    
    // Detect patterns for BUY/SELL signals
    const patterns = detectPatterns(candles)
    const signals = patterns.map(pattern => {
      const candle = candles[pattern.candleIndex]
      const data = mainData[pattern.candleIndex]
      return {
        time: data?.time || '',
        fullTime: candle.time,
        price: pattern.signal === 'BUY' ? candle.low * 0.998 : candle.high * 1.002,
        type: pattern.signal,
        pattern: pattern.pattern.replace(/_/g, ' '),
        confidence: pattern.confidence,
        index: pattern.candleIndex,
      }
    })
    
    // Prepare volume data
    const maxVolume = Math.max(...candles.map(c => c.volume))
    const volumeData = candles.map((candle, index) => {
      const isGreen = candle.close >= candle.open
      const priceRange = candle.high - candle.low
      const closePosition = priceRange > 0 ? (candle.close - candle.low) / priceRange : 0.5
      
      const buyVolume = isGreen ? candle.volume * closePosition : candle.volume * (1 - closePosition) * 0.3
      const sellVolume = !isGreen ? candle.volume * (1 - closePosition) : candle.volume * closePosition * 0.3
      
      return {
        time: mainData[index].time,
        volume: candle.volume,
        buyVolume,
        sellVolume,
        isGreen,
        intensity: candle.volume / maxVolume,
      }
    })
    
    return { mainData, volumeData, signals }
  }, [candles])

  const { mainData, volumeData, signals } = chartData

  const priceRange = useMemo(() => {
    if (!mainData || mainData.length === 0) {
      return { min: 0, max: 100 }
    }
    const prices = mainData.flatMap(d => [d.high, d.low, d.senkouA, d.senkouB].filter(Boolean))
    const min = Math.min(...prices)
    const max = Math.max(...prices)
    const padding = (max - min) * 0.1
    return {
      min: min - padding,
      max: max + padding,
    }
  }, [mainData])

  if (!candles || candles.length === 0) {
    return (
      <div className="w-full flex items-center justify-center text-muted-foreground" style={{ height: `${height}px` }}>
        <p>No chart data available</p>
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-black/95 border border-gray-700 rounded-lg p-3 shadow-xl">
          <p className="text-xs text-gray-400 mb-2">{data.date} {data.time}</p>
          <div className="space-y-1">
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
              <span className="text-gray-400">O:</span>
              <span className="text-white font-mono">${data.open?.toFixed(2)}</span>
              <span className="text-gray-400">H:</span>
              <span className="text-green-400 font-mono">${data.high?.toFixed(2)}</span>
              <span className="text-gray-400">L:</span>
              <span className="text-red-400 font-mono">${data.low?.toFixed(2)}</span>
              <span className="text-gray-400">C:</span>
              <span className={`font-mono ${data.isGreen ? 'text-green-400' : 'text-red-400'}`}>
                ${data.close?.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  const VolumeTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-black/95 border border-gray-700 rounded-lg p-3 shadow-xl">
          <p className="text-xs text-gray-400 mb-2">Volume</p>
          <div className="space-y-1">
            <p className="text-sm text-white font-mono">
              {(data.volume / 1000000).toFixed(2)}M
            </p>
            <div className="flex gap-3 text-xs">
              <span className="text-green-400">Buy: {(data.buyVolume / 1000000).toFixed(2)}M</span>
              <span className="text-red-400">Sell: {(data.sellVolume / 1000000).toFixed(2)}M</span>
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  // Custom shape for candlestick wicks
  const CandleWick = (props: any) => {
    const { x, y, width, height, payload, wickTop, wickBottom } = props
    if (!payload) return null
    
    const centerX = x + width / 2
    
    return (
      <g>
        {/* Wick line */}
        <line
          x1={centerX}
          y1={y}
          x2={centerX}
          y2={y + height}
          stroke={payload.isGreen ? '#22c55e' : '#ef4444'}
          strokeWidth={1.5}
        />
      </g>
    )
  }

  const mainChartHeight = height * 0.7
  const volumeChartHeight = height * 0.3

  return (
    <div className="w-full bg-[#0a0a0a] rounded-lg" style={{ height: `${height}px` }}>
      {/* Resistance Levels Legend */}
      {resistanceLevels && (
        <div className="px-4 py-2 border-b border-gray-800 bg-black/50">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-4">
              <span className="text-gray-400 font-semibold">📊 24H LEVELS:</span>
              <div className="flex items-center gap-1">
                <div className="w-3 h-0.5 bg-red-500"></div>
                <span className="text-red-400">High: ${resistanceLevels.high24h.toFixed(2)}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-0.5 bg-green-500"></div>
                <span className="text-green-400">Low: ${resistanceLevels.low24h.toFixed(2)}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-0.5 bg-yellow-500"></div>
                <span className="text-yellow-400">Mid: ${resistanceLevels.fib50.toFixed(2)}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-white"></div>
                <span className="text-white font-bold">Current: ${resistanceLevels.currentPrice.toFixed(2)}</span>
              </div>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className={`font-semibold ${
                resistanceLevels.currentPrice > resistanceLevels.fib50 
                  ? 'text-green-400' 
                  : 'text-red-400'
              }`}>
                {resistanceLevels.currentPrice > resistanceLevels.fib50 ? '📈 Above Mid' : '📉 Below Mid'}
              </span>
              <span className="text-gray-500">|</span>
              <span className="text-orange-400">
                Range: ${(resistanceLevels.high24h - resistanceLevels.low24h).toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      )}
      
      {/* Main Price Chart with Trend Bands */}
      <div style={{ height: `${mainChartHeight}px` }} className="relative">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart 
            data={mainData}
            margin={{ top: 40, right: 20, left: 10, bottom: 0 }}
          >
            <defs>
              {/* Bullish cloud gradient (green) */}
              <linearGradient id="bullishCloud" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0.1}/>
              </linearGradient>
              
              {/* Bearish cloud gradient (red) */}
              <linearGradient id="bearishCloud" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
              </linearGradient>
              
              {/* Gradient for volume bars */}
              <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#22c55e" stopOpacity={0.8}/>
                <stop offset="100%" stopColor="#22c55e" stopOpacity={0.3}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid 
              strokeDasharray="1 3" 
              stroke="#1f1f1f" 
              vertical={false}
            />
            
            <XAxis 
              dataKey="time" 
              stroke="#4a4a4a"
              tick={{ fill: '#888', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#2a2a2a' }}
              interval="preserveStartEnd"
            />
            
            <YAxis 
              domain={[priceRange.min, priceRange.max]}
              stroke="#4a4a4a"
              tick={{ fill: '#888', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#2a2a2a' }}
              orientation="right"
              tickFormatter={(value) => `$${value.toFixed(2)}`}
            />
            
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#4a4a4a', strokeDasharray: '3 3' }} />

            {/* Ichimoku Cloud - Senkou Span A and B */}
            <Area
              type="monotone"
              dataKey="senkouA"
              stroke="none"
              fill="url(#bullishCloud)"
              fillOpacity={1}
              connectNulls
              isAnimationActive={false}
            />
            
            <Area
              type="monotone"
              dataKey="senkouB"
              stroke="none"
              fill="url(#bearishCloud)"
              fillOpacity={1}
              connectNulls
              isAnimationActive={false}
            />

            {/* Moving Average Lines */}
            <Line 
              type="monotone" 
              dataKey="ma20" 
              stroke="#3b82f6" 
              strokeWidth={1.5}
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
            
            <Line 
              type="monotone" 
              dataKey="ma50" 
              stroke="#a855f7" 
              strokeWidth={1.5}
              dot={false}
              connectNulls
              isAnimationActive={false}
            />

            {/* Tenkan and Kijun lines (Ichimoku) */}
            <Line 
              type="monotone" 
              dataKey="tenkan" 
              stroke="#22c55e" 
              strokeWidth={1}
              strokeDasharray="2 2"
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
            
            <Line 
              type="monotone" 
              dataKey="kijun" 
              stroke="#ef4444" 
              strokeWidth={1}
              strokeDasharray="2 2"
              dot={false}
              connectNulls
              isAnimationActive={false}
            />

            {/* 24H HIGH/LOW RESISTANCE LEVELS */}
            {resistanceLevels && (
              <>
                {/* 24H High Resistance Zone (Red Box) */}
                <ReferenceArea
                  y1={resistanceLevels.highZone.top}
                  y2={resistanceLevels.highZone.bottom}
                  fill="#ef4444"
                  fillOpacity={0.15}
                  stroke="#ef4444"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  ifOverflow="extendDomain"
                />
                
                {/* 24H High Line */}
                <ReferenceLine
                  y={resistanceLevels.high24h}
                  stroke="#ef4444"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  ifOverflow="extendDomain"
                >
                  <Label 
                    value={`24H HIGH: $${resistanceLevels.high24h.toFixed(2)}`}
                    position="right"
                    fill="#ef4444"
                    fontSize={11}
                    fontWeight="bold"
                    style={{ 
                      backgroundColor: 'rgba(0,0,0,0.8)',
                      padding: '2px 6px',
                      borderRadius: '3px'
                    }}
                  />
                </ReferenceLine>

                {/* 24H Low Support Zone (Green Box) */}
                <ReferenceArea
                  y1={resistanceLevels.lowZone.top}
                  y2={resistanceLevels.lowZone.bottom}
                  fill="#22c55e"
                  fillOpacity={0.15}
                  stroke="#22c55e"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  ifOverflow="extendDomain"
                />
                
                {/* 24H Low Line */}
                <ReferenceLine
                  y={resistanceLevels.low24h}
                  stroke="#22c55e"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  ifOverflow="extendDomain"
                >
                  <Label 
                    value={`24H LOW: $${resistanceLevels.low24h.toFixed(2)}`}
                    position="right"
                    fill="#22c55e"
                    fontSize={11}
                    fontWeight="bold"
                    style={{ 
                      backgroundColor: 'rgba(0,0,0,0.8)',
                      padding: '2px 6px',
                      borderRadius: '3px'
                    }}
                  />
                </ReferenceLine>

                {/* Fibonacci 61.8% Level (Key Resistance) */}
                <ReferenceLine
                  y={resistanceLevels.fib618}
                  stroke="#f59e0b"
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  ifOverflow="extendDomain"
                >
                  <Label 
                    value={`FIB 61.8%: $${resistanceLevels.fib618.toFixed(2)}`}
                    position="right"
                    fill="#f59e0b"
                    fontSize={10}
                  />
                </ReferenceLine>

                {/* Fibonacci 50% Level (Mid-Range) */}
                <ReferenceLine
                  y={resistanceLevels.fib50}
                  stroke="#eab308"
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  ifOverflow="extendDomain"
                >
                  <Label 
                    value={`MID: $${resistanceLevels.fib50.toFixed(2)}`}
                    position="right"
                    fill="#eab308"
                    fontSize={10}
                  />
                </ReferenceLine>

                {/* Fibonacci 38.2% Level (Support) */}
                <ReferenceLine
                  y={resistanceLevels.fib382}
                  stroke="#84cc16"
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  ifOverflow="extendDomain"
                >
                  <Label 
                    value={`FIB 38.2%: $${resistanceLevels.fib382.toFixed(2)}`}
                    position="right"
                    fill="#84cc16"
                    fontSize={10}
                  />
                </ReferenceLine>

                {/* Current Price Line (White Dotted) */}
                <ReferenceLine
                  y={resistanceLevels.currentPrice}
                  stroke="#ffffff"
                  strokeWidth={2}
                  strokeDasharray="1 1"
                  ifOverflow="extendDomain"
                >
                  <Label 
                    value={`CURRENT: $${resistanceLevels.currentPrice.toFixed(2)}`}
                    position="right"
                    fill="#ffffff"
                    fontSize={11}
                    fontWeight="bold"
                    style={{ 
                      backgroundColor: 'rgba(0,0,0,0.9)',
                      padding: '2px 6px',
                      borderRadius: '3px'
                    }}
                  />
                </ReferenceLine>
              </>
            )}

            {/* Candlestick bodies */}
            <Bar 
              dataKey="bodyHeight" 
              fill="#22c55e"
              maxBarSize={12}
              shape={(props: any) => {
                const { x, y, width, height, payload } = props
                if (!payload) return null
                
                const centerX = x + width / 2
                const wickColor = payload.isGreen ? '#22c55e' : '#ef4444'
                const bodyColor = payload.isGreen ? '#22c55e' : '#ef4444'
                
                // Calculate wick positions
                const yHigh = y - ((payload.wickTop - payload.bodyTop) / (priceRange.max - priceRange.min)) * mainChartHeight * 0.7
                const yLow = y + height + ((payload.bodyBottom - payload.wickBottom) / (priceRange.max - priceRange.min)) * mainChartHeight * 0.7
                
                return (
                  <g>
                    {/* Upper wick */}
                    <line
                      x1={centerX}
                      y1={yHigh}
                      x2={centerX}
                      y2={y}
                      stroke={wickColor}
                      strokeWidth={1}
                    />
                    
                    {/* Body */}
                    <rect
                      x={x + 1}
                      y={y}
                      width={Math.max(1, width - 2)}
                      height={Math.max(1, height)}
                      fill={bodyColor}
                      stroke={bodyColor}
                      strokeWidth={1}
                    />
                    
                    {/* Lower wick */}
                    <line
                      x1={centerX}
                      y1={y + height}
                      x2={centerX}
                      y2={yLow}
                      stroke={wickColor}
                      strokeWidth={1}
                    />
                  </g>
                )
              }}
            />

            {/* BUY/SELL Signal Labels - TradingView Style */}
            {signals.map((signal, idx) => {
              const dataPoint = mainData.find(d => d.time === signal.time)
              if (!dataPoint) return null
              
              const isBuy = signal.type === 'BUY'
              const yPos = isBuy ? signal.price : signal.price
              
              return (
                <ReferenceDot
                  key={`signal-${idx}`}
                  x={signal.time}
                  y={yPos}
                  r={0}
                  shape={(props: any) => {
                    const { cx, cy } = props
                    if (!cx || !cy) return null
                    
                    const label = signal.type
                    const boxWidth = 38
                    const boxHeight = 18
                    const bgColor = isBuy ? '#10b981' : '#dc2626'
                    
                    return (
                      <g>
                        {/* Label box */}
                        <rect
                          x={cx - boxWidth / 2}
                          y={cy - (isBuy ? boxHeight + 8 : -8)}
                          width={boxWidth}
                          height={boxHeight}
                          fill={bgColor}
                          rx={3}
                          ry={3}
                        />
                        
                        {/* Label text */}
                        <text
                          x={cx}
                          y={cy - (isBuy ? boxHeight / 2 + 4 : -boxHeight / 2 - 4)}
                          textAnchor="middle"
                          fill="white"
                          fontSize={11}
                          fontWeight="700"
                          dominantBaseline="middle"
                        >
                          {label}
                        </text>
                        
                        {/* Arrow pointer */}
                        <polygon
                          points={isBuy 
                            ? `${cx},${cy - 4} ${cx - 4},${cy - 8} ${cx + 4},${cy - 8}`
                            : `${cx},${cy + 4} ${cx - 4},${cy + 8} ${cx + 4},${cy + 8}`
                          }
                          fill={bgColor}
                        />
                      </g>
                    )
                  }}
                />
              )
            })}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Chart */}
      <div style={{ height: `${volumeChartHeight}px` }} className="border-t border-gray-800">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart 
            data={volumeData}
            margin={{ top: 0, right: 20, left: 10, bottom: 10 }}
          >
            <CartesianGrid 
              strokeDasharray="1 3" 
              stroke="#1f1f1f" 
              vertical={false}
            />
            
            <XAxis 
              dataKey="time" 
              stroke="#4a4a4a"
              tick={{ fill: '#888', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#2a2a2a' }}
              interval="preserveStartEnd"
            />
            
            <YAxis 
              stroke="#4a4a4a"
              tick={{ fill: '#888', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#2a2a2a' }}
              orientation="right"
              tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
            />
            
            <Tooltip content={<VolumeTooltip />} cursor={false} />

            {/* Buy Volume (Green) */}
            <Bar 
              dataKey="buyVolume" 
              stackId="volume"
              fill="#22c55e"
              radius={[0, 0, 0, 0]}
            >
              {volumeData.map((entry, index) => (
                <Cell 
                  key={`buy-${index}`}
                  fill={`rgba(34, 197, 94, ${0.4 + entry.intensity * 0.5})`}
                />
              ))}
            </Bar>

            {/* Sell Volume (Red) */}
            <Bar 
              dataKey="sellVolume" 
              stackId="volume"
              fill="#ef4444"
              radius={[2, 2, 0, 0]}
            >
              {volumeData.map((entry, index) => (
                <Cell 
                  key={`sell-${index}`}
                  fill={`rgba(239, 68, 68, ${0.4 + entry.intensity * 0.5})`}
                />
              ))}
            </Bar>
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

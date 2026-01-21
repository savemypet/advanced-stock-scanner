import { useMemo } from 'react'
import { Candle } from '../types'
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Scatter,
  ZAxis,
  ReferenceLine,
  ReferenceArea,
  Label,
} from 'recharts'
import { detectPatterns, getLatestSignal, PatternSignal } from '../utils/candlestickPatterns'

interface CandlestickOnlyChartProps {
  candles: Candle[]
  height?: number
  onPatternDetected?: (pattern: PatternSignal | null) => void
}

export default function CandlestickOnlyChart({ candles, height = 400, onPatternDetected }: CandlestickOnlyChartProps) {
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
  
  // Detect all buy/sell signals from patterns
  const buySellSignals = useMemo(() => {
    if (!candles || candles.length === 0) return []
    
    const patterns = detectPatterns(candles)
    const signals: Array<{ index: number; signal: 'BUY' | 'SELL'; price: number; pattern: string; confidence: string }> = []
    
    patterns.forEach(pattern => {
      if (pattern.confidence === 'HIGH' || pattern.confidence === 'MEDIUM') {
        const candleIndex = pattern.candleIndex
        if (candleIndex < candles.length) {
          const candle = candles[candleIndex]
          signals.push({
            index: candleIndex,
            signal: pattern.signal,
            price: pattern.signal === 'BUY' ? candle.low : candle.high, // Buy at low, sell at high
            pattern: pattern.pattern,
            confidence: pattern.confidence,
          })
        }
      }
    })
    
    return signals
  }, [candles])

  const chartData = useMemo(() => {
    if (!candles || candles.length === 0) {
      return []
    }
    
    // Detect patterns and notify parent
    const latestPattern = getLatestSignal(candles)
    if (onPatternDetected) {
      onPatternDetected(latestPattern)
    }
    
    return candles.map((candle, index) => {
      const date = new Date(candle.time)
      const isGreen = candle.close >= candle.open
      
      // Calculate candle body for visualization
      const bodyHigh = Math.max(candle.open, candle.close)
      const bodyLow = Math.min(candle.open, candle.close)
      
      // Wicks
      const upperWick = candle.high - bodyHigh
      const lowerWick = bodyLow - candle.low
      
      // Check if this candle has a buy/sell signal
      const signal = buySellSignals.find(s => s.index === index)
      
      return {
        time: date.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
        }),
        fullTime: candle.time,
        open: candle.open,
        close: candle.close,
        high: candle.high,
        low: candle.low,
        volume: candle.volume,
        ma20: candle.ma20,
        ma50: candle.ma50,
        ma200: candle.ma200,
        isGreen,
        bodyHigh,
        bodyLow,
        bodyHeight: Math.max(bodyHigh - bodyLow, 0.01), // Ensure minimum visible height
        upperWick,
        lowerWick,
        signal: signal?.signal, // 'BUY' or 'SELL'
        signalPrice: signal?.price,
        signalPattern: signal?.pattern,
        signalConfidence: signal?.confidence,
      }
    })
  }, [candles, onPatternDetected, buySellSignals])

  const priceData = useMemo(() => {
    if (!chartData || chartData.length === 0) {
      return { minPrice: 0, maxPrice: 100, maxVolume: 1000000 }
    }
    const prices = chartData.map(d => [d.high, d.low]).flat()
    const volumes = chartData.map(d => d.volume)
    return {
      minPrice: Math.min(...prices) * 0.995,
      maxPrice: Math.max(...prices) * 1.005,
      maxVolume: Math.max(...volumes),
    }
  }, [chartData])

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const change = data.close - data.open
      const changePercent = ((change / data.open) * 100).toFixed(2)
      
      return (
        <div className="bg-black/90 border border-gray-700 rounded-md p-3 shadow-xl">
          <p className="text-xs text-gray-400 mb-2">{data.fullTime}</p>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className={`text-sm font-bold ${data.isGreen ? 'text-green-500' : 'text-red-500'}`}>
                {data.isGreen ? '▲' : '▼'} {changePercent}%
              </span>
              {/* Show buy/sell signal in tooltip */}
              {data.signal && (
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                  data.signal === 'BUY' 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}>
                  {data.signal} {data.signalConfidence}
                </span>
              )}
            </div>
            {data.signalPattern && (
              <div className="text-xs text-yellow-400 font-medium">
                🧠 Pattern: {data.signalPattern.replace(/_/g, ' ')}
              </div>
            )}
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
              <span className="text-gray-400">O:</span>
              <span className="text-white font-medium">${data.open.toFixed(2)}</span>
              <span className="text-gray-400">H:</span>
              <span className="text-green-400 font-medium">${data.high.toFixed(2)}</span>
              <span className="text-gray-400">L:</span>
              <span className="text-red-400 font-medium">${data.low.toFixed(2)}</span>
              <span className="text-gray-400">C:</span>
              <span className="text-white font-medium">${data.close.toFixed(2)}</span>
              {data.signalPrice && (
                <>
                  <span className="text-gray-400">Signal:</span>
                  <span className={`font-bold ${data.signal === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                    ${data.signalPrice.toFixed(2)}
                  </span>
                </>
              )}
              {data.volume && (
                <>
                  <span className="text-gray-400">Vol:</span>
                  <span className="text-blue-400 font-medium">{(data.volume / 1000000).toFixed(2)}M</span>
                </>
              )}
            </div>
            {data.ma20 && (
              <div className="border-t border-gray-700 pt-1 mt-1 text-xs space-y-0.5">
                <div className="flex justify-between">
                  <span className="text-blue-400">MA20:</span>
                  <span className="text-white">${data.ma20.toFixed(2)}</span>
                </div>
                {data.ma50 && (
                  <div className="flex justify-between">
                    <span className="text-purple-400">MA50:</span>
                    <span className="text-white">${data.ma50.toFixed(2)}</span>
                  </div>
                )}
                {data.ma200 && (
                  <div className="flex justify-between">
                    <span className="text-orange-400">MA200:</span>
                    <span className="text-white">${data.ma200.toFixed(2)}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )
    }
    return null
  }

  if (!candles || candles.length === 0) {
    return (
      <div className="w-full flex items-center justify-center text-muted-foreground" style={{ height: `${height}px` }}>
        <p>No chart data available</p>
      </div>
    )
  }

  const priceChartHeight = height * 0.75
  const volumeChartHeight = height * 0.25

  return (
    <div className="w-full flex flex-col bg-gradient-to-br from-gray-900 to-black rounded-lg" style={{ height: `${height}px` }}>
      {/* Resistance Levels Legend */}
      {resistanceLevels && (
        <div className="px-4 py-2 border-b border-gray-800 bg-black/50">
          <div className="flex items-center justify-between text-xs flex-wrap gap-2">
            <div className="flex items-center gap-4 flex-wrap">
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
            <div className="flex items-center gap-3 text-xs flex-wrap">
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
              {/* Buy/Sell Signals Count */}
              {buySellSignals.length > 0 && (
                <>
                  <span className="text-gray-500">|</span>
                  <div className="flex items-center gap-2">
                    <span className="text-green-400 font-semibold">
                      🟢 BUY: {buySellSignals.filter(s => s.signal === 'BUY').length}
                    </span>
                    <span className="text-red-400 font-semibold">
                      🔴 SELL: {buySellSignals.filter(s => s.signal === 'SELL').length}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Price Chart */}
      <div style={{ height: `${priceChartHeight}px` }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart 
            data={chartData}
            margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
          >
            <defs>
              {/* Solid colors for Webull-style candles */}
              <linearGradient id="greenCandle" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#26a69a" stopOpacity={1}/>
                <stop offset="100%" stopColor="#26a69a" stopOpacity={1}/>
              </linearGradient>
              <linearGradient id="redCandle" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef5350" stopOpacity={1}/>
                <stop offset="100%" stopColor="#ef5350" stopOpacity={1}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255,255,255,0.1)" 
              opacity={0.3}
              vertical={false}
            />
            
            <XAxis 
              dataKey="time" 
              stroke="rgba(255,255,255,0.3)"
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }}
              tickLine={false}
              interval="preserveStartEnd"
              axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
            />
            
            <YAxis 
              yAxisId="price"
              domain={[priceData.minPrice, priceData.maxPrice]}
              stroke="rgba(255,255,255,0.3)"
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }}
              tickLine={false}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
              axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
              orientation="right"
            />
            
            <Tooltip content={<CustomTooltip />} />

            {/* Moving Average Lines - Webull style thin lines */}
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="ma20" 
              stroke="#2196F3" 
              strokeWidth={1.5}
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
            
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="ma50" 
              stroke="#9C27B0" 
              strokeWidth={1.5}
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
            
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="ma200" 
              stroke="#FF9800" 
              strokeWidth={1.5}
              dot={false}
              connectNulls
              isAnimationActive={false}
            />

            {/* 24H HIGH/LOW RESISTANCE LEVELS */}
            {resistanceLevels && (
              <>
                {/* 24H High Resistance Zone (Red Box) */}
                <ReferenceArea
                  yAxisId="price"
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
                  yAxisId="price"
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
                  />
                </ReferenceLine>

                {/* 24H Low Support Zone (Green Box) */}
                <ReferenceArea
                  yAxisId="price"
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
                  yAxisId="price"
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
                  />
                </ReferenceLine>

                {/* Fibonacci 61.8% Level (Key Resistance) */}
                <ReferenceLine
                  yAxisId="price"
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
                  yAxisId="price"
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
                  yAxisId="price"
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
                  yAxisId="price"
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
                  />
                </ReferenceLine>
              </>
            )}

            {/* Draw candlesticks using Scatter with custom shapes */}
            <Scatter
              yAxisId="price"
              data={chartData}
              fill="#26a69a"
              isAnimationActive={false}
              shape={(props: any) => {
                const { cx, cy, payload, xAxis, yAxis } = props
                if (!payload || !yAxis || !xAxis) return null

                const color = payload.isGreen ? '#26a69a' : '#ef5350'
                
                // Convert prices to Y coordinates
                const highY = yAxis.scale(payload.high)
                const lowY = yAxis.scale(payload.low)
                const bodyHighY = yAxis.scale(payload.bodyHigh)
                const bodyLowY = yAxis.scale(payload.bodyLow)
                
                const bodyWidth = 6
                const wickWidth = 1.5
                
                // Buy/Sell signal markers
                const hasSignal = payload.signal === 'BUY' || payload.signal === 'SELL'
                const signalY = payload.signalPrice ? yAxis.scale(payload.signalPrice) : null
                const isBuy = payload.signal === 'BUY'
                const signalColor = isBuy ? '#22c55e' : '#ef4444'
                
                return (
                  <g>
                    {/* Upper wick from high to body top */}
                    <line
                      x1={cx}
                      y1={highY}
                      x2={cx}
                      y2={bodyHighY}
                      stroke={color}
                      strokeWidth={wickWidth}
                    />
                    
                    {/* Candle body */}
                    <rect
                      x={cx - bodyWidth / 2}
                      y={bodyHighY}
                      width={bodyWidth}
                      height={Math.max(bodyLowY - bodyHighY, 1)}
                      fill={color}
                    />
                    
                    {/* Lower wick from body bottom to low */}
                    <line
                      x1={cx}
                      y1={bodyLowY}
                      x2={cx}
                      y2={lowY}
                      stroke={color}
                      strokeWidth={wickWidth}
                    />
                    
                    {/* Buy/Sell Signal Markers */}
                    {hasSignal && signalY !== null && (
                      <g>
                        {/* Arrow pointing to signal price */}
                        {isBuy ? (
                          // BUY Signal - Green upward arrow below candle
                          <g>
                            <polygon
                              points={`${cx},${signalY + 15} ${cx - 8},${signalY + 5} ${cx + 8},${signalY + 5}`}
                              fill={signalColor}
                              stroke="#ffffff"
                              strokeWidth={1}
                            />
                            <text
                              x={cx}
                              y={signalY + 30}
                              textAnchor="middle"
                              fill={signalColor}
                              fontSize="10"
                              fontWeight="bold"
                            >
                              BUY
                            </text>
                            {/* Confidence indicator */}
                            <circle
                              cx={cx + 12}
                              cy={signalY + 5}
                              r={4}
                              fill={payload.signalConfidence === 'HIGH' ? '#22c55e' : '#f59e0b'}
                              stroke="#ffffff"
                              strokeWidth={1}
                            />
                          </g>
                        ) : (
                          // SELL Signal - Red downward arrow above candle
                          <g>
                            <polygon
                              points={`${cx},${signalY - 15} ${cx - 8},${signalY - 5} ${cx + 8},${signalY - 5}`}
                              fill={signalColor}
                              stroke="#ffffff"
                              strokeWidth={1}
                            />
                            <text
                              x={cx}
                              y={signalY - 25}
                              textAnchor="middle"
                              fill={signalColor}
                              fontSize="10"
                              fontWeight="bold"
                            >
                              SELL
                            </text>
                            {/* Confidence indicator */}
                            <circle
                              cx={cx + 12}
                              cy={signalY - 5}
                              r={4}
                              fill={payload.signalConfidence === 'HIGH' ? '#ef4444' : '#f59e0b'}
                              stroke="#ffffff"
                              strokeWidth={1}
                            />
                          </g>
                        )}
                        {/* Price line to signal */}
                        <line
                          x1={cx}
                          y1={isBuy ? lowY : highY}
                          x2={cx}
                          y2={signalY}
                          stroke={signalColor}
                          strokeWidth={1.5}
                          strokeDasharray="3 3"
                          opacity={0.6}
                        />
                      </g>
                    )}
                  </g>
                )
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Chart - Webull style */}
      <div style={{ height: `${volumeChartHeight}px` }} className="border-t border-gray-800">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart 
            data={chartData}
            margin={{ top: 0, right: 10, left: 10, bottom: 5 }}
          >
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255,255,255,0.1)" 
              opacity={0.2}
              vertical={false}
            />
            
            <XAxis 
              dataKey="time" 
              stroke="rgba(255,255,255,0.3)"
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }}
              tickLine={false}
              interval="preserveStartEnd"
              axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
            />
            
            <YAxis 
              stroke="rgba(255,255,255,0.3)"
              tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }}
              tickLine={false}
              tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
              axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
              orientation="right"
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            {/* Volume Bars */}
            <Bar 
              dataKey="volume" 
              fill="#26a69a"
              maxBarSize={8}
              isAnimationActive={false}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`vol-${index}`} 
                  fill={entry.isGreen ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'}
                />
              ))}
            </Bar>
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

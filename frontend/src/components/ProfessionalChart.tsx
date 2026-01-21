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
  Legend,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts'

interface ProfessionalChartProps {
  candles: Candle[]
  height?: number
  showVolume?: boolean
}

export default function ProfessionalChart({ candles, height = 400, showVolume = true }: ProfessionalChartProps) {
  const chartData = useMemo(() => {
    // Safety check for empty or undefined candles
    if (!candles || candles.length === 0) {
      return []
    }
    
    // Calculate volume metrics for Bookmap-style visualization
    const maxVolume = Math.max(...candles.map(c => c.volume))
    const avgVolume = candles.reduce((sum, c) => sum + c.volume, 0) / candles.length
    
    // Calculate VWAP (Volume Weighted Average Price)
    let cumulativeVolumePrice = 0
    let cumulativeVolume = 0
    
    return candles.map((candle, index) => {
      const date = new Date(candle.time)
      const isGreen = candle.close >= candle.open
      
      // Calculate candle body for visualization
      const bodyHigh = Math.max(candle.open, candle.close)
      const bodyLow = Math.min(candle.open, candle.close)
      
      // Calculate typical price for VWAP
      const typicalPrice = (candle.high + candle.low + candle.close) / 3
      cumulativeVolumePrice += typicalPrice * candle.volume
      cumulativeVolume += candle.volume
      const vwap = cumulativeVolume > 0 ? cumulativeVolumePrice / cumulativeVolume : candle.close
      
      // Volume intensity (0-1) for heatmap effect
      const volumeIntensity = candle.volume / maxVolume
      
      // Estimate buy/sell pressure (using close vs open and volume)
      const priceChange = candle.close - candle.open
      const buyPressure = isGreen ? candle.volume : candle.volume * 0.3
      const sellPressure = !isGreen ? candle.volume : candle.volume * 0.3
      
      // Delta volume (buy - sell estimate)
      const deltaVolume = buyPressure - sellPressure
      
      return {
        time: date.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          month: 'short',
          day: 'numeric'
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
        vwap: vwap,
        volumeIntensity: volumeIntensity,
        buyPressure: buyPressure,
        sellPressure: sellPressure,
        deltaVolume: deltaVolume,
        abovAvgVolume: candle.volume > avgVolume,
        isGreen,
        bodyHigh,
        bodyLow,
        bodyHeight: bodyHigh - bodyLow,
        wickHigh: candle.high,
        wickLow: candle.low,
        // Color volume based on price action
        volumeColor: isGreen ? '#22c55e' : '#ef4444',
      }
    })
  }, [candles])

  const priceData = useMemo(() => {
    if (!chartData || chartData.length === 0) {
      return {
        minPrice: 0,
        maxPrice: 100,
        maxVolume: 1000000,
      }
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
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
          <p className="text-xs text-muted-foreground mb-2">{data.fullTime}</p>
          <div className="space-y-1">
            <p className={`text-sm font-semibold ${data.isGreen ? 'text-green-400' : 'text-red-400'}`}>
              {data.isGreen ? '↑' : '↓'} {data.close >= data.open ? 'Bullish' : 'Bearish'}
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">O:</span> ${data.open.toFixed(2)}
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">H:</span> ${data.high.toFixed(2)}
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">L:</span> ${data.low.toFixed(2)}
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">C:</span> ${data.close.toFixed(2)}
            </p>
            <p className="text-sm">
              <span className="text-muted-foreground">V:</span> {(data.volume / 1000000).toFixed(2)}M
            </p>
            {data.ma20 && (
              <p className="text-sm">
                <span className="text-blue-400">MA20:</span> ${data.ma20.toFixed(2)}
              </p>
            )}
            {data.ma50 && (
              <p className="text-sm">
                <span className="text-purple-400">MA50:</span> ${data.ma50.toFixed(2)}
              </p>
            )}
            {data.ma200 && (
              <p className="text-sm">
                <span className="text-orange-400">MA200:</span> ${data.ma200.toFixed(2)}
              </p>
            )}
            {data.vwap && (
              <p className="text-sm border-t border-border pt-1 mt-1">
                <span className="text-yellow-400 font-semibold">VWAP:</span> ${data.vwap.toFixed(2)}
              </p>
            )}
          </div>
        </div>
      )
    }
    return null
  }

  const chartHeight = showVolume ? height * 0.7 : height
  const volumeHeight = showVolume ? height * 0.3 : 0

  if (!candles || candles.length === 0) {
    return (
      <div className="w-full flex items-center justify-center text-muted-foreground" style={{ height: `${height}px` }}>
        <p>No chart data available</p>
      </div>
    )
  }

  return (
    <div className="w-full" style={{ height: `${height}px` }}>
      {/* Price Chart */}
      <div style={{ height: `${chartHeight}px` }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart 
            data={chartData}
            margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="greenGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0.3}/>
              </linearGradient>
              <linearGradient id="redGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.3}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="hsl(var(--border))" 
              opacity={0.2}
            />
            
            <XAxis 
              dataKey="time" 
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            
            <YAxis 
              domain={[priceData.minPrice, priceData.maxPrice]}
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
              tickLine={false}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            <Legend 
              wrapperStyle={{ fontSize: '12px' }}
              iconType="line"
            />

            {/* Moving Average Lines */}
            <Line 
              type="monotone" 
              dataKey="ma20" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={false}
              name="MA20"
              connectNulls
            />
            
            <Line 
              type="monotone" 
              dataKey="ma50" 
              stroke="#a855f7" 
              strokeWidth={2}
              dot={false}
              name="MA50"
              connectNulls
            />
            
            <Line 
              type="monotone" 
              dataKey="ma200" 
              stroke="#f97316" 
              strokeWidth={2.5}
              dot={false}
              name="MA200"
              connectNulls
            />

            {/* VWAP (Volume Weighted Average Price) - Bookmap style */}
            <Line 
              type="monotone" 
              dataKey="vwap" 
              stroke="#eab308" 
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="VWAP"
              connectNulls
            />

            {/* Candlestick Bodies */}
            <Bar 
              dataKey="bodyHeight" 
              fill="#22c55e"
              radius={[2, 2, 2, 2]}
              maxBarSize={10}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.isGreen ? 'url(#greenGradient)' : 'url(#redGradient)'}
                />
              ))}
            </Bar>
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Enhanced Bookmap-Style Volume Chart */}
      {showVolume && (
        <div style={{ height: `${volumeHeight}px` }} className="mt-2">
          <div className="mb-1 flex items-center justify-between px-2">
            <span className="text-xs font-semibold text-foreground">📊 Order Flow & Volume Analysis</span>
            <div className="flex gap-3 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <span className="text-muted-foreground">Buy Pressure</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                <span className="text-muted-foreground">Sell Pressure</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-0.5 bg-yellow-500"></div>
                <span className="text-muted-foreground">VWAP</span>
              </div>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart 
              data={chartData}
              margin={{ top: 0, right: 10, left: 10, bottom: 10 }}
            >
              <defs>
                {/* Volume intensity gradients for heatmap effect */}
                <linearGradient id="buyHeatmap" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0.3} />
                </linearGradient>
                <linearGradient id="sellHeatmap" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity={0.3} />
                </linearGradient>
              </defs>
              
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="hsl(var(--border))" 
                opacity={0.2}
              />
              
              <XAxis 
                dataKey="time" 
                stroke="hsl(var(--muted-foreground))"
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
                tickLine={false}
                interval="preserveStartEnd"
              />
              
              <YAxis 
                stroke="hsl(var(--muted-foreground))"
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
                tickLine={false}
                tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                label={{ 
                  value: 'Volume', 
                  angle: -90, 
                  position: 'insideLeft',
                  style: { fill: 'hsl(var(--muted-foreground))', fontSize: 11 }
                }}
              />
              
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    const buyPct = (data.buyPressure / data.volume * 100).toFixed(1)
                    const sellPct = (data.sellPressure / data.volume * 100).toFixed(1)
                    return (
                      <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
                        <p className="text-xs font-semibold mb-1 text-muted-foreground">{data.time}</p>
                        <div className="space-y-1">
                          <p className="text-sm font-bold">
                            Total: {(data.volume / 1000000).toFixed(2)}M
                          </p>
                          <div className="flex items-center gap-2">
                            <span className="text-green-400 text-sm font-semibold">🟢 Buy:</span>
                            <span className="text-sm">{(data.buyPressure / 1000000).toFixed(2)}M ({buyPct}%)</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-red-400 text-sm font-semibold">🔴 Sell:</span>
                            <span className="text-sm">{(data.sellPressure / 1000000).toFixed(2)}M ({sellPct}%)</span>
                          </div>
                          <div className="border-t border-border pt-1 mt-1">
                            <p className="text-xs text-muted-foreground">
                              Delta: <span className={data.deltaVolume > 0 ? 'text-green-400' : 'text-red-400'}>
                                {data.deltaVolume > 0 ? '+' : ''}{(data.deltaVolume / 1000000).toFixed(2)}M
                              </span>
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Intensity: {(data.volumeIntensity * 100).toFixed(0)}%
                            </p>
                            {data.abovAvgVolume && (
                              <p className="text-xs text-yellow-400 font-semibold">⚡ Above Average</p>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  }
                  return null
                }}
              />

              {/* Buy Pressure Bars (Stacked at bottom) */}
              <Bar 
                dataKey="buyPressure" 
                stackId="volume"
                fill="url(#buyHeatmap)"
                radius={[0, 0, 0, 0]}
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`buy-${index}`}
                    fill={`rgba(34, 197, 94, ${0.3 + entry.volumeIntensity * 0.7})`}
                  />
                ))}
              </Bar>

              {/* Sell Pressure Bars (Stacked on top) */}
              <Bar 
                dataKey="sellPressure" 
                stackId="volume"
                fill="url(#sellHeatmap)"
                radius={[2, 2, 0, 0]}
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`sell-${index}`}
                    fill={`rgba(239, 68, 68, ${0.3 + entry.volumeIntensity * 0.7})`}
                  />
                ))}
              </Bar>

              {/* Volume Line (outline) */}
              <Line 
                type="monotone"
                dataKey="volume"
                stroke="hsl(var(--border))"
                strokeWidth={1}
                dot={false}
                opacity={0.5}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

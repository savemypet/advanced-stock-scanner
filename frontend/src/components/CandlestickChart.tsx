import { useMemo } from 'react'
import { Candle } from '../types'
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
  Scatter,
} from 'recharts'
import { detectPatterns, getLatestSignal, PatternSignal } from '../utils/candlestickPatterns'

interface CandlestickChartProps {
  candles: Candle[]
  height?: number
  onPatternDetected?: (pattern: PatternSignal | null) => void
}

interface Signal {
  time: string
  price: number
  type: 'BUY' | 'SELL'
  isNewHighLow: boolean
  pattern?: string
  description?: string
}

export default function CandlestickChart({ candles, height = 256, onPatternDetected }: CandlestickChartProps) {
  const { chartData, signals, latestPattern } = useMemo(() => {
    const data = candles.map((candle) => {
      const date = new Date(candle.time)
      return {
        time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        open: candle.open,
        close: candle.close,
        high: candle.high,
        low: candle.low,
        volume: candle.volume,
        isGreen: candle.close >= candle.open,
      }
    })

    // Detect candlestick patterns
    const patterns = detectPatterns(candles)
    const latest = getLatestSignal(candles)
    
    // Notify parent about latest pattern
    if (onPatternDetected) {
      onPatternDetected(latest)
    }

    // Generate buy/sell signals based on patterns
    const sigs: Signal[] = patterns.map(pattern => ({
      time: data[pattern.candleIndex]?.time || '',
      price: pattern.signal === 'BUY' ? candles[pattern.candleIndex].low : candles[pattern.candleIndex].high,
      type: pattern.signal,
      isNewHighLow: pattern.confidence === 'HIGH',
      pattern: pattern.pattern,
      description: pattern.description
    }))

    return { chartData: data, signals: sigs, latestPattern: latest }
  }, [candles, onPatternDetected])

  const avgPrice = useMemo(() => {
    const sum = chartData.reduce((acc, d) => acc + d.close, 0)
    return sum / chartData.length
  }, [chartData])

  // Separate buy and sell signals for rendering
  const buySignals = useMemo(() => 
    signals.filter(s => s.type === 'BUY').map(s => ({ 
      ...s, 
      size: s.isNewHighLow ? 150 : 80 
    }))
  , [signals])
  
  const sellSignals = useMemo(() => 
    signals.filter(s => s.type === 'SELL').map(s => ({ 
      ...s, 
      size: s.isNewHighLow ? 150 : 80 
    }))
  , [signals])

  const renderSignalLabel = (props: any) => {
    const { cx, cy, fill, payload } = props
    if (!cx || !cy) return null
    
    const isBuy = payload.type === 'BUY'
    const label = payload.pattern 
      ? payload.pattern.replace(/_/g, ' ')
      : `${payload.type}`
    
    if (isBuy) {
      // BUY label above the candle - text only, no box
      return (
        <g>
          <text
            x={cx}
            y={cy - 15}
            textAnchor="middle"
            fill="#10b981"
            fontSize={12}
            fontWeight="bold"
            style={{ textShadow: '0 0 4px rgba(0,0,0,0.9), 0 0 8px rgba(0,0,0,0.7)' }}
          >
            {label}
          </text>
          <text
            x={cx}
            y={cy - 3}
            textAnchor="middle"
            fill="#10b981"
            fontSize={10}
            style={{ textShadow: '0 0 4px rgba(0,0,0,0.9)' }}
          >
            ${payload.price.toFixed(2)}
          </text>
        </g>
      )
    } else {
      // SELL label below the candle - text only, no box
      return (
        <g>
          <text
            x={cx}
            y={cy + 15}
            textAnchor="middle"
            fill="#dc2626"
            fontSize={12}
            fontWeight="bold"
            style={{ textShadow: '0 0 4px rgba(0,0,0,0.9), 0 0 8px rgba(0,0,0,0.7)' }}
          >
            {label}
          </text>
          <text
            x={cx}
            y={cy + 27}
            textAnchor="middle"
            fill="#dc2626"
            fontSize={10}
            style={{ textShadow: '0 0 4px rgba(0,0,0,0.9)' }}
          >
            ${payload.price.toFixed(2)}
          </text>
        </g>
      )
    }
  }

  return (
    <div className="w-full rounded-lg bg-muted/20 p-2" style={{ height: `${height}px` }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData}>
          <XAxis 
            dataKey="time" 
            stroke="#666"
            tick={{ fill: '#888', fontSize: 11 }}
            tickLine={false}
          />
          <YAxis 
            stroke="#666"
            tick={{ fill: '#888', fontSize: 11 }}
            tickLine={false}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px',
              padding: '8px'
            }}
            formatter={(value: number) => `$${value.toFixed(2)}`}
          />
          <ReferenceLine 
            y={avgPrice} 
            stroke="#666" 
            strokeDasharray="3 3"
            label={{ value: 'AVG', fill: '#888', fontSize: 10 }}
          />
          
          {/* Candlestick bodies */}
          <Bar dataKey="close" fill="#22c55e" radius={[2, 2, 2, 2]}>
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.isGreen ? '#22c55e' : '#ef4444'}
              />
            ))}
          </Bar>
          
          {/* Buy signals - text labels only (no triangles) */}
          {buySignals.length > 0 && (
            <Scatter 
              data={buySignals}
              dataKey="price"
              fill="transparent"
              shape={renderSignalLabel}
              isAnimationActive={false}
              zIndex={1000}
            />
          )}
          
          {/* Sell signals - text labels only (no triangles) */}
          {sellSignals.length > 0 && (
            <Scatter 
              data={sellSignals}
              dataKey="price"
              fill="transparent"
              shape={renderSignalLabel}
              isAnimationActive={false}
              zIndex={1000}
            />
          )}
          
          {/* High/Low wicks */}
          {chartData.map((entry, index) => {
            const x = index * (100 / chartData.length)
            return (
              <line
                key={`wick-${index}`}
                x1={`${x}%`}
                y1={entry.high}
                x2={`${x}%`}
                y2={entry.low}
                stroke={entry.isGreen ? '#22c55e' : '#ef4444'}
                strokeWidth={1}
              />
            )
          })}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

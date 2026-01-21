import { useMemo } from 'react'
import { Candle } from '../types'
import {
  ComposedChart,
  Scatter,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ZAxis,
} from 'recharts'

interface BookmapChartProps {
  candles: Candle[]
  height?: number
}

export default function BookmapChart({ candles, height = 400 }: BookmapChartProps) {
  const chartData = useMemo(() => {
    if (!candles || candles.length === 0) {
      return { priceData: [], buyPoints: [], sellPoints: [] }
    }

    const maxVolume = Math.max(...candles.map(c => c.volume))
    
    // Calculate max buy and sell pressures for scaling
    let maxBuyPressure = 0
    let maxSellPressure = 0
    
    // First pass: calculate all pressures to find max
    const pressures = candles.map((candle) => {
      const isGreen = candle.close >= candle.open
      const priceRange = candle.high - candle.low
      const closePosition = priceRange > 0 ? (candle.close - candle.low) / priceRange : 0.5
      const buyPressure = candle.volume * closePosition * (isGreen ? 1.3 : 0.7)
      const sellPressure = candle.volume * (1 - closePosition) * (!isGreen ? 1.3 : 0.7)
      
      maxBuyPressure = Math.max(maxBuyPressure, buyPressure)
      maxSellPressure = Math.max(maxSellPressure, sellPressure)
      
      return { buyPressure, sellPressure }
    })
    
    const priceData: any[] = []
    const buyPoints: any[] = []
    const sellPoints: any[] = []
    
    candles.forEach((candle, index) => {
      const date = new Date(candle.time)
      const timeStr = date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
      })
      
      const isGreen = candle.close >= candle.open
      const priceChange = candle.close - candle.open
      const priceRange = candle.high - candle.low
      
      // Get pre-calculated pressures
      const { buyPressure, sellPressure } = pressures[index]
      
      // Net pressure determines direction
      const netPressure = buyPressure - sellPressure
      const isBuying = netPressure > 0
      
      // Ball size based on ACTUAL buy/sell pressure (not total volume)
      // Larger buying = larger green ball, larger selling = larger red ball
      const buyBubbleSize = 50 + (buyPressure / maxBuyPressure) * 400
      const sellBubbleSize = 50 + (sellPressure / maxSellPressure) * 400
      
      // Price line data
      priceData.push({
        time: timeStr,
        timeIndex: index,
        fullTime: candle.time,
        price: candle.close,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        volume: candle.volume,
        buyPressure,
        sellPressure,
        netPressure,
        isBuying,
      })
      
      // Create buy pressure points (green balls) - size based on buy pressure amount
      // Position higher in the candle range for buy pressure
      if (isBuying && buyPressure > 0) {
        const priceOffset = priceRange * 0.25 // Offset buy balls upward (25% of candle range)
        buyPoints.push({
          time: timeStr,
          timeIndex: index,
          fullTime: candle.time,
          price: candle.close + priceOffset,
          size: buyBubbleSize,
          volume: buyPressure,
          intensity: buyPressure / maxBuyPressure,
          pressureAmount: buyPressure,
        })
      }
      
      // Create sell pressure points (red balls) - size based on sell pressure amount
      // Position lower in the candle range for sell pressure
      if (!isBuying && sellPressure > 0) {
        const priceOffset = priceRange * 0.25 // Offset sell balls downward (25% of candle range)
        sellPoints.push({
          time: timeStr,
          timeIndex: index,
          fullTime: candle.time,
          price: candle.close - priceOffset,
          size: sellBubbleSize,
          volume: sellPressure,
          intensity: sellPressure / maxSellPressure,
          pressureAmount: sellPressure,
        })
      }
    })
    
    return { priceData, buyPoints, sellPoints }
  }, [candles])

  const { priceData, buyPoints, sellPoints } = chartData

  const priceRange = useMemo(() => {
    if (!priceData || priceData.length === 0) {
      return { minPrice: 0, maxPrice: 100 }
    }
    const prices = priceData.map(d => [d.high, d.low]).flat()
    return {
      minPrice: Math.min(...prices) * 0.98,
      maxPrice: Math.max(...prices) * 1.02,
    }
  }, [priceData])

  if (!candles || candles.length === 0) {
    return (
      <div className="w-full flex items-center justify-center text-muted-foreground" style={{ height: `${height}px` }}>
        <p>No data available</p>
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      
      // Handle scatter point tooltips (buy/sell balls)
      if (data.pressureAmount !== undefined) {
        const pressureType = data.intensity !== undefined && data.pressureAmount === data.volume ? 
          (data.pressureAmount > 0 ? 'BUY' : 'SELL') : 'UNKNOWN'
        
        return (
          <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
            <p className="text-xs text-muted-foreground mb-2">{data.fullTime}</p>
            <div className="space-y-1">
              <p className={`text-sm font-bold ${pressureType === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                {pressureType === 'BUY' ? '📈 BUYING PRESSURE' : '📉 SELLING PRESSURE'}
              </p>
              <p className="text-sm font-semibold">
                Price: ${data.price.toFixed(2)}
              </p>
              <div className="border-t border-border pt-1 mt-1">
                <p className={`text-sm font-bold ${pressureType === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                  {pressureType === 'BUY' ? '🟢' : '🔴'} Pressure: {(data.pressureAmount / 1000000).toFixed(2)}M
                </p>
                <p className="text-xs text-muted-foreground">
                  Intensity: {(data.intensity * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-yellow-400 mt-1">
                  💡 Ball size = pressure amount
                </p>
              </div>
            </div>
          </div>
        )
      }
      
      // Handle price line tooltips
      if (data.volume) {
        const buyPct = ((data.buyPressure / data.volume) * 100).toFixed(1)
        const sellPct = ((data.sellPressure / data.volume) * 100).toFixed(1)
        
        return (
          <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
            <p className="text-xs text-muted-foreground mb-2">{data.fullTime}</p>
            <div className="space-y-1">
              <p className={`text-sm font-bold ${data.isBuying ? 'text-green-400' : 'text-red-400'}`}>
                {data.isBuying ? '📈 BUYING PRESSURE' : '📉 SELLING PRESSURE'}
              </p>
              <p className="text-sm font-semibold">
                Price: ${data.price.toFixed(2)}
              </p>
              <div className="border-t border-border pt-1 mt-1">
                <p className="text-xs font-semibold text-green-400">
                  🟢 Buy: {(data.buyPressure / 1000000).toFixed(2)}M ({buyPct}%)
                </p>
                <p className="text-xs font-semibold text-red-400">
                  🔴 Sell: {(data.sellPressure / 1000000).toFixed(2)}M ({sellPct}%)
                </p>
              </div>
              <div className="border-t border-border pt-1 mt-1">
                <p className={`text-xs font-semibold ${data.netPressure > 0 ? 'text-green-400' : 'text-red-400'}`}>
                  Net: {data.netPressure > 0 ? '↑ +' : '↓ '}{(data.netPressure / 1000000).toFixed(2)}M
                </p>
              </div>
            </div>
          </div>
        )
      }
      
      return null
    }
    return null
  }

  return (
    <div className="w-full" style={{ height: `${height}px` }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart 
          data={priceData}
          margin={{ top: 10, right: 10, left: 10, bottom: 10 }}
        >
          <defs>
            {/* Gradient for price line */}
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.8}/>
              <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.2}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="hsl(var(--border))" 
            opacity={0.3}
            horizontal={true}
            vertical={false}
          />
          
          <XAxis 
            dataKey="time" 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          
          <YAxis 
            domain={[priceRange.minPrice, priceRange.maxPrice]}
            stroke="hsl(var(--muted-foreground))"
            tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
            tickLine={false}
            tickFormatter={(value) => `$${value.toFixed(2)}`}
          />
          
          <ZAxis range={[50, 450]} dataKey="size" />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Legend 
            wrapperStyle={{ fontSize: '12px' }}
            iconType="circle"
          />

          {/* Price line - moves up with buying, down with selling */}
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#8b5cf6" 
            strokeWidth={3}
            dot={false}
            name="Price Movement"
            animationDuration={300}
          />

          {/* Green balls for buying pressure */}
          <Scatter 
            data={buyPoints}
            dataKey="price"
            fill="#22c55e"
            fillOpacity={0.7}
            stroke="#16a34a"
            strokeWidth={2}
            name="🟢 Buy Pressure"
            shape="circle"
          />

          {/* Red balls for selling pressure */}
          <Scatter 
            data={sellPoints}
            dataKey="price"
            fill="#ef4444"
            fillOpacity={0.7}
            stroke="#dc2626"
            strokeWidth={2}
            name="🔴 Sell Pressure"
            shape="circle"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

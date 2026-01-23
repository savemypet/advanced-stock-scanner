import { Stock, ChartTimeframe } from '../types'
import { TrendingUp, TrendingDown, Activity, BarChart3, Newspaper, Brain } from 'lucide-react'
import PriceBox from './PriceBox'
import { formatNumber, formatCurrency } from '../utils/formatters'

interface StockCardProps {
  stock: Stock
  timeframe: ChartTimeframe
  onClick?: () => void
  onAIAnalysisClick?: (stock: Stock) => void
}

export default function StockCard({ stock, timeframe, onClick }: StockCardProps) {
  const isPositive = stock.changePercent >= 0
  const volumeRatio = (stock.volume / stock.avgVolume).toFixed(2)
  
  return (
    <div 
      className="rounded-lg border border-border bg-card p-3 sm:p-6 hover:border-primary/50 transition-all duration-200 cursor-pointer hover:shadow-lg"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick?.()
        }
      }}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start justify-between mb-3 sm:mb-4 gap-2 sm:gap-0">
        <div className="flex-1 w-full sm:w-auto">
          <div className="flex items-center gap-2 sm:gap-3 mb-1 flex-wrap">
            <h3 className="text-xl sm:text-2xl font-bold text-primary">{stock.symbol}</h3>
            {stock.isHot && (
              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-orange-500/20 text-orange-400">
                🔥 HOT
              </span>
            )}
            {stock.signal === 'BUY' && (
              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-500/20 text-green-400">
                BUY
              </span>
            )}
            {stock.signal === 'SELL' && (
              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-500/20 text-red-400">
                SELL
              </span>
            )}
            {(stock as any).detectedPattern && (
              <span 
                className={`px-2 py-1 text-xs font-semibold rounded-full flex items-center gap-1 ${
                  (stock as any).detectedPattern.signal === 'BUY' 
                    ? 'bg-gradient-to-r from-green-500/20 to-blue-500/20 text-green-300 border border-green-500/30' 
                    : 'bg-gradient-to-r from-red-500/20 to-orange-500/20 text-red-300 border border-red-500/30'
                }`}
                title={(stock as any).detectedPattern.description}
              >
                🧠 {(stock as any).detectedPattern.name.replace(/_/g, ' ')}
              </span>
            )}
            {stock.hasNews && stock.newsCount && stock.newsCount > 0 && (
              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-500/20 text-blue-400 flex items-center gap-1">
                <Newspaper className="w-3 h-3" />
                {stock.newsCount} News
              </span>
            )}
            {/* AI Analysis Button */}
            <button
              onClick={(e) => {
                e.stopPropagation()
                onAIAnalysisClick?.(stock)
              }}
              className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 border border-purple-500/30 flex items-center gap-1 transition-colors"
              title="Get AI Analysis (Ollama)"
            >
              <Brain className="w-3 h-3" />
              AI
            </button>
          </div>
          <p className="text-sm sm:text-base font-medium text-foreground mb-0.5">{stock.name}</p>
          <p className="text-xs text-muted-foreground">
            Float: {formatNumber(stock.float)} • Volume: {formatNumber(stock.volume)}
          </p>
        </div>
        
        <div className="text-left sm:text-right w-full sm:w-auto">
          <div className="text-2xl sm:text-3xl font-bold mb-1">
            {formatCurrency(stock.currentPrice)}
          </div>
          <div className={`flex items-center gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? <TrendingUp className="w-3 h-3 sm:w-4 sm:h-4" /> : <TrendingDown className="w-3 h-3 sm:w-4 sm:h-4" />}
            <span className="text-base sm:text-lg font-semibold">
              {isPositive ? '+' : ''}{stock.changePercent.toFixed(2)}%
            </span>
            <span className="text-xs sm:text-sm">
              ({isPositive ? '+' : ''}{formatCurrency(stock.changeAmount)})
            </span>
          </div>
        </div>
      </div>

      {/* Stats Grid - Responsive */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-3 sm:mb-4">
        <StatItem 
          label="Volume" 
          value={formatNumber(stock.volume)}
          subValue={`${volumeRatio}x avg`}
          icon={<Activity className="w-3 h-3 sm:w-4 sm:h-4" />}
        />
        <StatItem 
          label="Float" 
          value={formatNumber(stock.float)}
          subValue="shares"
          icon={<BarChart3 className="w-3 h-3 sm:w-4 sm:h-4" />}
        />
        <StatItem 
          label="Day High" 
          value={formatCurrency(stock.dayHigh)}
          subValue={`Low: ${formatCurrency(stock.dayLow)}`}
        />
        <StatItem 
          label="Open" 
          value={formatCurrency(stock.openPrice)}
          subValue={`Prev: ${formatCurrency(stock.previousClose)}`}
        />
      </div>

      {/* Price Information */}
      <div className="mt-3 sm:mt-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-2 gap-1">
          <span className="text-xs sm:text-sm font-medium">Price Info - Click for details</span>
          <span className="text-xs text-muted-foreground">
            {new Date(stock.lastUpdated).toLocaleTimeString()}
          </span>
        </div>
        <div className="rounded-lg overflow-hidden border border-border/50">
          <PriceBox 
            candles={stock.candles} 
            currentPrice={stock.currentPrice}
            height={280} 
          />
        </div>
      </div>
    </div>
  )
}

interface StatItemProps {
  label: string
  value: string
  subValue?: string
  icon?: React.ReactNode
}

function StatItem({ label, value, subValue, icon }: StatItemProps) {
  return (
    <div className="flex flex-col">
      <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
        {icon}
        <span className="truncate">{label}</span>
      </div>
      <div className="text-base sm:text-lg font-semibold truncate">{value}</div>
      {subValue && (
        <div className="text-xs text-muted-foreground truncate">{subValue}</div>
      )}
    </div>
  )
}

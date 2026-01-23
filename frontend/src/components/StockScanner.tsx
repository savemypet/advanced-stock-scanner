import { Stock, ScannerSettings } from '../types'
import StockCard from './StockCard'
import { AlertCircle, Search } from 'lucide-react'

interface StockScannerProps {
  stocks: Stock[]
  isLoading: boolean
  settings: ScannerSettings
  countdown: number
  onStockClick?: (stock: Stock) => void
  onAIAnalysisClick?: (stock: Stock) => void
}

export default function StockScanner({ stocks, isLoading, settings, countdown, onStockClick }: StockScannerProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-center py-12 px-4">
          <div className="text-center max-w-md">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4 mx-auto">
              <Search className="w-8 h-8 text-primary animate-pulse" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Scanning Markets...</h3>
            <p className="text-muted-foreground mb-2">
              Searching for stocks matching your criteria
            </p>
            <p className="text-xs text-muted-foreground bg-muted/30 rounded-lg p-2">
              Looking for: {settings.minGainPercent}% gain, {settings.volumeMultiplier}x volume
            </p>
            <div className="mt-4 flex items-center justify-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        </div>
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="h-64 rounded-lg bg-card border border-border animate-shimmer" />
        ))}
      </div>
    )
  }

  if (stocks.length === 0) {
    // Check if scanner has been started
    const hasScanned = settings.realTimeUpdates || isLoading
    
    return (
      <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
        <div className="flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
          <AlertCircle className="w-8 h-8 text-muted-foreground" />
        </div>
        
        {!hasScanned ? (
          <>
            <h3 className="text-xl font-semibold mb-2">Welcome to Stock Scanner</h3>
            <p className="text-muted-foreground max-w-md mb-6">
              Click <strong>Start</strong> to begin scanning or choose a quick preset below
            </p>
            
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
              <div className="px-6 py-4 rounded-lg bg-gradient-to-r from-green-500/10 to-emerald-600/10 border border-green-500/20">
                <p className="text-sm font-medium mb-1">💰 Penny Stocks</p>
                <p className="text-xs text-muted-foreground">$0.05 - $1.00</p>
              </div>
              <div className="px-6 py-4 rounded-lg bg-gradient-to-r from-blue-500/10 to-indigo-600/10 border border-blue-500/20">
                <p className="text-sm font-medium mb-1">🔥 Explosive Mode</p>
                <p className="text-xs text-muted-foreground">$1 - $20</p>
              </div>
            </div>
            
            <p className="text-xs text-muted-foreground">
              Open <strong>Settings</strong> to choose a preset or customize filters
            </p>
          </>
        ) : (
          <>
            <h3 className="text-xl font-semibold mb-2">No Stocks Found</h3>
            <p className="text-muted-foreground max-w-md mb-4">
              No stocks currently match your criteria. The scanner will keep looking!
            </p>
            
            {settings.realTimeUpdates && countdown > 0 && (
              <div className="mb-6 px-4 py-2 rounded-lg bg-primary/10 border border-primary/20">
                <span className="text-sm text-primary font-medium">
                  Next scan in {countdown}s
                </span>
              </div>
            )}
            
            <div className="mt-2 p-4 rounded-lg bg-muted/50 text-sm text-left max-w-md">
              <p className="font-medium mb-2">Current Filters:</p>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Price: ${settings.minPrice} - ${settings.maxPrice}</li>
                <li>• Min Gain: {settings.minGainPercent}%</li>
                <li>• Volume: {settings.volumeMultiplier}x average</li>
              </ul>
            </div>
            
            <p className="text-xs text-muted-foreground mt-6">
              💡 Tip: Try lowering the minimum gain % or increasing volume multiplier if no stocks appear
            </p>
          </>
        )}
      </div>
    )
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-2">
        <div>
          <h2 className="text-lg sm:text-xl font-semibold">
            Qualifying Stocks ({stocks.length})
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Sorted by highest gain percentage • {settings.minGainPercent}% gain • {settings.volumeMultiplier}x volume
          </p>
        </div>
        
        {settings.realTimeUpdates && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              Live Updates ({settings.updateInterval}s)
            </div>
            {countdown > 0 && (
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
                <span className="text-xs font-medium text-primary">
                  Next update in
                </span>
                <span className="text-sm font-bold text-primary tabular-nums">
                  {countdown}s
                </span>
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="space-y-4">
        {stocks.map((stock) => (
          <StockCard 
            key={stock.symbol} 
            stock={stock} 
            timeframe={settings.chartTimeframe}
            onClick={() => onStockClick?.(stock)}
            onAIAnalysisClick={onAIAnalysisClick}
          />
        ))}
      </div>
    </div>
  )
}

import { useState, useEffect, useCallback, useRef } from 'react'
import { Toaster, toast } from 'sonner'
import { Settings, TrendingUp, RefreshCw, Play, Pause, Search, X } from 'lucide-react'
import StockScanner from './components/StockScanner'
import SimulatedScanner from './components/SimulatedScanner'
import SettingsPanel from './components/SettingsPanel'
import StockDetailModal from './components/StockDetailModal'
import NewsSection from './components/NewsSection'
import { scanStocks, getStock } from './api/stockApi'
import { Stock, ScannerSettings } from './types'
import { detectPatterns, getLatestSignal } from './utils/candlestickPatterns'
import './App.css'

type ViewMode = 'live' | 'simulated'

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('simulated') // Start on simulated for demo
  const [stocks, setStocks] = useState<Stock[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [countdown, setCountdown] = useState<number>(0)
  const [searchSymbol, setSearchSymbol] = useState<string>('')
  const [isSearching, setIsSearching] = useState<boolean>(false)
  // IBKR only mode - no rate limits, removed rate limit state
  const [refreshCooldown, setRefreshCooldown] = useState<number>(0)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const countdownRef = useRef<NodeJS.Timeout | null>(null)
  // Removed readyTimerRef - no rate limit countdown needed
  const refreshCooldownRef = useRef<NodeJS.Timeout | null>(null)
  const previousStocksRef = useRef<Set<string>>(new Set())
  
  const [settings, setSettings] = useState<ScannerSettings>({
    minPrice: 1,
    maxPrice: 6,
    maxFloat: 10_000_000, // 10M shares - low float for volatile stocks
    minGainPercent: 10, // 10% - only explosive movers
    volumeMultiplier: 4, // 4x - EXPLOSIVE volume only
    displayCount: 10, // Show 10 stocks
    chartTimeframe: '5m',
    autoAdd: true,
    realTimeUpdates: true, // AUTO-SCAN ENABLED - dynamically adjusts to API availability
    updateInterval: 12, // 12 seconds - update interval
    notificationsEnabled: true,
    notifyOnNewStocks: true,
    // API Selection - Default: Yahoo only (most reliable)
    useYahoo: true,
    useSerpAPI: false,
    useAlphaVantage: false,
    useMassive: false,
  })

  // IBKR only mode - no rate limits, clear any saved rate limit state
  useEffect(() => {
    // Clear any old rate limit state (from previous API modes)
    localStorage.removeItem('rateLimitedUntil')
    // Removed setRateLimited and setReadyTime - no longer needed in IBKR-only mode
  }, [])

  const performScan = useCallback(async () => {
    // IBKR only mode - no rate limits, always allow scanning
    try {
      const result = await scanStocks(settings)
      
      if (result.success) {
        const newStocks = result.stocks || []
        
        // 🧠 AI PATTERN DETECTION: Analyze candlestick patterns on real stocks
        const stocksWithPatterns = newStocks.map(stock => {
          if (stock.chartData && stock.chartData[settings.chartTimeframe]) {
            const candles = stock.chartData[settings.chartTimeframe]
            
            if (candles && candles.length >= 3) {
              // Detect patterns in the chart data
              const patterns = detectPatterns(candles)
              const latestPattern = patterns.length > 0 ? patterns[patterns.length - 1] : null
              
              if (latestPattern) {
                // Update stock signal based on detected pattern (if HIGH confidence)
                let updatedSignal = stock.signal
                if (latestPattern.confidence === 'HIGH') {
                  updatedSignal = latestPattern.signal
                } else if (latestPattern.confidence === 'MEDIUM' && !stock.signal) {
                  updatedSignal = latestPattern.signal
                }
                
                return {
                  ...stock,
                  signal: updatedSignal,
                  detectedPattern: {
                    name: latestPattern.pattern,
                    signal: latestPattern.signal,
                    confidence: latestPattern.confidence,
                    description: latestPattern.description
                  }
                }
              }
            }
          }
          
          return stock
        })
        
        // IBKR only mode - no rate limits, always clear any rate limit state
        // IBKR only mode - no rate limits, removed rate limit state
        localStorage.removeItem('rateLimitedUntil')
        
        // Check for new stocks (silent - no popups)
        if (settings.notificationsEnabled && settings.notifyOnNewStocks) {
          const currentSymbols = new Set(stocksWithPatterns.map(s => s.symbol))
          const newSymbols = Array.from(currentSymbols).filter(
            symbol => !previousStocksRef.current.has(symbol)
          )
          
          if (newSymbols.length > 0 && previousStocksRef.current.size > 0) {
            // Log new stocks to console instead of showing popup
            newSymbols.forEach(symbol => {
              const stock = stocksWithPatterns.find(s => s.symbol === symbol)
              if (stock) {
                console.log(`🆕 New stock: ${symbol} - ${stock.changePercent.toFixed(2)}% gain`)
              }
            })
          }
          
          previousStocksRef.current = currentSymbols
        }
        
        setStocks(stocksWithPatterns)
        setLastUpdate(new Date())
      } else {
        // Handle failed scan (e.g., timeout)
        console.warn('Scan failed:', result.error || 'Unknown error')
        // Keep existing stocks, don't clear them on timeout
      }
    } catch (error: any) {
      console.error('Scan error:', error)
      // IBKR only mode - log error but don't show popup
      // Errors are logged to console for debugging
      // Keep existing stocks on error
    } finally {
      // Always reset loading state, even on timeout/error
      setIsLoading(false)
    }
  }, [settings])

  // Don't auto-scan on mount - wait for user to start
  // User must click Start/Play, Refresh, or apply preset/settings

  // IBKR only mode - no rate limits, no countdown needed
  // Removed rate limit countdown timer

  useEffect(() => {
    if (settings.realTimeUpdates) {
      // Set initial countdown
      setCountdown(settings.updateInterval)
      
      // Main scan interval
      intervalRef.current = setInterval(() => {
        performScan()
      }, settings.updateInterval * 1000) // Convert seconds to milliseconds
      
      // Countdown timer (updates every second)
      countdownRef.current = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            return settings.updateInterval
          }
          return prev - 1
        })
      }, 1000)
      
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
        }
        if (countdownRef.current) {
          clearInterval(countdownRef.current)
        }
      }
    } else {
      setCountdown(0)
    }
  }, [settings.realTimeUpdates, settings.updateInterval, performScan])

  // Refresh cooldown timer
  useEffect(() => {
    if (refreshCooldown > 0) {
      refreshCooldownRef.current = setInterval(() => {
        setRefreshCooldown(prev => {
          if (prev <= 1) {
            return 0
          }
          return prev - 1
        })
      }, 1000)
      
      return () => {
        if (refreshCooldownRef.current) {
          clearInterval(refreshCooldownRef.current)
        }
      }
    }
  }, [refreshCooldown])

  const handleRefresh = () => {
    // Manual refresh - scan immediately and start 20s lockout
    setIsLoading(true)
    performScan()
    
    // Start 20-second cooldown lockout
    setRefreshCooldown(20)
  }

  const handleSettingsUpdate = (newSettings: ScannerSettings) => {
    setSettings(newSettings)
    setIsLoading(true)
    previousStocksRef.current.clear()
    // Start scanning when settings are applied
    performScan()
  }

  const toggleAutoRefresh = () => {
    const newSettings = { ...settings, realTimeUpdates: !settings.realTimeUpdates }
    setSettings(newSettings)
    // No popup notifications - silent toggle
  }

  const handleSearchStock = async () => {
    if (!searchSymbol.trim()) {
      toast.error('Please enter a stock symbol')
      return
    }

    const symbol = searchSymbol.trim().toUpperCase()
    setIsSearching(true)

    // Show loading message with green indicator
    const loadingToast = toast.loading(`🔍 Searching for ${symbol}... This may take 30-60 seconds.`, {
      description: 'The search button will turn green while searching'
    })

    try {
      const stock = await getStock(symbol, settings.chartTimeframe)
      toast.dismiss(loadingToast)
      setSelectedStock(stock)
      setSearchSymbol('')
      toast.success(`✅ Found ${symbol} - ${stock.name || symbol}`, {
        description: `Price: $${stock.currentPrice} | Change: ${stock.changePercent?.toFixed(2)}%`
      })
    } catch (error: any) {
      console.error('Error searching stock:', error)
      toast.dismiss(loadingToast)
      
      // Provide more specific error messages
      let errorMessage = `Could not find stock: ${symbol}`
      
      if (error.message?.includes('timeout') || error.code === 'ECONNABORTED') {
        errorMessage = `Request timed out for ${symbol}. IBKR may be slow or the symbol may not be available. Try again or check if IBKR is connected.`
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.message) {
        errorMessage = error.message
      }
      
      toast.error(`❌ ${errorMessage}`, {
        duration: 5000
      })
    } finally {
      setIsSearching(false)
    }
  }

  const handleSearchKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearchStock()
    }
  }

  // Removed formatCountdown - no rate limit countdown needed

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Toaster position="top-right" richColors />
      
      {/* IBKR only mode - no rate limit banners */}
      
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-40">
        <div className="container mx-auto px-3 sm:px-4 py-3 sm:py-4">
          {/* Stock Search Bar - Top of page */}
          <div className="mb-3 pb-3 border-b border-border">
            <div className="flex items-center gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  value={searchSymbol}
                  onChange={(e) => setSearchSymbol(e.target.value.toUpperCase())}
                  onKeyPress={handleSearchKeyPress}
                  placeholder="Search stock symbol (e.g., AAPL, TSLA, GME)..."
                  className="w-full pl-10 pr-10 py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  disabled={isSearching}
                />
                {searchSymbol && (
                  <button
                    onClick={() => setSearchSymbol('')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    aria-label="Clear search"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
              <button
                onClick={handleSearchStock}
                disabled={isSearching || !searchSymbol.trim()}
                className={`px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 ${
                  isSearching 
                    ? 'bg-green-500 text-white hover:bg-green-600' 
                    : 'bg-primary text-primary-foreground hover:bg-primary/90'
                }`}
              >
                {isSearching ? (
                  <>
                    <div className="w-2 h-2 rounded-full bg-white animate-pulse mr-1" />
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span className="hidden sm:inline">Searching {searchSymbol}...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span className="hidden sm:inline">Search</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* View Mode Tabs */}
          <div className="flex items-center gap-2 mb-3 pb-3 border-b border-border">
            <button
              onClick={() => setViewMode('simulated')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-medium ${
                viewMode === 'simulated'
                  ? 'bg-purple-500 text-white'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              🎮 Simulated Demo
            </button>
            <button
              onClick={() => setViewMode('live')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-medium ${
                viewMode === 'live'
                  ? 'bg-green-500 text-white'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              📡 Live Scanner
            </button>
            {viewMode === 'simulated' && (
              <div className="ml-auto text-xs text-muted-foreground bg-purple-500/10 px-3 py-1.5 rounded-lg border border-purple-500/20">
                ✨ <strong>Demo Mode:</strong> Test the new Bookmap-style charts with simulated data
              </div>
            )}
          </div>
          
          <div className="flex items-center justify-between">
            {/* Logo & Title - Responsive */}
            <div className="flex items-center gap-2 sm:gap-3 min-w-0">
              <div className="flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-primary flex-shrink-0">
                <TrendingUp className="w-4 h-4 sm:w-6 sm:h-6 text-primary-foreground" />
              </div>
              <div className="min-w-0">
                <h1 className="text-lg sm:text-2xl font-bold truncate">
                  Stock Scanner {viewMode === 'simulated' && <span className="text-purple-500">• Demo</span>}
                </h1>
                <p className="text-xs sm:text-sm text-muted-foreground hidden sm:block">
                  {viewMode === 'simulated' 
                    ? 'Interactive demo with simulated data - test all features!'
                    : 'Real-time low-float, high-volume discovery'
                  }
                </p>
              </div>
            </div>
            
            {/* Actions - Responsive (only show in live mode) */}
            {viewMode === 'live' && (
              <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                {/* Last Update - Hidden on mobile */}
                <div className="text-right mr-2 hidden md:block">
                  <p className="text-xs text-muted-foreground">Last Update</p>
                  <p className="text-sm font-medium flex items-center gap-2">
                    {lastUpdate.toLocaleTimeString()}
                    {isLoading && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/20 text-xs text-primary">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                        Scanning...
                      </span>
                    )}
                  </p>
                </div>
                
                {/* Auto-Refresh Toggle */}
                <button
                  onClick={toggleAutoRefresh}
                  className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 rounded-lg transition-colors ${
                    settings.realTimeUpdates 
                      ? 'bg-green-500 text-white hover:bg-green-600' 
                      : 'bg-muted text-muted-foreground hover:bg-muted/80'
                  }`}
                  title={settings.realTimeUpdates ? 'Pause auto-refresh' : 'Start auto-refresh'}
                >
                  {settings.realTimeUpdates ? (
                    <>
                      <Pause className="w-4 h-4" />
                      <span className="hidden sm:inline text-sm font-medium">Pause</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span className="hidden sm:inline text-sm font-medium">Start</span>
                    </>
                  )}
                </button>
                
                {/* Refresh Button */}
                <button
                  onClick={handleRefresh}
                  disabled={refreshCooldown > 0}
                  className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Refresh"
                  title={
                    refreshCooldown > 0
                      ? `⏳ Cooldown: ${refreshCooldown}s`
                      : isLoading
                      ? 'Scanning...'
                      : 'Refresh stock data now'
                  }
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                  <span className="hidden sm:inline">
                    {refreshCooldown > 0 ? `${refreshCooldown}s` : isLoading ? 'Scanning...' : 'Refresh'}
                  </span>
                </button>
              </div>
            )}
            
            {/* Settings Button - Always visible */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 rounded-lg bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors"
              aria-label="Settings"
            >
              <Settings className="w-4 h-4" />
              <span className="hidden sm:inline">Settings</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-3 sm:px-4 py-4 sm:py-6">
        <div className="flex flex-col gap-4 sm:gap-6">
          <div className="flex flex-col lg:flex-row gap-4 sm:gap-6">
            {/* Scanner Results */}
            <div className="flex-1 min-w-0">
              {viewMode === 'simulated' ? (
                <SimulatedScanner liveStocks={stocks} />
              ) : (
                <StockScanner 
                  stocks={stocks} 
                  isLoading={isLoading}
                  settings={settings}
                  countdown={countdown}
                  onStockClick={(stock) => setSelectedStock(stock)}
                />
              )}
            </div>
          
          {/* Settings Sidebar - Mobile Overlay / Desktop Sidebar */}
          {showSettings && (
            <>
              {/* Mobile Overlay */}
              <div 
                className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                onClick={() => setShowSettings(false)}
              />
              
              {/* Settings Panel */}
              <div className="fixed inset-x-0 bottom-0 lg:relative lg:w-96 z-50 max-h-[80vh] lg:max-h-none overflow-y-auto">
                <SettingsPanel 
                  settings={settings}
                  onSettingsChange={handleSettingsUpdate}
                  onClose={() => setShowSettings(false)}
                  isRateLimited={false}
                  readyCountdown={0}
                />
              </div>
            </>
          )}
          </div>
          
          {/* News Section - Shows news found for stocks that qualified */}
          <NewsSection />
        </div>
      </main>

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

export default App

import { useState, useEffect, useCallback, useRef } from 'react'
import { Toaster, toast } from 'sonner'
import { Settings, TrendingUp, RefreshCw, Play, Pause } from 'lucide-react'
import StockScanner from './components/StockScanner'
import SimulatedScanner from './components/SimulatedScanner'
import SettingsPanel from './components/SettingsPanel'
import StockDetailModal from './components/StockDetailModal'
import { scanStocks } from './api/stockApi'
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
  const [rateLimited, setRateLimited] = useState(false)
  const [readyTime, setReadyTime] = useState<Date | null>(null)
  const [readyCountdown, setReadyCountdown] = useState<number>(0)
  const [refreshCooldown, setRefreshCooldown] = useState<number>(0)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const countdownRef = useRef<NodeJS.Timeout | null>(null)
  const readyTimerRef = useRef<NodeJS.Timeout | null>(null)
  const refreshCooldownRef = useRef<NodeJS.Timeout | null>(null)
  const previousStocksRef = useRef<Set<string>>(new Set())
  
  const [settings, setSettings] = useState<ScannerSettings>({
    minPrice: 1,
    maxPrice: 20,
    maxFloat: 10_000_000, // 10M shares - LOW-FLOAT for volatile stocks (displays as "10M")
    minGainPercent: 10, // 10% - only explosive movers (adjust lower in settings for more stocks)
    volumeMultiplier: 5, // 5x - EXPLOSIVE volume only (adjust lower in settings for more stocks)
    displayCount: 10, // Show all 10 symbols if they qualify
    chartTimeframe: '5m',
    autoAdd: true,
    realTimeUpdates: false, // Start paused - user must click Start or Refresh
    updateInterval: 20, // 20 seconds - FASTEST safe interval (1,800 req/hr, 200 buffer)
    notificationsEnabled: true,
    notifyOnNewStocks: true,
  })

  // Check for saved rate limit on mount AND verify with backend
  useEffect(() => {
    const checkLockoutStatus = async () => {
      const savedRateLimitUntil = localStorage.getItem('rateLimitedUntil')
      if (savedRateLimitUntil) {
        const readyAt = new Date(savedRateLimitUntil)
        const now = Date.now()
        
        // If still rate limited, restore the state
        if (readyAt.getTime() > now) {
          setRateLimited(true)
          setReadyTime(readyAt)
          console.log('Restored rate limit state from localStorage:', readyAt.toLocaleTimeString())
        } else {
          // Rate limit expired, clear localStorage
          localStorage.removeItem('rateLimitedUntil')
        }
      }
      
      // ALWAYS check backend status on mount to see if fallback API is available
      try {
        const testScan = await scanStocks({
          minPrice: 1,
          maxPrice: 20,
          maxFloat: 10000000,
          minGainPercent: 100, // High threshold to get quick empty response
          volumeMultiplier: 100,
          chartTimeframe: '5m',
          displayCount: 1
        })
        
        // If scan succeeded, backend has working API (Yahoo or SerpAPI)
        if (testScan.apiStatus && !testScan.apiStatus.yahooLocked) {
          console.log('✅ Backend has working API - clearing frontend lockout')
          setRateLimited(false)
          setReadyTime(null)
          localStorage.removeItem('rateLimitedUntil')
        }
      } catch (error) {
        console.log('Backend status check failed:', error)
      }
    }
    
    checkLockoutStatus()
  }, [])

  const performScan = useCallback(async () => {
    // Prevent scanning if rate limited
    if (rateLimited && readyCountdown > 0) {
      console.log('Scan blocked - rate limited')
      return
    }
    
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
        
        // Check backend API status and update lockout state
        if (data.apiStatus) {
          // Backend is using SerpAPI or Yahoo is unlocked
          if (!data.apiStatus.yahooLocked || data.apiStatus.serpapiQuota.remaining > 0) {
            // Clear frontend lockout - backend has fallback working
            setRateLimited(false)
            setReadyTime(null)
            localStorage.removeItem('rateLimitedUntil')
            console.log(`✅ Backend using ${data.apiStatus.activeSource} - Frontend unlocked`)
          }
        } else {
          // Old API response format - clear rate limit if scan succeeded
          setRateLimited(false)
          setReadyTime(null)
          localStorage.removeItem('rateLimitedUntil')
        }
        
        // Check for new stocks
        if (settings.notificationsEnabled && settings.notifyOnNewStocks) {
          const currentSymbols = new Set(stocksWithPatterns.map(s => s.symbol))
          const newSymbols = Array.from(currentSymbols).filter(
            symbol => !previousStocksRef.current.has(symbol)
          )
          
          if (newSymbols.length > 0 && previousStocksRef.current.size > 0) {
            newSymbols.forEach(symbol => {
              const stock = stocksWithPatterns.find(s => s.symbol === symbol)
              if (stock) {
                // Enhanced notification with pattern detection
                let description = `${symbol} now qualifies - ${stock.changePercent.toFixed(2)}% gain`
                if ((stock as any).detectedPattern) {
                  const pattern = (stock as any).detectedPattern
                  description += ` 🧠 Pattern: ${pattern.name} (${pattern.signal})`
                }
                
                toast.success(`New Stock Alert!`, {
                  description
                })
              }
            })
          }
          
          previousStocksRef.current = currentSymbols
        }
        
        setStocks(stocksWithPatterns)
        setLastUpdate(new Date())
      }
    } catch (error: any) {
      console.error('Scan error:', error)
      
      // Check if it's a rate limit error
      if (error?.isRateLimit || error?.message?.includes('429') || error?.message?.includes('Too Many Requests') || error?.message?.includes('Rate Limited')) {
        // Only lock if BOTH Yahoo and SerpAPI failed (true lockout)
        // If backend has fallback, don't lock frontend
        setRateLimited(true)
        const readyAt = new Date(Date.now() + 120 * 60 * 1000) // 2 hours from now
        setReadyTime(readyAt)
        
        // Save rate limit to localStorage
        localStorage.setItem('rateLimitedUntil', readyAt.toISOString())
        
        toast.error('Rate Limit Detected', {
          description: `⚠️ Backend is switching to fallback API (SerpAPI). Scanner may still work!`,
          duration: 8000
        })
      } else {
        toast.error('Failed to scan stocks', {
          description: 'Please check your connection and try again'
        })
      }
    } finally {
      setIsLoading(false)
    }
  }, [settings, rateLimited, readyCountdown])

  // Don't auto-scan on mount - wait for user to start
  // User must click Start/Play, Refresh, or apply preset/settings

  // Ready time countdown
  useEffect(() => {
    if (readyTime) {
      const updateReadyCountdown = () => {
        const now = Date.now()
        const ready = readyTime.getTime()
        const remaining = Math.max(0, Math.floor((ready - now) / 1000))
        setReadyCountdown(remaining)
        
        if (remaining === 0) {
          // Don't clear immediately - show green "Ready!" banner for 10 seconds
          setTimeout(() => {
            setRateLimited(false)
            setReadyTime(null)
            localStorage.removeItem('rateLimitedUntil')
          }, 10000)
          
          toast.success('Scanner Ready!', {
            description: 'Rate limit cleared! You can start scanning now.',
            duration: 10000
          })
        }
      }
      
      updateReadyCountdown()
      readyTimerRef.current = setInterval(updateReadyCountdown, 1000)
      
      return () => {
        if (readyTimerRef.current) {
          clearInterval(readyTimerRef.current)
        }
      }
    }
  }, [readyTime])

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
    
    if (!settings.realTimeUpdates) {
      // Turning ON - show notification
      toast.success('Auto-Refresh Enabled', {
        description: `Scanning every ${settings.updateInterval} seconds`
      })
    } else {
      // Turning OFF - show notification
      toast.info('Auto-Refresh Paused', {
        description: 'Click Refresh button to scan manually'
      })
    }
  }

  // Format countdown timer to show hours:minutes:seconds for long waits
  const formatCountdown = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      // Show hours:minutes:seconds for countdowns over 1 hour
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    } else {
      // Show minutes:seconds for countdowns under 1 hour
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Toaster position="top-right" richColors />
      
      {/* Rate Limit Banner */}
      {rateLimited && readyTime && readyCountdown > 0 && (
        <div className="bg-red-500/10 border-b-4 border-red-500/40 sticky top-0 z-50">
          <div className="container mx-auto px-3 sm:px-4 py-3 sm:py-4">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                  <span className="text-sm font-semibold text-red-600 dark:text-red-400">
                    🔒 LOCKED - Yahoo Finance Rate Limit (2 Hour Minimum)
                  </span>
                </div>
                <div className="flex flex-col sm:flex-row items-end sm:items-center gap-2 sm:gap-3">
                  <div className="flex flex-col items-end">
                    <span className="text-xs font-medium text-red-700 dark:text-red-300">
                      Ready at: {readyTime.toLocaleTimeString()}
                    </span>
                    <span className="text-xs text-red-600/70 dark:text-red-400/70">
                      {Math.floor(readyCountdown / 3600) > 0 
                        ? `${Math.floor(readyCountdown / 3600)} hour${Math.floor(readyCountdown / 3600) !== 1 ? 's' : ''} ${Math.floor((readyCountdown % 3600) / 60)} min remaining`
                        : `${Math.floor(readyCountdown / 60)} minutes remaining`
                      }
                    </span>
                  </div>
                  <div className="px-4 py-1.5 rounded-full bg-red-500/20 border-2 border-red-500/40">
                    <span className="text-base font-bold text-red-600 dark:text-red-400 tabular-nums">
                      ⏱️ {formatCountdown(readyCountdown)}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-xs text-red-600 dark:text-red-400 bg-red-500/5 px-3 py-2 rounded border border-red-500/20">
                ⚠️ <strong>IMPORTANT:</strong> If the timer reaches 0 and you still get blocked, Yahoo's actual limit may be 3-6 hours or even 24 hours for your IP. Wait longer or you'll reset the lockout!
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Ready Banner */}
      {rateLimited && readyTime && readyCountdown === 0 && (
        <div className="bg-green-500/10 border-b-4 border-green-500/40 sticky top-0 z-50 animate-pulse">
          <div className="container mx-auto px-3 sm:px-4 py-3 sm:py-4">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-ping" />
                  <span className="text-sm font-bold text-green-600 dark:text-green-400">
                    ✅ 2-Hour Timer Complete - Test Carefully!
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs font-medium text-green-700 dark:text-green-300">
                    You may try scanning now, but proceed with caution
                  </span>
                  <div className="px-4 py-1.5 rounded-full bg-green-500/20 border-2 border-green-500/40">
                    <span className="text-base font-bold text-green-600 dark:text-green-400">
                      ✅ READY
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-xs text-yellow-600 dark:text-yellow-400 bg-yellow-500/5 px-3 py-2 rounded border border-yellow-500/20">
                ⚠️ <strong>TIP:</strong> If you get blocked again immediately, Yahoo may require 3-6 hours or 24 hours. Consider using fewer symbols (5-10) or longer scan intervals (30-60s) to avoid future rate limits.
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-40">
        <div className="container mx-auto px-3 sm:px-4 py-3 sm:py-4">
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
                  disabled={rateLimited && readyCountdown > 0}
                  className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed ${
                    settings.realTimeUpdates 
                      ? 'bg-green-500 text-white hover:bg-green-600' 
                      : 'bg-muted text-muted-foreground hover:bg-muted/80'
                  }`}
                  title={
                    rateLimited && readyCountdown > 0 
                      ? `Locked until rate limit clears (${Math.floor(readyCountdown / 60)}:${(readyCountdown % 60).toString().padStart(2, '0')})` 
                      : settings.realTimeUpdates ? 'Pause auto-refresh' : 'Start auto-refresh'
                  }
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
                  disabled={(rateLimited && readyCountdown > 0) || refreshCooldown > 0}
                  className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Refresh"
                  title={
                    rateLimited && readyCountdown > 0
                      ? `🔒 Rate Limited - Wait ${Math.floor(readyCountdown / 60)}:${(readyCountdown % 60).toString().padStart(2, '0')}`
                      : refreshCooldown > 0
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
                  isRateLimited={rateLimited && readyCountdown > 0}
                  readyCountdown={readyCountdown}
                />
              </div>
            </>
          )}
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

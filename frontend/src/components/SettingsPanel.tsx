import { useState, useEffect } from 'react'
import { ScannerSettings, ChartTimeframe } from '../types'
import { X, DollarSign, TrendingUp, BarChart3, Bell, Clock, Hash, HelpCircle, Globe, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import FAQSection from './FAQSection'

// Helper function to check preset status
function getPresetStatus(settings: ScannerSettings): {
  float: 'good' | 'wont-work' | 'ok'
  gain: 'good' | 'wont-work' | 'ok'
  volume: 'good' | 'wont-work' | 'ok'
  displayCount: 'good' | 'wont-work' | 'ok'
  timeframe: 'good' | 'wont-work' | 'ok'
  priceRange: 'good' | 'wont-work' | 'ok'
} {
  return {
    // Float filter - IBKR doesn't provide, so it won't work
    float: 'wont-work',
    
    // Gain filter - Good if 5%+, OK if 3-5%, Won't work if negative
    gain: settings.minGainPercent < 0 ? 'wont-work' : 
          settings.minGainPercent >= 5 ? 'good' : 
          settings.minGainPercent >= 3 ? 'ok' : 'ok',
    
    // Volume multiplier - Good if 2x+, OK if 1.5-2x, Won't work if < 1x
    volume: settings.volumeMultiplier < 1 ? 'wont-work' :
            settings.volumeMultiplier >= 2 ? 'good' :
            settings.volumeMultiplier >= 1.5 ? 'ok' : 'ok',
    
    // Display count - Good if 5-10, OK if 10-20, Won't work if > 20
    displayCount: settings.displayCount > 20 ? 'wont-work' :
                   settings.displayCount >= 5 && settings.displayCount <= 10 ? 'good' :
                   settings.displayCount > 10 && settings.displayCount <= 20 ? 'ok' : 'ok',
    
    // Timeframe - Good if 5m+, OK if 1m-3m, Won't work if invalid
    timeframe: ['1m', '2m'].includes(settings.chartTimeframe) ? 'ok' :
               ['5m', '15m', '30m', '1h', '24h'].includes(settings.chartTimeframe) ? 'good' : 'ok',
    
    // Price range - Good if reasonable ($1-$50), OK if wider, Won't work if too wide
    priceRange: (settings.maxPrice - settings.minPrice) > 1000 ? 'wont-work' :
                settings.minPrice >= 1 && settings.maxPrice <= 50 ? 'good' :
                settings.minPrice >= 0.05 && settings.maxPrice <= 100 ? 'ok' : 'ok'
  }
}

function PresetStatusBadge({ status, message }: { status: 'good' | 'wont-work' | 'ok', message: string }) {
  if (status === 'good') {
    return (
      <div className="flex items-center gap-1 text-xs text-green-500 mt-1">
        <CheckCircle className="w-3 h-3" />
        <span>{message}</span>
      </div>
    )
  } else if (status === 'wont-work') {
    return (
      <div className="flex items-center gap-1 text-xs text-red-500 mt-1">
        <XCircle className="w-3 h-3" />
        <span>{message}</span>
      </div>
    )
  } else {
    return (
      <div className="flex items-center gap-1 text-xs text-yellow-500 mt-1">
        <AlertTriangle className="w-3 h-3" />
        <span>{message}</span>
      </div>
    )
  }
}

interface SettingsPanelProps {
  settings: ScannerSettings
  onSettingsChange: (settings: ScannerSettings) => void
  onClose: () => void
  isRateLimited?: boolean
  readyCountdown?: number
}

// Helper function to check if US stock market is open
function isMarketOpen(): { isOpen: boolean; message: string } {
  const now = new Date()
  const day = now.getDay() // 0 = Sunday, 6 = Saturday
  const hour = now.getHours()
  const minute = now.getMinutes()
  
  // Market is closed on weekends
  if (day === 0 || day === 6) {
    return { 
      isOpen: false, 
      message: day === 0 ? 'Market closed (Sunday)' : 'Market closed (Saturday)' 
    }
  }
  
  // Convert to ET (simplified - assumes server/client is in ET or adjust accordingly)
  // Market hours: 9:30 AM - 4:00 PM ET (14:30 - 20:00 UTC)
  // For simplicity, we'll check local time (user should be aware of timezone)
  const marketOpenHour = 9
  const marketOpenMinute = 30
  const marketCloseHour = 16
  const marketCloseMinute = 0
  
  const currentTime = hour * 60 + minute
  const openTime = marketOpenHour * 60 + marketOpenMinute
  const closeTime = marketCloseHour * 60 + marketCloseMinute
  
  if (currentTime < openTime) {
    const hoursUntilOpen = Math.floor((openTime - currentTime) / 60)
    const minutesUntilOpen = (openTime - currentTime) % 60
    return { 
      isOpen: false, 
      message: `Market closed - Opens in ${hoursUntilOpen}h ${minutesUntilOpen}m` 
    }
  }
  
  if (currentTime >= closeTime) {
    return { 
      isOpen: false, 
      message: 'Market closed (After hours)' 
    }
  }
  
  return { isOpen: true, message: 'Market is open' }
}

// Helper function to check API lockout status
function getApiLockoutStatus(): Record<string, { locked: boolean; unlockAt: number | null }> {
  const lockouts: Record<string, { locked: boolean; unlockAt: number | null }> = {
    yahoo: { locked: false, unlockAt: null },
    serpapi: { locked: false, unlockAt: null },
    alphavantage: { locked: false, unlockAt: null },
    massive: { locked: false, unlockAt: null },
  }
  
  const now = Date.now()
  const LOCKOUT_DURATION = 24 * 60 * 60 * 1000 // 24 hours in milliseconds
  
  // Check localStorage for lockout timestamps
  const yahooLockout = localStorage.getItem('api_lockout_yahoo')
  const serpapiLockout = localStorage.getItem('api_lockout_serpapi')
  const alphavantageLockout = localStorage.getItem('api_lockout_alphavantage')
  const massiveLockout = localStorage.getItem('api_lockout_massive')
  
  if (yahooLockout) {
    const unlockTime = parseInt(yahooLockout)
    if (now < unlockTime) {
      lockouts.yahoo = { locked: true, unlockAt: unlockTime }
    } else {
      localStorage.removeItem('api_lockout_yahoo')
    }
  }
  
  if (serpapiLockout) {
    const unlockTime = parseInt(serpapiLockout)
    if (now < unlockTime) {
      lockouts.serpapi = { locked: true, unlockAt: unlockTime }
    } else {
      localStorage.removeItem('api_lockout_serpapi')
    }
  }
  
  if (alphavantageLockout) {
    const unlockTime = parseInt(alphavantageLockout)
    if (now < unlockTime) {
      lockouts.alphavantage = { locked: true, unlockAt: unlockTime }
    } else {
      localStorage.removeItem('api_lockout_alphavantage')
    }
  }
  
  if (massiveLockout) {
    const unlockTime = parseInt(massiveLockout)
    if (now < unlockTime) {
      lockouts.massive = { locked: true, unlockAt: unlockTime }
    } else {
      localStorage.removeItem('api_lockout_massive')
    }
  }
  
  return lockouts
}

// Helper function to lock an API for 24 hours
export function lockApi(apiName: 'yahoo' | 'serpapi' | 'alphavantage' | 'massive') {
  const unlockTime = Date.now() + (24 * 60 * 60 * 1000) // 24 hours from now
  localStorage.setItem(`api_lockout_${apiName}`, unlockTime.toString())
}

export default function SettingsPanel({ settings, onSettingsChange, onClose, isRateLimited = false, readyCountdown = 0 }: SettingsPanelProps) {
  const [localSettings, setLocalSettings] = useState(settings)
  const [floatDisplayValue, setFloatDisplayValue] = useState(formatFloatHelper(settings.maxFloat))
  const [activeTab, setActiveTab] = useState<'settings' | 'faq'>('settings')
  const [marketStatus, setMarketStatus] = useState(isMarketOpen())
  const [apiLockouts, setApiLockouts] = useState(getApiLockoutStatus())
  
  // Update market status and API lockouts every second for countdown
  useEffect(() => {
    const interval = setInterval(() => {
      setMarketStatus(isMarketOpen())
      setApiLockouts(getApiLockoutStatus()) // Update lockout status every second for countdown
    }, 1000) // Update every second for smooth countdown
    
    return () => clearInterval(interval)
  }, [])
  
  // Format time remaining until unlock (with seconds for countdown)
  const getTimeUntilUnlock = (unlockAt: number | null): string => {
    if (!unlockAt) return ''
    const now = Date.now()
    const remaining = unlockAt - now
    if (remaining <= 0) return '0:00:00'
    
    const hours = Math.floor(remaining / (60 * 60 * 1000))
    const minutes = Math.floor((remaining % (60 * 60 * 1000)) / (60 * 1000))
    const seconds = Math.floor((remaining % (60 * 1000)) / 1000)
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    }
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }
  
  // Auto-update settings when API selection changes
  useEffect(() => {
    const hasYahoo = localSettings.useYahoo ?? true
    const hasSerpAPI = localSettings.useSerpAPI ?? false
    const hasAlphaVantage = localSettings.useAlphaVantage ?? false
    const hasMassive = localSettings.useMassive ?? false
    
    // Calculate recommended interval
    let recommendedInterval = 20
    if (hasMassive || hasAlphaVantage) {
      if (!hasYahoo && !hasSerpAPI) {
        recommendedInterval = 60 // Only Massive/AlphaVantage: 60s
      } else {
        recommendedInterval = 60 // Mixed: use 60s for safety
      }
    } else if (hasSerpAPI && !hasYahoo) {
      recommendedInterval = 120 // Only SerpAPI: 120s
    } else {
      recommendedInterval = 20 // Yahoo available: 20s
    }
    
    // Calculate recommended stock count
    let maxStocks = 10
    if (hasMassive || hasAlphaVantage) {
      maxStocks = 5 // 5 calls/min limit
    } else if (hasSerpAPI && !hasYahoo) {
      maxStocks = 10 // SerpAPI can handle 10
    } else {
      maxStocks = 10 // Yahoo allows 10
    }
    
    // Update settings if they don't match recommendations
    if (localSettings.updateInterval !== recommendedInterval || 
        (localSettings.displayCount || 10) > maxStocks) {
      setLocalSettings(prev => ({
        ...prev,
        updateInterval: recommendedInterval,
        displayCount: Math.min(prev.displayCount || 10, maxStocks)
      }))
    }
  }, [localSettings.useYahoo, localSettings.useSerpAPI, localSettings.useAlphaVantage, localSettings.useMassive])

  // Format number to K/M format
  function formatFloatHelper(value: number): string {
    if (value >= 1_000_000) {
      const millions = value / 1_000_000
      return millions % 1 === 0 ? `${millions}M` : `${millions.toFixed(1)}M`
    } else if (value >= 1_000) {
      const thousands = value / 1_000
      return thousands % 1 === 0 ? `${thousands}K` : `${thousands.toFixed(1)}K`
    }
    return value.toString()
  }

  // Parse K/M format to number
  const parseFloatValue = (value: string): number => {
    const cleaned = value.trim().toUpperCase()
    
    if (cleaned.endsWith('M')) {
      return parseFloat(cleaned.slice(0, -1)) * 1_000_000
    } else if (cleaned.endsWith('K')) {
      return parseFloat(cleaned.slice(0, -1)) * 1_000
    }
    
    return parseFloat(cleaned) || 0
  }

  const handleChange = (key: keyof ScannerSettings, value: any) => {
    const newSettings = { ...localSettings, [key]: value }
    setLocalSettings(newSettings)
    
    // Auto-update settings when API selection changes
    if (key === 'useYahoo' || key === 'useSerpAPI' || key === 'useAlphaVantage' || key === 'useMassive') {
      // Calculate recommended values based on selected APIs
      const hasYahoo = newSettings.useYahoo ?? true
      const hasSerpAPI = newSettings.useSerpAPI ?? false
      const hasAlphaVantage = newSettings.useAlphaVantage ?? false
      const hasMassive = newSettings.useMassive ?? false
      
      // Calculate recommended interval
      let recommendedInterval = 20
      if (hasMassive || hasAlphaVantage) {
        if (!hasYahoo && !hasSerpAPI) {
          recommendedInterval = 60 // Only Massive/AlphaVantage: 60s
        } else {
          recommendedInterval = 60 // Mixed: use 60s for safety
        }
      } else if (hasSerpAPI && !hasYahoo) {
        recommendedInterval = 120 // Only SerpAPI: 120s
      } else {
        recommendedInterval = 20 // Yahoo available: 20s
      }
      
      // Calculate recommended stock count
      let maxStocks = 10
      if (hasMassive || hasAlphaVantage) {
        maxStocks = 5 // 5 calls/min limit
      } else if (hasSerpAPI && !hasYahoo) {
        maxStocks = 10 // SerpAPI can handle 10
      } else {
        maxStocks = 10 // Yahoo allows 10
      }
      
      // Auto-update the settings
      newSettings.updateInterval = recommendedInterval
      newSettings.displayCount = Math.min(newSettings.displayCount || 10, maxStocks)
      setLocalSettings(newSettings)
    }
  }

  const handleFloatChange = (value: string) => {
    setFloatDisplayValue(value)
    const numericValue = parseFloatValue(value)
    handleChange('maxFloat', numericValue)
  }

  const handleApply = () => {
    onSettingsChange(localSettings)
  }

  const handlePennyStockPreset = () => {
    const pennySettings: ScannerSettings = {
      minPrice: 0.05, // $0.05 - penny stock minimum
      maxPrice: 1, // $1.00 - penny stock maximum
      maxFloat: 100_000_000, // 100M shares - penny stocks have higher float
      minGainPercent: 10, // 10% - keep explosive movers
      volumeMultiplier: 5, // 5x - keep massive volume
      displayCount: 10, // Show all 10 tracked symbols
      chartTimeframe: '5m',
      autoAdd: true,
      realTimeUpdates: true,
      updateInterval: 20, // 20 seconds - fastest safe with 10 symbols
      notificationsEnabled: true,
      notifyOnNewStocks: true,
      useYahoo: localSettings.useYahoo ?? true,
      useSerpAPI: localSettings.useSerpAPI ?? false,
      useAlphaVantage: localSettings.useAlphaVantage ?? false,
      useMassive: localSettings.useMassive ?? false,
    }
    setLocalSettings(pennySettings)
    setFloatDisplayValue(formatFloatHelper(pennySettings.maxFloat))
    onSettingsChange(pennySettings)
  }

  const handleReset = () => {
    const defaultSettings: ScannerSettings = {
      minPrice: 1,
      maxPrice: 6,
      maxFloat: 10_000_000, // 10M shares - LOW-FLOAT for volatile stocks
      minGainPercent: 10, // 10% - only explosive movers
      volumeMultiplier: 4, // 4x - EXPLOSIVE volume only
      displayCount: 10, // Show all 10 tracked symbols
      chartTimeframe: '5m',
      autoAdd: true,
      realTimeUpdates: true,
      updateInterval: 12, // 12 seconds - update interval
      notificationsEnabled: true,
      notifyOnNewStocks: true,
      useYahoo: localSettings.useYahoo ?? true,
      useSerpAPI: localSettings.useSerpAPI ?? false,
      useAlphaVantage: localSettings.useAlphaVantage ?? false,
      useMassive: localSettings.useMassive ?? false,
    }
    setLocalSettings(defaultSettings)
    setFloatDisplayValue(formatFloatHelper(defaultSettings.maxFloat))
    onSettingsChange(defaultSettings)
  }

  return (
    <div className="rounded-t-xl lg:rounded-lg border border-border bg-card p-4 sm:p-6 lg:sticky lg:top-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg sm:text-xl font-bold">Scanner Settings</h2>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-muted transition-colors"
          aria-label="Close settings"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-border">
        <button
          onClick={() => setActiveTab('settings')}
          className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors relative ${
            activeTab === 'settings'
              ? 'text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Settings</span>
          {activeTab === 'settings' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>
          )}
        </button>
        <button
          onClick={() => setActiveTab('faq')}
          className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors relative ${
            activeTab === 'faq'
              ? 'text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <HelpCircle className="w-4 h-4" />
          <span>Help & FAQ</span>
          {activeTab === 'faq' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>
          )}
        </button>
      </div>

      {/* Settings Tab Content */}
      {activeTab === 'settings' && (
        <div className="space-y-6">
        {/* Price Range */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <DollarSign className="w-4 h-4" />
            Price Range
          </h3>
          <div className="space-y-3">
            <div>
              <InputField
                label="Minimum Price"
                type="number"
                value={localSettings.minPrice}
                onChange={(v) => handleChange('minPrice', parseFloat(v) || 0)}
                prefix="$"
              />
            </div>
            <div>
              <InputField
                label="Maximum Price"
                type="number"
                value={localSettings.maxPrice}
                onChange={(v) => handleChange('maxPrice', parseFloat(v) || 0)}
                prefix="$"
              />
            </div>
            {getPresetStatus(localSettings).priceRange === 'good' && (
              <PresetStatusBadge status="good" message="Good: Reasonable price range ($1-$50), won't hit rate limits" />
            )}
            {getPresetStatus(localSettings).priceRange === 'ok' && (
              <PresetStatusBadge status="ok" message="Okay: Wide range may find many stocks, monitor rate limits" />
            )}
            {getPresetStatus(localSettings).priceRange === 'wont-work' && (
              <PresetStatusBadge status="wont-work" message="Won't work: Range > $1000 will find too many stocks, rate limit risk" />
            )}
          </div>
        </section>

        {/* Stock Criteria */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <TrendingUp className="w-4 h-4" />
            Stock Criteria
          </h3>
          <div className="space-y-3">
            <div>
              <InputField
                label="Max Float (shares)"
                type="text"
                value={floatDisplayValue}
                onChange={handleFloatChange}
                helperText="Use M for millions, K for thousands (e.g., 10M, 500K)"
                placeholder="e.g., 10M or 10000000"
              />
              <PresetStatusBadge 
                status={getPresetStatus(localSettings).float} 
                message={getPresetStatus(localSettings).float === 'good' ? "Float data from Massive.com (if available)" : "Float data from Massive.com only - may not be available for all stocks"}
              />
            </div>
            <InputField
              label="Minimum Gain %"
              type="number"
              value={localSettings.minGainPercent}
              onChange={(v) => handleChange('minGainPercent', parseFloat(v) || 0)}
              suffix="%"
            />
            <div>
              <InputField
                label="Volume Multiplier"
                type="number"
                step="0.1"
                value={localSettings.volumeMultiplier}
                onChange={(v) => handleChange('volumeMultiplier', parseFloat(v) || 0)}
                suffix="x"
                helperText="Current vs average volume"
              />
              {getPresetStatus(localSettings).volume === 'good' && (
                <PresetStatusBadge status="good" message="Good: 2.0x+ filters well, reduces API calls" />
              )}
              {getPresetStatus(localSettings).volume === 'ok' && (
                <PresetStatusBadge status="ok" message="Okay: 1.5-2.0x may find many stocks, monitor rate limits" />
              )}
              {getPresetStatus(localSettings).volume === 'wont-work' && (
                <PresetStatusBadge status="wont-work" message="Won't work: Less than 1.0x doesn't filter anything" />
              )}
            </div>
          </div>
        </section>

        {/* Display Settings */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <BarChart3 className="w-4 h-4" />
            Display Settings
          </h3>
          <div className="space-y-3">
            <div>
              <InputField
                label="Number of Stocks"
                type="number"
                min="1"
                max="20"
                value={localSettings.displayCount}
                onChange={(v) => handleChange('displayCount', parseInt(v) || 1)}
              />
              {getPresetStatus(localSettings).displayCount === 'good' && (
                <PresetStatusBadge status="good" message="Good: 5-10 stocks optimal, fast scanning" />
              )}
              {getPresetStatus(localSettings).displayCount === 'ok' && (
                <PresetStatusBadge status="ok" message="Okay: 10-20 stocks may be slower, monitor performance" />
              )}
              {getPresetStatus(localSettings).displayCount === 'wont-work' && (
                <PresetStatusBadge status="wont-work" message="Won't work: 20+ stocks causes performance issues and rate limits" />
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Chart Timeframe
              </label>
              <select
                value={localSettings.chartTimeframe}
                onChange={(e) => handleChange('chartTimeframe', e.target.value as ChartTimeframe)}
                className="w-full px-3 py-2 rounded-lg bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="1m">1 minute</option>
                <option value="3m">3 minutes</option>
                <option value="5m">5 minutes</option>
                <option value="15m">15 minutes</option>
                <option value="30m">30 minutes</option>
              </select>
            </div>
          </div>
        </section>

        {/* Auto Features */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <Clock className="w-4 h-4" />
            Auto Features
          </h3>
          <div className="space-y-3">
            <ToggleField
              label="Auto-add qualifying stocks"
              checked={localSettings.autoAdd}
              onChange={(v) => handleChange('autoAdd', v)}
            />
            <ToggleField
              label="Real-time updates"
              checked={localSettings.realTimeUpdates}
              onChange={(v) => handleChange('realTimeUpdates', v)}
            />
            <InputField
              label="Update interval (seconds)"
              type="number"
              min="5"
              max="300"
              value={localSettings.updateInterval}
              onChange={(v) => handleChange('updateInterval', parseInt(v) || 20)}
              helperText={(() => {
                // Calculate recommended based on selected APIs
                const hasYahoo = localSettings.useYahoo ?? true
                const hasSerpAPI = localSettings.useSerpAPI ?? false
                const hasAlphaVantage = localSettings.useAlphaVantage ?? false
                const hasMassive = localSettings.useMassive ?? false
                
                if ((hasMassive || hasAlphaVantage) && !hasYahoo && !hasSerpAPI) {
                  return "60s recommended (5 calls/min limit)"
                } else if (hasYahoo || hasSerpAPI) {
                  return "20s recommended (high quota APIs)"
                } else {
                  return "Check API selection for recommended interval"
                }
              })()}
              disabled={!localSettings.realTimeUpdates}
            />
          </div>
        </section>

        {/* Notifications */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <Bell className="w-4 h-4" />
            Notifications
          </h3>
          <div className="space-y-3">
            <ToggleField
              label="Enable notifications"
              checked={localSettings.notificationsEnabled}
              onChange={(v) => handleChange('notificationsEnabled', v)}
            />
            <ToggleField
              label="New stock alerts"
              checked={localSettings.notifyOnNewStocks}
              onChange={(v) => handleChange('notifyOnNewStocks', v)}
              disabled={!localSettings.notificationsEnabled}
            />
          </div>
        </section>

        {/* API Selection - HIDDEN: IBKR-only mode, no API selection needed */}
        {false && (
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <Globe className="w-4 h-4" />
            API Selection
          </h3>
          <div className="space-y-3">
            {/* Market Status */}
            {!marketStatus.isOpen && (
              <div className="px-3 py-2 rounded-lg bg-orange-500/10 border border-orange-500/20 mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-orange-400">⚠️ {marketStatus.message}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  APIs may return delayed/closed data. Real-time data available 9:30 AM - 4:00 PM ET (Mon-Fri)
                </p>
              </div>
            )}
            {marketStatus.isOpen && (
              <div className="px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/20 mb-2">
                <span className="text-xs font-semibold text-green-400">✅ {marketStatus.message}</span>
              </div>
            )}
            
            <p className="text-xs text-muted-foreground mb-2">
              Choose which APIs to use for stock scanning. At least one must be enabled.
            </p>
            
            {/* Calculate recommended wait time and stock count based on selected APIs */}
            {(() => {
              const selectedApis = []
              let minWaitTime = Infinity
              let recommendedInterval = 20 // Default
              let maxStocks = 10 // Default
              
              if (localSettings.useYahoo ?? true) {
                selectedApis.push('Yahoo')
                minWaitTime = Math.min(minWaitTime, 20) // 20 seconds minimum
                recommendedInterval = 20 // Yahoo allows 20s scans
                maxStocks = 10 // Yahoo allows 10 stocks per scan
              }
              if (localSettings.useSerpAPI ?? false) {
                selectedApis.push('SerpAPI')
                minWaitTime = Math.min(minWaitTime, 120) // ~2 minutes per call (250/month)
                if (recommendedInterval < 120) recommendedInterval = 120
                maxStocks = Math.min(maxStocks, 10) // SerpAPI: 5-10 stocks recommended
              }
              if (localSettings.useAlphaVantage ?? false) {
                selectedApis.push('AlphaVantage')
                minWaitTime = Math.min(minWaitTime, 60) // 60 seconds (5 calls/min = 12s per call, but need 60s for safe scanning)
                if (recommendedInterval < 60) recommendedInterval = 60
                maxStocks = Math.min(maxStocks, 5) // AlphaVantage: 5 stocks max (5 calls/min)
              }
              if (localSettings.useMassive ?? false) {
                selectedApis.push('Massive.com')
                minWaitTime = Math.min(minWaitTime, 60) // 60 seconds (5 calls/min = 12s per call, but need 60s for safe scanning)
                if (recommendedInterval < 60) recommendedInterval = 60
                maxStocks = Math.min(maxStocks, 5) // Massive.com: 5 stocks max (5 calls/min)
              }
              
              // If only Massive or AlphaVantage, need 60s for 5 stocks
              if ((localSettings.useMassive || localSettings.useAlphaVantage) && 
                  !(localSettings.useYahoo ?? true) && !(localSettings.useSerpAPI ?? false)) {
                recommendedInterval = 60 // 60 seconds for 5 stocks at 5/min
                maxStocks = 5
              }
              
              return (
                <div className="mb-3 px-3 py-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-blue-400">Recommended Settings:</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Max Stocks:</span>
                    <span className="text-xs font-bold text-blue-300">📊 {maxStocks} stocks</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Scan Interval:</span>
                    <span className="text-xs font-bold text-blue-300">⏱️ {recommendedInterval}s</span>
                  </div>
                  {selectedApis.length > 0 && (
                    <p className="text-xs text-muted-foreground mt-1 pt-1 border-t border-blue-500/20">
                      Based on: {selectedApis.join(', ')} • Min wait: {minWaitTime}s
                    </p>
                  )}
                </div>
              )
            })()}
            
            <div className="space-y-2">
              <div className={`flex items-center justify-between p-2 rounded-lg ${apiLockouts.yahoo.locked ? 'bg-red-500/5 border border-red-500/20 opacity-60' : ''}`}>
                <div className="flex items-center gap-2 flex-1">
                  <ToggleField
                    label="Yahoo Finance (Recommended)"
                    checked={localSettings.useYahoo ?? true}
                    onChange={(v) => handleChange('useYahoo', v)}
                    disabled={apiLockouts.yahoo.locked}
                  />
                  {apiLockouts.yahoo.locked && (
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-bold text-red-400">🔒</span>
                      <span className="text-xs font-mono font-semibold text-red-400">
                        {getTimeUntilUnlock(apiLockouts.yahoo.unlockAt)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center justify-between ml-0">
                <p className={`text-xs ${apiLockouts.yahoo.locked ? 'text-muted-foreground/50' : 'text-muted-foreground'}`}>
                  {apiLockouts.yahoo.locked ? 'Rate limited - Locked for 24 hours' : 'Fast, reliable, high quota'}
                </p>
                {!apiLockouts.yahoo.locked && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-blue-400">📊 10 stocks</span>
                    <span className="text-xs font-semibold text-green-400">⏱️ 20s</span>
                  </div>
                )}
              </div>
            </div>
            <div className="space-y-2">
              <div className={`flex items-center justify-between p-2 rounded-lg ${apiLockouts.serpapi.locked ? 'bg-red-500/5 border border-red-500/20 opacity-60' : ''}`}>
                <div className="flex items-center gap-2 flex-1">
                  <ToggleField
                    label="SerpAPI"
                    checked={localSettings.useSerpAPI ?? false}
                    onChange={(v) => handleChange('useSerpAPI', v)}
                    disabled={apiLockouts.serpapi.locked}
                  />
                  {apiLockouts.serpapi.locked && (
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-bold text-red-400">🔒</span>
                      <span className="text-xs font-mono font-semibold text-red-400">
                        {getTimeUntilUnlock(apiLockouts.serpapi.unlockAt)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center justify-between ml-0">
                <p className={`text-xs ${apiLockouts.serpapi.locked ? 'text-muted-foreground/50' : 'text-muted-foreground'}`}>
                  {apiLockouts.serpapi.locked ? 'Rate limited - Locked for 24 hours' : '250 calls/month free tier'}
                </p>
                {!apiLockouts.serpapi.locked && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-blue-400">📊 5-10 stocks</span>
                    <span className="text-xs font-semibold text-yellow-400">⏱️ 120s</span>
                  </div>
                )}
              </div>
            </div>
            <div className="space-y-2">
              <div className={`flex items-center justify-between p-2 rounded-lg ${apiLockouts.alphavantage.locked ? 'bg-red-500/5 border border-red-500/20 opacity-60' : ''}`}>
                <div className="flex items-center gap-2 flex-1">
                  <ToggleField
                    label="AlphaVantage"
                    checked={localSettings.useAlphaVantage ?? false}
                    onChange={(v) => handleChange('useAlphaVantage', v)}
                    disabled={apiLockouts.alphavantage.locked}
                  />
                  {apiLockouts.alphavantage.locked && (
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-bold text-red-400">🔒</span>
                      <span className="text-xs font-mono font-semibold text-red-400">
                        {getTimeUntilUnlock(apiLockouts.alphavantage.unlockAt)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center justify-between ml-0">
                <p className={`text-xs ${apiLockouts.alphavantage.locked ? 'text-muted-foreground/50' : 'text-muted-foreground'}`}>
                  {apiLockouts.alphavantage.locked ? 'Rate limited - Locked for 24 hours' : '5 calls/minute, 500/day free'}
                </p>
                {!apiLockouts.alphavantage.locked && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-blue-400">📊 5 stocks max</span>
                    <span className="text-xs font-semibold text-orange-400">⏱️ 60s</span>
                  </div>
                )}
              </div>
            </div>
            <div className="space-y-2">
              <div className={`flex items-center justify-between p-2 rounded-lg ${apiLockouts.massive.locked ? 'bg-red-500/5 border border-red-500/20 opacity-60' : ''}`}>
                <div className="flex items-center gap-2 flex-1">
                  <ToggleField
                    label="Massive.com (Polygon.io)"
                    checked={localSettings.useMassive ?? false}
                    onChange={(v) => handleChange('useMassive', v)}
                    disabled={apiLockouts.massive.locked}
                  />
                  {apiLockouts.massive.locked && (
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-bold text-red-400">🔒</span>
                      <span className="text-xs font-mono font-semibold text-red-400">
                        {getTimeUntilUnlock(apiLockouts.massive.unlockAt)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center justify-between ml-0">
                <p className={`text-xs ${apiLockouts.massive.locked ? 'text-muted-foreground/50' : 'text-muted-foreground'}`}>
                  {apiLockouts.massive.locked ? 'Rate limited - Locked for 24 hours' : '5 calls/minute rate limit'}
                </p>
                {!apiLockouts.massive.locked && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-blue-400">📊 5 stocks max</span>
                    <span className="text-xs font-semibold text-orange-400">⏱️ 60s</span>
                  </div>
                )}
              </div>
            </div>
            {(!localSettings.useYahoo && !localSettings.useSerpAPI && !localSettings.useAlphaVantage && !localSettings.useMassive) && (
              <div className="px-3 py-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-xs text-yellow-600 dark:text-yellow-400">
                ⚠️ At least one API must be enabled
              </div>
            )}
          </div>
        </section>
        )}

        {/* Presets */}
        <section>
          <h3 className="text-sm font-semibold mb-3">Quick Presets</h3>
          {isRateLimited && (
            <div className="mb-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-600 dark:text-red-400">
              🔒 Locked - Wait {Math.floor(readyCountdown / 60)}:{(readyCountdown % 60).toString().padStart(2, '0')}
            </div>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              onClick={handlePennyStockPreset}
              disabled={isRateLimited}
              className="px-4 py-3 rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 transition-all font-medium text-sm shadow-md hover:shadow-lg disabled:opacity-30 disabled:cursor-not-allowed"
              title={isRateLimited ? `Locked until rate limit clears (${Math.floor(readyCountdown / 60)}:${(readyCountdown % 60).toString().padStart(2, '0')})` : 'Apply penny stock settings'}
            >
              💰 Penny Stocks ($0.05-$1)
            </button>
            <button
              onClick={handleReset}
              disabled={isRateLimited}
              className="px-4 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700 transition-all font-medium text-sm shadow-md hover:shadow-lg disabled:opacity-30 disabled:cursor-not-allowed"
              title={isRateLimited ? `Locked until rate limit clears (${Math.floor(readyCountdown / 60)}:${(readyCountdown % 60).toString().padStart(2, '0')})` : 'Apply explosive mode settings'}
            >
              🔥 Explosive Mode ($1-$20)
            </button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Quick presets to switch between scanning modes
          </p>
        </section>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-2 pt-4 border-t border-border">
          <button
            onClick={handleApply}
            disabled={isRateLimited}
            className="flex-1 px-4 py-3 sm:py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium text-base sm:text-sm disabled:opacity-30 disabled:cursor-not-allowed"
            title={isRateLimited ? `🔒 Locked - Wait ${Math.floor(readyCountdown / 60)}:${(readyCountdown % 60).toString().padStart(2, '0')}` : 'Apply custom settings'}
          >
            Apply Settings
          </button>
        </div>
        </div>
      )}

      {/* FAQ Tab Content */}
      {activeTab === 'faq' && (
        <div>
          <FAQSection />
        </div>
      )}
    </div>
  )
}

interface InputFieldProps {
  label: string
  type?: string
  value: string | number
  onChange: (value: string) => void
  prefix?: string
  suffix?: string
  helperText?: string
  placeholder?: string
  min?: string
  max?: string
  step?: string
  disabled?: boolean
}

function InputField({ label, type = 'text', value, onChange, prefix, suffix, helperText, placeholder, min, max, step, disabled }: InputFieldProps) {
  return (
    <div>
      <label className={`block text-sm font-medium mb-2 ${disabled ? 'text-muted-foreground' : ''}`}>{label}</label>
      <div className="flex items-center gap-2">
        {prefix && <span className="text-muted-foreground">{prefix}</span>}
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          min={min}
          max={max}
          step={step}
          disabled={disabled}
          className="flex-1 px-3 py-2 rounded-lg bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
        />
        {suffix && <span className="text-muted-foreground">{suffix}</span>}
      </div>
      {helperText && (
        <p className="text-xs text-muted-foreground mt-1">{helperText}</p>
      )}
    </div>
  )
}

interface ToggleFieldProps {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
}

function ToggleField({ label, checked, onChange, disabled }: ToggleFieldProps) {
  return (
    <label className={`flex items-center justify-between ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}>
      <span className={`text-sm ${disabled ? 'text-muted-foreground/50' : ''}`}>{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
          ${checked ? 'bg-primary' : 'bg-muted'}
          ${disabled ? 'opacity-30 cursor-not-allowed grayscale' : ''}
        `}
      >
        <span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
            ${checked ? 'translate-x-6' : 'translate-x-1'}
            ${disabled ? 'opacity-50' : ''}
          `}
        />
      </button>
    </label>
  )
}

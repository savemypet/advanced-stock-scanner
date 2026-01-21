import { useState } from 'react'
import { ScannerSettings, ChartTimeframe } from '../types'
import { X, DollarSign, TrendingUp, BarChart3, Bell, Clock, Hash, HelpCircle } from 'lucide-react'
import FAQSection from './FAQSection'

interface SettingsPanelProps {
  settings: ScannerSettings
  onSettingsChange: (settings: ScannerSettings) => void
  onClose: () => void
  isRateLimited?: boolean
  readyCountdown?: number
}

export default function SettingsPanel({ settings, onSettingsChange, onClose, isRateLimited = false, readyCountdown = 0 }: SettingsPanelProps) {
  const [localSettings, setLocalSettings] = useState(settings)
  const [floatDisplayValue, setFloatDisplayValue] = useState(formatFloatHelper(settings.maxFloat))
  const [activeTab, setActiveTab] = useState<'settings' | 'faq'>('settings')

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
    }
    setLocalSettings(pennySettings)
    setFloatDisplayValue(formatFloatHelper(pennySettings.maxFloat))
    onSettingsChange(pennySettings)
  }

  const handleReset = () => {
    const defaultSettings: ScannerSettings = {
      minPrice: 1,
      maxPrice: 20,
      maxFloat: 10_000_000, // 10M shares - LOW-FLOAT for volatile stocks
      minGainPercent: 10, // 10% - only explosive movers
      volumeMultiplier: 5, // 5x - EXPLOSIVE volume only
      displayCount: 10, // Show all 10 tracked symbols
      chartTimeframe: '5m',
      autoAdd: true,
      realTimeUpdates: true,
      updateInterval: 20, // 20 seconds - fastest safe with 10 symbols
      notificationsEnabled: true,
      notifyOnNewStocks: true,
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
            <InputField
              label="Minimum Price"
              type="number"
              value={localSettings.minPrice}
              onChange={(v) => handleChange('minPrice', parseFloat(v) || 0)}
              prefix="$"
            />
            <InputField
              label="Maximum Price"
              type="number"
              value={localSettings.maxPrice}
              onChange={(v) => handleChange('maxPrice', parseFloat(v) || 0)}
              prefix="$"
            />
          </div>
        </section>

        {/* Stock Criteria */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <TrendingUp className="w-4 h-4" />
            Stock Criteria
          </h3>
          <div className="space-y-3">
            <InputField
              label="Max Float (shares)"
              type="text"
              value={floatDisplayValue}
              onChange={handleFloatChange}
              helperText="Use M for millions, K for thousands (e.g., 10M, 500K)"
              placeholder="e.g., 10M or 10000000"
            />
            <InputField
              label="Minimum Gain %"
              type="number"
              value={localSettings.minGainPercent}
              onChange={(v) => handleChange('minGainPercent', parseFloat(v) || 0)}
              suffix="%"
            />
            <InputField
              label="Volume Multiplier"
              type="number"
              step="0.1"
              value={localSettings.volumeMultiplier}
              onChange={(v) => handleChange('volumeMultiplier', parseFloat(v) || 0)}
              suffix="x"
              helperText="Current vs average volume"
            />
          </div>
        </section>

        {/* Display Settings */}
        <section>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <BarChart3 className="w-4 h-4" />
            Display Settings
          </h3>
          <div className="space-y-3">
            <InputField
              label="Number of Stocks"
              type="number"
              min="1"
              max="10"
              value={localSettings.displayCount}
              onChange={(v) => handleChange('displayCount', parseInt(v) || 1)}
            />
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
              helperText="20s = fastest safe with 10 symbols"
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
    <label className="flex items-center justify-between cursor-pointer">
      <span className={`text-sm ${disabled ? 'text-muted-foreground' : ''}`}>{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
          ${checked ? 'bg-primary' : 'bg-muted'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
            ${checked ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </button>
    </label>
  )
}

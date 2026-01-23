import { useState, useEffect } from 'react'
import { Calendar, DollarSign, CheckCircle2, XCircle } from 'lucide-react'

interface DayConfig {
  date: string
  dayName: string
  enabled: boolean
  buyUsed: boolean
  sellUsed: boolean
}

interface TradingCalendarProps {
  dailyTradeBudget: number
  onBudgetChange: (budget: number) => void
  enabledDays: { [date: string]: boolean }
  onDayToggle: (date: string, enabled: boolean) => void
  dailyTrades: { [date: string]: { buyUsed: boolean; sellUsed: boolean } }
  accountBalance: number
}

export default function TradingCalendar({
  dailyTradeBudget,
  onBudgetChange,
  enabledDays,
  onDayToggle,
  dailyTrades,
  accountBalance
}: TradingCalendarProps) {
  const [days, setDays] = useState<DayConfig[]>([])

  useEffect(() => {
    // Generate 5 days starting from today
    const today = new Date()
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    const next5Days: DayConfig[] = []
    for (let i = 0; i < 5; i++) {
      const date = new Date(today)
      date.setDate(today.getDate() + i)
      const dateStr = date.toISOString().split('T')[0] // YYYY-MM-DD
      
      next5Days.push({
        date: dateStr,
        dayName: dayNames[date.getDay()],
        enabled: enabledDays[dateStr] || false,
        buyUsed: dailyTrades[dateStr]?.buyUsed || false,
        sellUsed: dailyTrades[dateStr]?.sellUsed || false
      })
    }
    
    setDays(next5Days)
  }, [enabledDays, dailyTrades])

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}/${day}`
  }

  const isToday = (dateStr: string) => {
    const today = new Date().toISOString().split('T')[0]
    return dateStr === today
  }

  return (
    <div className="bg-card border border-border rounded-lg p-4 space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold">Ollama Trading Calendar</h3>
      </div>

      {/* Account Balance */}
      <div className="bg-muted/50 rounded-lg p-3 border border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">IBKR Balance:</span>
          </div>
          <span className="text-lg font-bold text-green-500">
            ${accountBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
      </div>

      {/* Daily Trade Budget */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <DollarSign className="w-4 h-4" />
          Daily Trade Budget (per day)
        </label>
        <input
          type="number"
          min="0"
          max={accountBalance}
          step="0.01"
          value={dailyTradeBudget}
          onChange={(e) => onBudgetChange(parseFloat(e.target.value) || 0)}
          className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Enter daily budget"
        />
        <p className="text-xs text-muted-foreground">
          Maximum amount Ollama can use for one full trade (1 buy + 1 sell) per enabled day
        </p>
      </div>

      {/* 5-Day Calendar */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Select Trading Days</label>
        <div className="grid grid-cols-5 gap-2">
          {days.map((day) => (
            <div
              key={day.date}
              className={`relative p-3 rounded-lg border-2 transition-all cursor-pointer ${
                day.enabled
                  ? 'border-primary bg-primary/10'
                  : 'border-border bg-card hover:border-muted-foreground/50'
              } ${isToday(day.date) ? 'ring-2 ring-primary/50' : ''}`}
              onClick={() => onDayToggle(day.date, !day.enabled)}
            >
              {/* Day Header */}
              <div className="text-center mb-2">
                <div className="text-xs text-muted-foreground mb-1">{day.dayName}</div>
                <div className={`text-sm font-semibold ${isToday(day.date) ? 'text-primary' : ''}`}>
                  {formatDate(day.date)}
                </div>
                {isToday(day.date) && (
                  <div className="text-xs text-primary font-medium mt-1">Today</div>
                )}
              </div>

              {/* Checkbox */}
              <div className="flex items-center justify-center mb-2">
                <div
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                    day.enabled
                      ? 'bg-primary border-primary'
                      : 'bg-background border-border'
                  }`}
                >
                  {day.enabled && (
                    <CheckCircle2 className="w-4 h-4 text-primary-foreground" />
                  )}
                </div>
              </div>

              {/* Trade Status */}
              {day.enabled && (
                <div className="space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Buy:</span>
                    {day.buyUsed ? (
                      <XCircle className="w-3 h-3 text-red-500" />
                    ) : (
                      <CheckCircle2 className="w-3 h-3 text-green-500" />
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Sell:</span>
                    {day.sellUsed ? (
                      <XCircle className="w-3 h-3 text-red-500" />
                    ) : (
                      <CheckCircle2 className="w-3 h-3 text-green-500" />
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-xs text-muted-foreground">
        <p className="font-medium mb-1">📋 Trading Rules:</p>
        <ul className="space-y-1 list-disc list-inside">
          <li>1 buy and 1 sell maximum per enabled day</li>
          <li>Daily budget applies to each enabled day</li>
          <li>Trades reset at midnight</li>
        </ul>
      </div>
    </div>
  )
}

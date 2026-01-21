import { useState } from 'react'
import { ChevronDown, ChevronUp, HelpCircle, BarChart3, TrendingUp, Settings as SettingsIcon, Zap, Shield } from 'lucide-react'

interface FAQItem {
  question: string
  answer: string
  category: string
  icon?: React.ReactNode
}

const faqData: FAQItem[] = [
  // Getting Started
  {
    category: "Getting Started",
    question: "How do I start scanning for stocks?",
    answer: "Click the green 'Start' button at the top of the page. The scanner will search for stocks matching your filter criteria. You can also choose a Quick Preset (Penny Stocks or Explosive Mode) from the Settings panel.",
    icon: <Zap className="w-4 h-4" />
  },
  {
    category: "Getting Started",
    question: "What happens when I click Start?",
    answer: "The scanner fetches real-time data from Yahoo Finance for 10 volatile stocks (GME, AMC, TSLA, etc.) and filters them based on your settings. Only stocks meeting ALL criteria will appear in the list.",
    icon: <TrendingUp className="w-4 h-4" />
  },
  {
    category: "Getting Started",
    question: "Why don't I see any stocks?",
    answer: "Your filters might be too strict! Try: 1) Lower Min Gain % (try 5% instead of 10%), 2) Increase Max Float (try 50M or 100M), 3) Lower Volume Multiplier (try 2x or 3x), or 4) Use the 'Penny Stocks' preset which has looser filters.",
    icon: <HelpCircle className="w-4 h-4" />
  },

  // Charts
  {
    category: "Charts & Analysis",
    question: "What are the green and red candlesticks?",
    answer: "Green candles = Price went UP (closed higher than it opened). Red candles = Price went DOWN (closed lower than it opened). The body shows open-to-close range, and the wicks show the high-low range for that period.",
    icon: <BarChart3 className="w-4 h-4" />
  },
  {
    category: "Charts & Analysis",
    question: "What do the colored lines mean?",
    answer: "Blue Line (MA20) = 20-period average (short-term trend). Purple Line (MA50) = 50-period average (medium-term trend). Orange Line (MA200) = 200-period average (long-term trend). These help identify trend direction and support/resistance levels.",
    icon: <BarChart3 className="w-4 h-4" />
  },
  {
    category: "Charts & Analysis",
    question: "What are the volume bars at the bottom?",
    answer: "Green bars = Buying volume (volume on up candles). Red bars = Selling volume (volume on down candles). Higher bars mean more trading activity. Use this to confirm price moves - breakouts should have high volume!",
    icon: <BarChart3 className="w-4 h-4" />
  },
  {
    category: "Charts & Analysis",
    question: "How do I switch timeframes?",
    answer: "Click any stock card to open the detail modal, then click the timeframe buttons (1m, 5m, 1h, 24h) at the top of the chart. Switching is INSTANT with no loading - all data is pre-loaded!",
    icon: <BarChart3 className="w-4 h-4" />
  },
  {
    category: "Charts & Analysis",
    question: "What timeframe should I use?",
    answer: "1m = Scalping/quick trades (last 24 hours). 5m = Day trading (last 5 days). 1h = Swing trading (last month). 24h = Position trading/trends (last 3 months). Start with 24h to see the big picture, then zoom to shorter timeframes for entry timing.",
    icon: <BarChart3 className="w-4 h-4" />
  },

  // Filters
  {
    category: "Filters & Settings",
    question: "What is 'Max Float' and why does it matter?",
    answer: "Float = Number of shares available for trading. Lower float = Higher volatility (price moves faster). Set to 10M for explosive moves, or 100M for penny stocks. Lower float stocks can have bigger percentage gains!",
    icon: <SettingsIcon className="w-4 h-4" />
  },
  {
    category: "Filters & Settings",
    question: "What is 'Min Gain %'?",
    answer: "The minimum percentage gain required for a stock to appear. 10% = Only shows stocks up 10% or more. Lower it to 2-5% to see more stocks. Higher values (15-20%) = Only the most explosive movers.",
    icon: <SettingsIcon className="w-4 h-4" />
  },
  {
    category: "Filters & Settings",
    question: "What is 'Volume Multiplier'?",
    answer: "How many times above average volume is required. 5x = Volume must be 5 times the average. Lower to 2-3x to see more stocks. High volume confirms strong interest and validates price moves!",
    icon: <SettingsIcon className="w-4 h-4" />
  },
  {
    category: "Filters & Settings",
    question: "What's the difference between Penny Stocks and Explosive Mode?",
    answer: "Penny Stocks ($0.05-$1): Higher float (100M), cheaper stocks, more options. Explosive Mode ($1-$20): Strict float (10M), higher quality, bigger gains potential. Both require 10% gain and 5x volume.",
    icon: <SettingsIcon className="w-4 h-4" />
  },

  // Features
  {
    category: "Features",
    question: "What does the Play/Pause button do?",
    answer: "Green (Playing) = Auto-refresh ON, scans every 20 seconds automatically. Gray (Paused) = Auto-refresh OFF, only scans when you click Refresh. Start in paused mode to avoid API calls.",
    icon: <Zap className="w-4 h-4" />
  },
  {
    category: "Features",
    question: "What are the 'HOT' and 'BUY' badges?",
    answer: "🔥 HOT = Volume is 5x+ average (extreme interest). BUY = Stock is up 15%+ with 3x+ volume (strong buy signal). These are automatic signals based on price action and volume.",
    icon: <TrendingUp className="w-4 h-4" />
  },
  {
    category: "Features",
    question: "Why does the scanner lock with a red banner?",
    answer: "Yahoo Finance rate limits requests (too many API calls). The red banner means you hit the limit. Wait 45 minutes for the countdown to hit 0:00, then you'll see a green 'Ready!' banner. This protects your access!",
    icon: <Shield className="w-4 h-4" />
  },
  {
    category: "Features",
    question: "Does refreshing the page reset the rate limit?",
    answer: "No! The rate limit is saved in your browser. Even if you close and reopen the app, the lock persists until the countdown completes. This prevents accidental API abuse.",
    icon: <Shield className="w-4 h-4" />
  },

  // Trading
  {
    category: "Trading Tips",
    question: "How do I know if a breakout is real?",
    answer: "Check 3 things: 1) Price breaks above resistance (previous high). 2) Volume spikes (green bars 2x+ average). 3) Green candle closes above the breakout level. All 3 = Strong breakout! Missing volume = Likely false breakout.",
    icon: <TrendingUp className="w-4 h-4" />
  },
  {
    category: "Trading Tips",
    question: "What's a Golden Cross?",
    answer: "When the MA20 (blue line) crosses ABOVE the MA50 (purple line), especially when both are above MA200 (orange). This is a strong bullish signal indicating upward momentum. Look for this on the 24h chart!",
    icon: <TrendingUp className="w-4 h-4" />
  },
  {
    category: "Trading Tips",
    question: "How do I use moving averages for entries?",
    answer: "Buy when price pulls back TO a rising MA (support), then bounces with a green candle + green volume. MA20 = aggressive entries. MA50 = safer entries. MA200 = major support. Price below all MAs = Stay out!",
    icon: <TrendingUp className="w-4 h-4" />
  },
  {
    category: "Trading Tips",
    question: "What's the best way to analyze a stock?",
    answer: "1) Start with 24h chart - Is there a long-term trend? Price above MA200? 2) Check 1h - Is today confirming? 3) Check 5m - What's the current move? 4) Check 1m - Find precise entry point. Always check multiple timeframes!",
    icon: <TrendingUp className="w-4 h-4" />
  },

  // Technical
  {
    category: "Technical",
    question: "How often does the scanner update?",
    answer: "Every 20 seconds when auto-refresh is ON (green Play button). This is the fastest safe interval with 10 stocks. You can also manually refresh anytime with the 🔄 button.",
    icon: <Zap className="w-4 h-4" />
  },
  {
    category: "Technical",
    question: "Do I need an API key?",
    answer: "No! The scanner uses Yahoo Finance's free public data. No signup, no API key, no cost. However, Yahoo limits requests (rate limiting), so use the 20-second interval to stay safe.",
    icon: <Shield className="w-4 h-4" />
  },
  {
    category: "Technical",
    question: "Why do timeframe switches happen instantly?",
    answer: "When the scanner runs, it fetches ALL timeframes (1m, 5m, 1h, 24h) at once and stores them in memory. Switching between them just swaps the data - no new API calls needed! This is why it's instant.",
    icon: <Zap className="w-4 h-4" />
  },
  {
    category: "Technical",
    question: "Can I add my own stocks to scan?",
    answer: "Currently, the scanner monitors 10 pre-selected volatile stocks (GME, AMC, TSLA, AMD, PLTR, SOFI, NIO, LCID, ATER, BBIG). This keeps API usage low and focuses on the most active stocks.",
    icon: <SettingsIcon className="w-4 h-4" />
  },
]

export default function FAQSection() {
  const [openItems, setOpenItems] = useState<Set<number>>(new Set())
  const [selectedCategory, setSelectedCategory] = useState<string>("All")

  const categories = ["All", ...Array.from(new Set(faqData.map(item => item.category)))]

  const filteredFAQs = selectedCategory === "All" 
    ? faqData 
    : faqData.filter(item => item.category === selectedCategory)

  const toggleItem = (index: number) => {
    const newOpenItems = new Set(openItems)
    if (newOpenItems.has(index)) {
      newOpenItems.delete(index)
    } else {
      newOpenItems.add(index)
    }
    setOpenItems(newOpenItems)
  }

  const expandAll = () => {
    setOpenItems(new Set(filteredFAQs.map((_, index) => index)))
  }

  const collapseAll = () => {
    setOpenItems(new Set())
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold">Frequently Asked Questions</h3>
        </div>
        <div className="flex gap-2">
          <button
            onClick={expandAll}
            className="text-xs px-2 py-1 rounded bg-primary/20 text-primary hover:bg-primary/30 transition-colors"
          >
            Expand All
          </button>
          <button
            onClick={collapseAll}
            className="text-xs px-2 py-1 rounded bg-muted text-muted-foreground hover:bg-muted/80 transition-colors"
          >
            Collapse All
          </button>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              selectedCategory === category
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      {/* FAQ Items */}
      <div className="space-y-2">
        {filteredFAQs.map((item, index) => (
          <div
            key={index}
            className="border border-border rounded-lg overflow-hidden bg-card hover:border-primary/50 transition-colors"
          >
            <button
              onClick={() => toggleItem(index)}
              className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-muted/30 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1">
                {item.icon && (
                  <div className="text-primary flex-shrink-0">
                    {item.icon}
                  </div>
                )}
                <span className="font-medium text-sm">{item.question}</span>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className="text-xs text-muted-foreground hidden sm:inline">
                  {item.category}
                </span>
                {openItems.has(index) ? (
                  <ChevronUp className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                )}
              </div>
            </button>
            
            {openItems.has(index) && (
              <div className="px-4 py-3 bg-muted/20 border-t border-border">
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {item.answer}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Quick Tips */}
      <div className="mt-6 p-4 rounded-lg bg-primary/10 border border-primary/20">
        <h4 className="font-semibold text-sm mb-2 flex items-center gap-2">
          <Zap className="w-4 h-4 text-primary" />
          Quick Tips
        </h4>
        <ul className="text-sm text-muted-foreground space-y-1.5">
          <li>• Start with the <strong>24h chart</strong> to see the big picture trend</li>
          <li>• Use <strong>volume bars</strong> to confirm breakouts (need 2x+ volume)</li>
          <li>• Watch for <strong>MA20 crossing above MA50</strong> (Golden Cross = bullish)</li>
          <li>• <strong>Green volume + green candles</strong> = strong buying pressure</li>
          <li>• If rate limited, wait for the <strong>green "Ready!"</strong> banner</li>
          <li>• Click <strong>any stock card</strong> to see detailed charts and switch timeframes</li>
        </ul>
      </div>

      {/* Legend */}
      <div className="mt-6 p-4 rounded-lg bg-muted/30 border border-border">
        <h4 className="font-semibold text-sm mb-3">Chart Legend</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gradient-to-b from-green-500/80 to-green-500/30 rounded"></div>
              <span>Green Candle = Price Up (Bullish)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gradient-to-b from-red-500/80 to-red-500/30 rounded"></div>
              <span>Red Candle = Price Down (Bearish)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-blue-500"></div>
              <span>MA20 = 20-Period Average (Short-term)</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-purple-500"></div>
              <span>MA50 = 50-Period Average (Medium-term)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-orange-500"></div>
              <span>MA200 = 200-Period Average (Long-term)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-3 bg-green-500/70"></div>
              <span>Green Volume = Buying Pressure</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

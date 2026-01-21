import { useState, useEffect } from 'react'
import { Stock, ChartTimeframe, NewsItem } from '../types'
import { X, TrendingUp, TrendingDown, Activity, BarChart3, Newspaper, ExternalLink } from 'lucide-react'
import BookmapChart from './BookmapChart'
import CandlestickOnlyChart from './CandlestickOnlyChart'
import TradingViewChart from './TradingViewChart'
import { formatNumber, formatCurrency } from '../utils/formatters'
import { PatternSignal } from '../utils/candlestickPatterns'
import axios from 'axios'

interface StockDetailModalProps {
  stock: Stock
  onClose: () => void
}

export default function StockDetailModal({ stock, onClose }: StockDetailModalProps) {
  const [bookmapTimeframe, setBookmapTimeframe] = useState<ChartTimeframe>('5m')
  const [candlestickTimeframe, setCandlestickTimeframe] = useState<ChartTimeframe>('5m')
  const [tradingviewTimeframe, setTradingviewTimeframe] = useState<ChartTimeframe>('5m')
  const [fullscreenChart, setFullscreenChart] = useState<'none' | 'bookmap' | 'candlestick' | 'tradingview'>('none')
  const [news, setNews] = useState<NewsItem[]>([])
  const [newsLoading, setNewsLoading] = useState(false)
  const [candlestickPattern, setCandlestickPattern] = useState<PatternSignal | null>(null)
  const isPositive = stock.changePercent >= 0
  const volumeRatio = (stock.volume / stock.avgVolume).toFixed(2)
  
  // Available timeframes from chartData in chronological order
  const timeframeOrder: ChartTimeframe[] = ['1m', '5m', '15m', '30m', '1h', '4h', '24h', '1week', '1month']
  const availableTimeframes: ChartTimeframe[] = stock.chartData 
    ? timeframeOrder.filter(tf => stock.chartData![tf])
    : ['5m']
  
  // Get candles for each chart's selected timeframe
  const bookmapCandles = stock.chartData?.[bookmapTimeframe] || stock.candles
  const candlestickCandles = stock.chartData?.[candlestickTimeframe] || stock.candles
  const tradingviewCandles = stock.chartData?.[tradingviewTimeframe] || stock.candles

  // Fetch news when modal opens (if stock has news)
  useEffect(() => {
    if (stock.hasNews) {
      setNewsLoading(true)
      axios.get(`http://127.0.0.1:5000/api/news/${stock.symbol}`)
        .then(response => {
          if (response.data.success) {
            setNews(response.data.news || [])
          }
        })
        .catch(error => {
          console.error('Error fetching news:', error)
        })
        .finally(() => {
          setNewsLoading(false)
        })
    }
  }, [stock.symbol, stock.hasNews])

  useEffect(() => {
    // ESC key to close
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onClose])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-card border border-border rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-card border-b border-border px-6 py-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h2 className="text-3xl font-bold text-primary">{stock.symbol}</h2>
                {stock.isHot && (
                  <span className="px-3 py-1 text-sm font-semibold rounded-full bg-orange-500/20 text-orange-400">
                    🔥 HOT
                  </span>
                )}
                {stock.signal === 'BUY' && (
                  <span className="px-3 py-1 text-sm font-semibold rounded-full bg-green-500/20 text-green-400">
                    BUY
                  </span>
                )}
              </div>
              <p className="text-lg font-medium text-foreground">{stock.name}</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
            aria-label="Close"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Price Info */}
        <div className="px-6 py-4 bg-muted/30">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-5xl font-bold mb-2">
                {formatCurrency(stock.currentPrice)}
              </div>
              <div className={`flex items-center gap-2 text-2xl font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                {isPositive ? <TrendingUp className="w-6 h-6" /> : <TrendingDown className="w-6 h-6" />}
                <span>
                  {isPositive ? '+' : ''}{stock.changePercent.toFixed(2)}%
                </span>
                <span className="text-lg">
                  ({isPositive ? '+' : ''}{formatCurrency(stock.changeAmount)})
                </span>
              </div>
            </div>
            
            <div className="text-right text-sm text-muted-foreground">
              <p>Last Updated</p>
              <p className="text-lg font-medium text-foreground">
                {new Date(stock.lastUpdated).toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="px-6 py-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard 
            label="Volume" 
            value={formatNumber(stock.volume)}
            subValue={`${volumeRatio}x average`}
            icon={<Activity className="w-5 h-5" />}
          />
          <StatCard 
            label="Float" 
            value={formatNumber(stock.float)}
            subValue="shares outstanding"
            icon={<BarChart3 className="w-5 h-5" />}
          />
          <StatCard 
            label="Day High / Low" 
            value={formatCurrency(stock.dayHigh)}
            subValue={`Low: ${formatCurrency(stock.dayLow)}`}
          />
          <StatCard 
            label="Open / Previous" 
            value={formatCurrency(stock.openPrice)}
            subValue={`Prev: ${formatCurrency(stock.previousClose)}`}
          />
        </div>

        {/* Breaking News Section */}
        {stock.hasNews && news.length > 0 && (
          <div className="px-6 py-4 border-t border-border">
            <div className="mb-3 flex items-center gap-2">
              <Newspaper className="w-5 h-5 text-blue-400" />
              <h3 className="text-lg font-semibold text-foreground">Breaking News Today ({news.length})</h3>
              <span className="ml-auto text-xs text-muted-foreground bg-blue-500/10 px-2 py-1 rounded">
                Fetched at 4 AM
              </span>
            </div>
            
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {news.map((item, index) => (
                <div 
                  key={index}
                  className="bg-gradient-to-br from-blue-500/5 to-blue-500/10 border border-blue-500/20 rounded-lg p-4 hover:border-blue-500/40 transition-all"
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold text-blue-400 bg-blue-500/20 px-2 py-0.5 rounded">
                          {new Date(item.timestamp * 1000).toLocaleTimeString('en-US', { 
                            hour: 'numeric', 
                            minute: '2-digit',
                            hour12: true 
                          })}
                        </span>
                        <span className="text-xs text-muted-foreground">•</span>
                        <span className="text-xs font-medium text-muted-foreground">{item.source}</span>
                      </div>
                      <h4 className="font-semibold text-foreground mb-1 leading-tight">{item.headline}</h4>
                      {item.summary && (
                        <p className="text-sm text-muted-foreground line-clamp-2">{item.summary}</p>
                      )}
                    </div>
                  </div>
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      Read Full Article
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Dual Chart Layout */}
        <div className="px-6 py-6">
          {/* Fullscreen Chart View */}
          {fullscreenChart !== 'none' && (
            <div className="fixed inset-0 z-50 bg-black/95 backdrop-blur-sm flex flex-col">
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h3 className="text-lg font-semibold text-foreground">
                  {fullscreenChart === 'bookmap' && '📊 Bookmap - Buy/Sell Pressure'}
                  {fullscreenChart === 'candlestick' && '🕯️ Candlestick Chart'}
                  {fullscreenChart === 'tradingview' && '📈 TradingView Style - Ichimoku Cloud'}
                </h3>
                <button
                  onClick={() => setFullscreenChart('none')}
                  className="p-2 rounded-lg hover:bg-muted transition-colors"
                  aria-label="Exit Fullscreen"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="flex-1 p-6">
                {fullscreenChart === 'bookmap' && (
                  <div className="h-full">
                    {/* Bookmap Timeframe Selector */}
                    {stock.chartData && availableTimeframes.length > 1 && (
                      <div className="flex items-center gap-2 mb-4">
                        <span className="text-sm font-medium text-muted-foreground">Timeframe:</span>
                        <div className="flex gap-2">
                          {availableTimeframes.map((tf) => (
                            <button
                              key={tf}
                              onClick={() => setBookmapTimeframe(tf)}
                              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                                bookmapTimeframe === tf
                                  ? 'bg-primary text-primary-foreground'
                                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
                              }`}
                            >
                              {tf}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="h-[calc(100%-60px)]">
                      <BookmapChart candles={bookmapCandles} height={window.innerHeight - 200} />
                    </div>
                  </div>
                )}
                
                {fullscreenChart === 'candlestick' && (
                  <div className="h-full">
                    {/* Candlestick Timeframe Selector */}
                    {stock.chartData && availableTimeframes.length > 1 && (
                      <div className="flex items-center gap-2 mb-4">
                        <span className="text-sm font-medium text-muted-foreground">Timeframe:</span>
                        <div className="flex gap-2">
                          {availableTimeframes.map((tf) => (
                            <button
                              key={tf}
                              onClick={() => setCandlestickTimeframe(tf)}
                              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                                candlestickTimeframe === tf
                                  ? 'bg-primary text-primary-foreground'
                                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
                              }`}
                            >
                              {tf}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="h-[calc(100%-60px)]">
                      <CandlestickOnlyChart candles={candlestickCandles} height={window.innerHeight - 200} />
                    </div>
                  </div>
                )}
                
                {fullscreenChart === 'tradingview' && (
                  <div className="h-full">
                    {/* TradingView Timeframe Selector */}
                    {stock.chartData && availableTimeframes.length > 1 && (
                      <div className="flex items-center gap-2 mb-4">
                        <span className="text-sm font-medium text-muted-foreground">Timeframe:</span>
                        <div className="flex gap-2">
                          {availableTimeframes.map((tf) => (
                            <button
                              key={tf}
                              onClick={() => setTradingviewTimeframe(tf)}
                              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                                tradingviewTimeframe === tf
                                  ? 'bg-primary text-primary-foreground'
                                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
                              }`}
                            >
                              {tf}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="h-[calc(100%-60px)]">
                      <TradingViewChart candles={tradingviewCandles} height={window.innerHeight - 200} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Grid Chart View - Now with 3 charts */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            
            {/* Bookmap Chart */}
            <div 
              className="bg-gradient-to-br from-green-500/5 to-red-500/5 rounded-lg p-4 border border-border/50 cursor-pointer hover:border-primary/50 transition-all"
              onClick={() => setFullscreenChart('bookmap')}
            >
              <div className="mb-3">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-foreground">📊 Bookmap - Buy/Sell Pressure</h3>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-green-500"></div>
                        <span className="text-muted-foreground">Buy</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-red-500"></div>
                        <span className="text-muted-foreground">Sell</span>
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground px-2 py-1 bg-muted/50 rounded">
                      Click to fullscreen
                    </span>
                  </div>
                </div>
                
                {/* Bookmap Timeframe Selector */}
                {stock.chartData && availableTimeframes.length > 1 && (
                  <div className="flex items-center gap-2 mb-3" onClick={(e) => e.stopPropagation()}>
                    <span className="text-xs font-medium text-muted-foreground">Timeframe:</span>
                    <div className="flex gap-1">
                      {availableTimeframes.map((tf) => (
                        <button
                          key={tf}
                          onClick={(e) => {
                            e.stopPropagation()
                            setBookmapTimeframe(tf)
                          }}
                          className={`px-3 py-1 rounded-lg font-medium text-xs transition-all ${
                            bookmapTimeframe === tf
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted text-muted-foreground hover:bg-muted/80'
                          }`}
                        >
                          {tf}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div onClick={(e) => e.stopPropagation()}>
                <BookmapChart candles={bookmapCandles} height={500} />
              </div>
            </div>

            {/* Candlestick Chart */}
            <div 
              className="bg-gradient-to-br from-muted/20 to-muted/40 rounded-lg p-4 border border-border/50 cursor-pointer hover:border-primary/50 transition-all"
              onClick={() => setFullscreenChart('candlestick')}
            >
              <div className="mb-3">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-foreground">🕯️ Candlestick Chart</h3>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-0.5 bg-blue-500"></div>
                        <span className="text-muted-foreground">MA20</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-0.5 bg-purple-500"></div>
                        <span className="text-muted-foreground">MA50</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-0.5 bg-orange-500"></div>
                        <span className="text-muted-foreground">MA200</span>
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground px-2 py-1 bg-muted/50 rounded">
                      Click to fullscreen
                    </span>
                  </div>
                </div>
                
                {/* Candlestick Timeframe Selector */}
                {stock.chartData && availableTimeframes.length > 1 && (
                  <div className="flex items-center justify-between mb-3" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-muted-foreground">Timeframe:</span>
                      <div className="flex gap-1">
                        {availableTimeframes.map((tf) => (
                          <button
                            key={tf}
                            onClick={(e) => {
                              e.stopPropagation()
                              setCandlestickTimeframe(tf)
                            }}
                            className={`px-3 py-1 rounded-lg font-medium text-xs transition-all ${
                              candlestickTimeframe === tf
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted text-muted-foreground hover:bg-muted/80'
                            }`}
                          >
                            {tf}
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    {/* Pattern Indicator */}
                    {candlestickPattern && (
                      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
                        candlestickPattern.signal === 'BUY' 
                          ? 'bg-green-500/20 border border-green-500/40' 
                          : 'bg-red-500/20 border border-red-500/40'
                      }`}>
                        <div className={`px-2 py-0.5 rounded text-xs font-bold ${
                          candlestickPattern.signal === 'BUY' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                        }`}>
                          {candlestickPattern.signal}
                        </div>
                        <span className="text-xs font-medium">
                          {candlestickPattern.pattern.replace(/_/g, ' ')}
                        </span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          candlestickPattern.confidence === 'HIGH' 
                            ? 'bg-orange-500/30 text-orange-300' 
                            : 'bg-blue-500/30 text-blue-300'
                        }`}>
                          {candlestickPattern.confidence}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div onClick={(e) => e.stopPropagation()}>
                <CandlestickOnlyChart 
                  candles={candlestickCandles} 
                  height={500} 
                  onPatternDetected={setCandlestickPattern}
                />
              </div>
            </div>

            {/* TradingView Style Chart */}
            <div 
              className="bg-[#0a0a0a] rounded-lg p-4 border border-border/50 cursor-pointer hover:border-primary/50 transition-all"
              onClick={() => setFullscreenChart('tradingview')}
            >
              <div className="mb-3">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-foreground">📈 TradingView Style</h3>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-0.5 bg-green-500/40"></div>
                        <span className="text-muted-foreground">Cloud</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded bg-red-500"></div>
                        <span className="text-muted-foreground">SELL</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded bg-green-500"></div>
                        <span className="text-muted-foreground">BUY</span>
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground px-2 py-1 bg-muted/50 rounded">
                      Click to fullscreen
                    </span>
                  </div>
                </div>
                
                {/* TradingView Timeframe Selector */}
                {stock.chartData && availableTimeframes.length > 1 && (
                  <div className="flex items-center gap-2 mb-3" onClick={(e) => e.stopPropagation()}>
                    <span className="text-xs font-medium text-muted-foreground">Timeframe:</span>
                    <div className="flex gap-1">
                      {availableTimeframes.map((tf) => (
                        <button
                          key={tf}
                          onClick={(e) => {
                            e.stopPropagation()
                            setTradingviewTimeframe(tf)
                          }}
                          className={`px-3 py-1 rounded-lg font-medium text-xs transition-all ${
                            tradingviewTimeframe === tf
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted text-muted-foreground hover:bg-muted/80'
                          }`}
                        >
                          {tf}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div onClick={(e) => e.stopPropagation()}>
                <TradingViewChart candles={tradingviewCandles} height={500} />
              </div>
            </div>

          </div>
          
          {/* Note about instant switching */}
          {stock.chartData && availableTimeframes.length > 1 && (
            <div className="mt-3 text-center">
              <span className="text-xs text-muted-foreground">
                ✅ No API calls - All three charts switch timeframes instantly
              </span>
            </div>
          )}
        </div>

        {/* Additional Info */}
        <div className="px-6 py-4 border-t border-border bg-muted/10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground mb-1">Average Volume</p>
              <p className="font-semibold">{formatNumber(stock.avgVolume)}</p>
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Volume Ratio</p>
              <p className="font-semibold">{volumeRatio}x</p>
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Float Shares</p>
              <p className="font-semibold">{formatNumber(stock.float)}</p>
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Signal</p>
              <p className={`font-semibold ${
                stock.signal === 'BUY' ? 'text-green-400' :
                stock.signal === 'SELL' ? 'text-red-400' :
                'text-yellow-400'
              }`}>
                {stock.signal}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

interface StatCardProps {
  label: string
  value: string
  subValue?: string
  icon?: React.ReactNode
}

function StatCard({ label, value, subValue, icon }: StatCardProps) {
  return (
    <div className="bg-muted/50 rounded-lg p-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
        {icon}
        <span>{label}</span>
      </div>
      <div className="text-2xl font-bold mb-1">{value}</div>
      {subValue && (
        <div className="text-sm text-muted-foreground">{subValue}</div>
      )}
    </div>
  )
}

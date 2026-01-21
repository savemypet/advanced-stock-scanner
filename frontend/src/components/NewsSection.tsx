import { useState, useEffect } from 'react'
import { Newspaper, ExternalLink, Clock, Search } from 'lucide-react'
import { getAllNewsToday, getStockNews, searchStockNews, StockNews } from '../api/stockNewsApi'

interface NewsSectionProps {
  symbol?: string // If provided, show news for this symbol only
  userId?: string // OneSignal user ID for push notifications
}

export default function NewsSection({ symbol, userId }: NewsSectionProps) {
  const [news, setNews] = useState<Record<string, StockNews[]>>({})
  const [loading, setLoading] = useState(false)
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    loadNews()
  }, [symbol])

  const loadNews = async () => {
    setLoading(true)
    try {
      if (symbol) {
        // Get news for specific symbol
        const symbolNews = await getStockNews(symbol)
        setNews({ [symbol]: symbolNews })
      } else {
        // Get all news found today
        const allNews = await getAllNewsToday()
        setNews(allNews)
      }
    } catch (error) {
      console.error('Error loading news:', error)
      setNews({})
    } finally {
      setLoading(false)
    }
  }

  const handleSearchNews = async (searchSymbol: string) => {
    if (!searchSymbol) return
    
    setSearching(true)
    try {
      const result = await searchStockNews(searchSymbol, userId, true)
      if (result.news.length > 0) {
        // Reload news to show new results
        await loadNews()
        alert(`✅ Found ${result.news.length} news articles for ${searchSymbol}${result.notificationSent ? ' - Push notification sent!' : ''}`)
      } else {
        alert(`No news found for ${searchSymbol}`)
      }
    } catch (error) {
      console.error('Error searching news:', error)
      alert('Error searching for news')
    } finally {
      setSearching(false)
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    } catch {
      return dateString
    }
  }

  const symbols = Object.keys(news)
  const totalNewsCount = Object.values(news).reduce((sum, articles) => sum + articles.length, 0)

  return (
    <div className="bg-gray-900 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Newspaper className="w-5 h-5 text-blue-400" />
          <h2 className="text-xl font-bold text-white">
            📰 News Found Today
            {symbol && ` - ${symbol}`}
          </h2>
        </div>
        {symbol && (
          <button
            onClick={() => handleSearchNews(symbol)}
            disabled={searching}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg flex items-center gap-2 text-sm"
          >
            <Search className="w-4 h-4" />
            {searching ? 'Searching...' : 'Search News'}
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-gray-400 text-center py-8">Loading news...</div>
      ) : totalNewsCount === 0 ? (
        <div className="text-gray-400 text-center py-8">
          {symbol 
            ? `No news found for ${symbol} today. Click "Search News" to search the internet.`
            : 'No news found today. News will appear here when stocks qualify in the scanner.'}
        </div>
      ) : (
        <div className="space-y-6">
          {symbols.map(sym => (
            <div key={sym} className="border-b border-gray-800 pb-4 last:border-0">
              <h3 className="text-lg font-semibold text-white mb-3">
                {sym} - {news[sym].length} article{news[sym].length !== 1 ? 's' : ''}
              </h3>
              <div className="space-y-3">
                {news[sym].map((article) => (
                  <a
                    key={article.id}
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-4 bg-gray-800 hover:bg-gray-750 rounded-lg transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="text-white font-medium mb-1 line-clamp-2">
                          {article.title}
                        </h4>
                        <p className="text-gray-400 text-sm mb-2 line-clamp-2">
                          {article.snippet}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Newspaper className="w-3 h-3" />
                            {article.source}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatDate(article.publishedAt)}
                          </span>
                        </div>
                      </div>
                      <ExternalLink className="w-5 h-5 text-gray-500 flex-shrink-0 mt-1" />
                    </div>
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {!symbol && totalNewsCount > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-800 text-sm text-gray-400">
          Total: {totalNewsCount} news article{totalNewsCount !== 1 ? 's' : ''} across {symbols.length} stock{symbols.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  )
}

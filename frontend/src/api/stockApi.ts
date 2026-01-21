import axios from 'axios'
import { ScannerSettings, ScanResult, Stock } from '../types'
import { scanStocks as renderScanStocks, getStockQuote, markScanComplete, canScanNow, getTimeUntilNextScan } from './renderBackend'

// Use Render backend (bypasses Yahoo rate limits via different IP)
const USE_RENDER_BACKEND = true
const API_BASE_URL = '/api'

export const scanStocks = async (settings: ScannerSettings): Promise<ScanResult> => {
  try {
    if (USE_RENDER_BACKEND) {
      // Check rate limit (20s minimum between scans)
      if (!canScanNow()) {
        const waitTime = getTimeUntilNextScan()
        const rateLimitError = new Error(`Rate limited - wait ${waitTime}s`)
        ;(rateLimitError as any).isRateLimit = true
        throw rateLimitError
      }

      // Use Render backend - enforce 10 stock maximum
      const symbols = settings.symbols || ['GME', 'AMC', 'TSLA', 'PLTR', 'SOFI', 'NIO', 'LCID', 'ATER', 'AMD', 'NVDA']
      const limitedSymbols = symbols.slice(0, 10) // Yahoo Finance limit

      console.log(`📡 Using Render backend (${limitedSymbols.length}/10 stocks, 20s interval)`)

      const result = await renderScanStocks({
        symbols: limitedSymbols,
        minPrice: settings.minPrice,
        maxPrice: settings.maxPrice,
        maxFloat: settings.maxFloat,
        minGainPercent: settings.minGainPercent,
        volumeMultiplier: settings.volumeMultiplier,
      })

      markScanComplete() // Track last scan time

      // Convert to ScanResult format
      return {
        success: true,
        stocks: result.stocks.map(stock => ({
          symbol: stock.symbol,
          name: stock.name,
          price: stock.price,
          open: stock.open,
          high: stock.high,
          low: stock.low,
          volume: stock.volume,
          avgVolume: stock.avgVolume,
          float: stock.float,
          marketCap: stock.marketCap,
          changePercent: stock.changePercent,
          volumeMultiplier: stock.volume / (stock.avgVolume || 1),
          signal: stock.changePercent > 5 ? 'BUY' : stock.changePercent < -5 ? 'SELL' : 'HOLD',
          isHot: stock.changePercent > 10,
          hasNews: false,
          candles: stock.candles,
          updatedAt: Date.now(),
        })),
        count: result.count,
        apiStatus: {
          activeSource: 'Render Backend (Yahoo Finance)',
          fallbackAvailable: false,
          massiveRateLimit: null,
        }
      }
    } else {
      // Use local Python backend (fallback)
      const response = await axios.post(`${API_BASE_URL}/scan`, settings)
      return response.data
    }
  } catch (error: any) {
    console.error('Error scanning stocks:', error)
    
    // Check if it's a 429 rate limit error
    if (error.response?.status === 429 || error.response?.data?.rateLimited || error.message?.includes('wait')) {
      const rateLimitError = new Error(error.message || '429 Too Many Requests - Rate Limited')
      ;(rateLimitError as any).isRateLimit = true
      throw rateLimitError
    }
    
    throw error
  }
}

export const getStock = async (symbol: string, timeframe: string): Promise<Stock> => {
  try {
    if (USE_RENDER_BACKEND) {
      // Use Render backend for individual stock quotes
      console.log(`📊 Fetching ${symbol} (${timeframe}) via Render backend...`)
      const stock = await getStockQuote(symbol, timeframe as any)
      
      return {
        symbol: stock.symbol,
        name: stock.name,
        price: stock.price,
        open: stock.open,
        high: stock.high,
        low: stock.low,
        volume: stock.volume,
        avgVolume: stock.avgVolume,
        float: stock.float,
        marketCap: stock.marketCap,
        changePercent: stock.changePercent,
        volumeMultiplier: stock.volume / (stock.avgVolume || 1),
        signal: stock.changePercent > 5 ? 'BUY' : stock.changePercent < -5 ? 'SELL' : 'HOLD',
        isHot: stock.changePercent > 10,
        hasNews: false,
        candles: stock.candles,
        updatedAt: Date.now(),
      }
    } else {
      // Use local Python backend
      const response = await axios.get(`${API_BASE_URL}/stock/${symbol}`, {
        params: { timeframe }
      })
      return response.data.stock
    }
  } catch (error) {
    console.error(`Error fetching stock ${symbol}:`, error)
    throw error
  }
}

export const getSymbols = async (): Promise<string[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/symbols`)
    return response.data.symbols
  } catch (error) {
    console.error('Error fetching symbols:', error)
    throw error
  }
}

export const addSymbol = async (symbol: string): Promise<void> => {
  try {
    await axios.post(`${API_BASE_URL}/symbols`, { symbol })
  } catch (error) {
    console.error(`Error adding symbol ${symbol}:`, error)
    throw error
  }
}

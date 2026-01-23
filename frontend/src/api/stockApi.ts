import axios from 'axios'
import { ScannerSettings, ScanResult, Stock } from '../types'

// IBKR only mode - use local backend (no rate limits)
const API_BASE_URL = '/api'

export const scanStocks = async (settings: ScannerSettings): Promise<ScanResult> => {
  const startTime = Date.now()
  const url = `${API_BASE_URL}/scan`
  console.log(`📡 [SCANNER API] ===== SCAN REQUEST START =====`)
  console.log(`📡 [SCANNER API] URL: ${url}`)
  console.log(`📡 [SCANNER API] Settings:`, {
    minPrice: settings.minPrice,
    maxPrice: settings.maxPrice,
    minGainPercent: settings.minGainPercent,
    volumeMultiplier: settings.volumeMultiplier,
    displayCount: settings.displayCount
  })
  
  try {
    // IBKR only mode - use local backend (no rate limits)
    // Optimized timeout: 3 symbols × ~15s = ~45s, use 90s for safety
    console.log(`📡 [SCANNER API] Sending POST request to backend...`)
    const response = await axios.post(url, settings, {
      timeout: 90000 // 90 seconds (optimized for IBKR: 3 symbols, faster scan)
    })
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
    console.log(`✅ [SCANNER API] Response received in ${elapsed}s`)
    console.log(`✅ [SCANNER API] Response status: ${response.status}`)
    console.log(`✅ [SCANNER API] Response data:`, {
      success: response.data.success,
      stocksCount: response.data.stocks?.length || 0,
      apiStatus: response.data.apiStatus
    })
    console.log(`✅ [SCANNER API] ===== SCAN REQUEST SUCCESS =====`)
    return response.data

  } catch (error: any) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
    console.error(`❌ [SCANNER API] ===== SCAN REQUEST ERROR =====`)
    console.error(`❌ [SCANNER API] Error after ${elapsed}s:`, error)
    console.error(`❌ [SCANNER API] Error type:`, error.constructor.name)
    console.error(`❌ [SCANNER API] Error code:`, error.code)
    console.error(`❌ [SCANNER API] Error message:`, error.message)
    
    if (error.response) {
      console.error(`❌ [SCANNER API] Response status:`, error.response.status)
      console.error(`❌ [SCANNER API] Response data:`, error.response.data)
      
      // Handle IBKR connection errors (503 Service Unavailable)
      if (error.response.status === 503 && error.response.data?.error) {
        const errorDetails = error.response.data.details || {}
        console.error(`❌ [SCANNER API] IBKR connection failed:`, error.response.data.error)
        return {
          success: false,
          stocks: [],
          apiStatus: {
            ibkrConnected: false,
            activeSource: 'Not Connected',
            ibkrHost: errorDetails.ibkrHost || '127.0.0.1',
            ibkrPort: errorDetails.ibkrPort || 4001,
            ibkrAvailable: errorDetails.ibkrAvailable || false
          },
          error: error.response.data.error,
          errorDetails: errorDetails
        }
      }
    }
    
    // IBKR only mode - no rate limit handling needed
    // Return empty result on timeout/error instead of throwing
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.warn(`⏱️ [SCANNER API] Scan request timed out after ${elapsed}s - returning empty result`)
      return {
        success: false,
        stocks: [],
        apiStatus: {
          ibkrConnected: false,
          activeSource: 'Not Connected',
          ibkrPort: 0
        },
        error: 'Request timed out. The scan is taking too long.'
      }
    }
    throw error
  }
}

export const getStock = async (symbol: string, timeframe: string): Promise<Stock> => {
  const startTime = Date.now()
  const url = `${API_BASE_URL}/stock/${symbol}`
  console.log(`📡 [API] Starting request to: ${url}`)
  console.log(`📡 [API] Params: timeframe=${timeframe}`)
  
  try {
    // IBKR only mode - use local backend
    // Increased timeout for IBKR data fetching (can take 30-60 seconds)
    console.log(`📡 [API] Sending GET request...`)
    const response = await axios.get(url, {
      params: { timeframe },
      timeout: 60000 // 60 second timeout for IBKR data fetching
    })
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
    console.log(`✅ [API] Response received in ${elapsed}s`)
    console.log(`✅ [API] Response status: ${response.status}`)
    console.log(`✅ [API] Response data keys:`, Object.keys(response.data))
    
    if (response.data.stock) {
      console.log(`✅ [API] Stock data received:`, {
        symbol: response.data.stock.symbol,
        name: response.data.stock.name,
        price: response.data.stock.currentPrice,
        candles: response.data.stock.candles?.length || 0
      })
      return response.data.stock
    } else {
      console.error(`❌ [API] No stock data in response:`, response.data)
      throw new Error('No stock data in response')
    }
  } catch (error: any) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
    console.error(`❌ [API ERROR] Failed after ${elapsed}s for ${symbol}:`, error)
    console.error(`❌ [API ERROR] Error type:`, error.constructor.name)
    console.error(`❌ [API ERROR] Error code:`, error.code)
    console.error(`❌ [API ERROR] Error message:`, error.message)
    
    if (error.response) {
      console.error(`❌ [API ERROR] Response status:`, error.response.status)
      console.error(`❌ [API ERROR] Response data:`, error.response.data)
    }
    
    // Provide more helpful error messages
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new Error(`Request timed out. IBKR may be fetching data for ${symbol}. Please try again or check IBKR connection.`)
    }
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error)
    }
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

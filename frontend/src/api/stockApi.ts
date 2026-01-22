import axios from 'axios'
import { ScannerSettings, ScanResult, Stock } from '../types'

// IBKR only mode - use local backend (no rate limits)
const API_BASE_URL = '/api'

export const scanStocks = async (settings: ScannerSettings): Promise<ScanResult> => {
  try {
    // IBKR only mode - use local backend (no rate limits)
    // Add timeout to prevent hanging (30 seconds max)
    const response = await axios.post(`${API_BASE_URL}/scan`, settings, {
      timeout: 30000 // 30 second timeout
    })
    return response.data

  } catch (error: any) {
    console.error('Error scanning stocks:', error)
    // IBKR only mode - no rate limit handling needed
    // Return empty result on timeout/error instead of throwing
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.warn('Scan request timed out - returning empty result')
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
  try {
    // IBKR only mode - use local backend
    // Increased timeout for IBKR data fetching (can take 30-60 seconds)
    const response = await axios.get(`${API_BASE_URL}/stock/${symbol}`, {
      params: { timeframe },
      timeout: 60000 // 60 second timeout for IBKR data fetching
    })
    return response.data.stock
  } catch (error: any) {
    console.error(`Error fetching stock ${symbol}:`, error)
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

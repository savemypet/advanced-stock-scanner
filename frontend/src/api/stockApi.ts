import axios from 'axios'
import { ScannerSettings, ScanResult, Stock } from '../types'

const API_BASE_URL = '/api'

export const scanStocks = async (settings: ScannerSettings): Promise<ScanResult> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/scan`, settings)
    return response.data
  } catch (error: any) {
    console.error('Error scanning stocks:', error)
    
    // Check if it's a 429 rate limit error
    if (error.response?.status === 429 || error.response?.data?.rateLimited) {
      const rateLimitError = new Error('429 Too Many Requests - Rate Limited')
      ;(rateLimitError as any).isRateLimit = true
      throw rateLimitError
    }
    
    throw error
  }
}

export const getStock = async (symbol: string, timeframe: string): Promise<Stock> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/stock/${symbol}`, {
      params: { timeframe }
    })
    return response.data.stock
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

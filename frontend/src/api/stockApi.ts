import axios from 'axios'
import { ScannerSettings, ScanResult, Stock } from '../types'
import { scanStocks as renderScanStocks, getStockQuote, markScanComplete, canScanNow, getTimeUntilNextScan } from './renderBackend'
import { lockApi } from '../components/SettingsPanel'

// Use Render backend (bypasses Yahoo rate limits via different IP)
const USE_RENDER_BACKEND = true
const API_BASE_URL = '/api'

export const scanStocks = async (settings: ScannerSettings): Promise<ScanResult> => {
  try {
    // IBKR only mode - use local backend (no rate limits)
    const response = await axios.post(`${API_BASE_URL}/scan`, settings)
    return response.data

  } catch (error: any) {
    console.error('Error scanning stocks:', error)
    // IBKR only mode - no rate limit handling needed
    throw error
  }
}

export const getStock = async (symbol: string, timeframe: string): Promise<Stock> => {
  try {
    // IBKR only mode - use local backend
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

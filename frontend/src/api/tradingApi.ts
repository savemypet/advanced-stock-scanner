import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export interface DailyTradeStatus {
  buyUsed: boolean
  sellUsed: boolean
}

export interface DailyTradeStatusRange {
  [date: string]: DailyTradeStatus
}

export async function getAccountBalance(): Promise<number> {
  try {
    const response = await axios.get(`${API_BASE_URL}/trade/account-balance`, {
      timeout: 10000
    })
    
    if (response.data.success) {
      return response.data.balance || 0
    }
    
    return 0
  } catch (error: any) {
    console.error('Error getting account balance:', error)
    return 0
  }
}

export async function getDailyTradeStatus(date: string): Promise<DailyTradeStatus | null> {
  try {
    const response = await axios.get(`${API_BASE_URL}/trade/daily-status`, {
      params: { date },
      timeout: 5000
    })
    
    if (response.data.success) {
      return {
        buyUsed: response.data.buyUsed || false,
        sellUsed: response.data.sellUsed || false
      }
    }
    
    return null
  } catch (error: any) {
    console.error('Error getting daily trade status:', error)
    return null
  }
}

export async function getDailyTradeStatusRange(): Promise<DailyTradeStatusRange> {
  try {
    const response = await axios.get(`${API_BASE_URL}/trade/daily-status-range`, {
      timeout: 5000
    })
    
    if (response.data.success) {
      return response.data.status || {}
    }
    
    return {}
  } catch (error: any) {
    console.error('Error getting daily trade status range:', error)
    return {}
  }
}

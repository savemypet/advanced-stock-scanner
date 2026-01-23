/**
 * Ollama AI API Client
 * Handles communication with Ollama service for candlestick analysis
 */

export interface OllamaAnalysis {
  pattern: string | null;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  reasoning: string;
  entryPrice: number | null;
  stopLoss: number | null;
  takeProfit: number | null;
  riskRewardRatio?: number | null;
  timestamp?: string;
  model?: string;
  candleCount?: number;
  volumeRatio?: number;
}

export interface OllamaAnalysisResponse {
  success: boolean;
  analysis?: OllamaAnalysis;
  error?: string;
}

export interface OllamaStatus {
  available: boolean;
  models?: string[];
  baseUrl?: string;
  error?: string;
}

export interface TradeDecision {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  reasoning: string;
  entryPrice: number | null;
  stopLoss: number | null;
  takeProfit: number | null;
  pattern: string | null;
  timestamp: string;
  readyToExecute: boolean;
  recommendedQuantity?: number;
}

export interface TradeDecisionResponse {
  success: boolean;
  decision?: TradeDecision;
  error?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Check Ollama connection status
 */
export async function checkOllamaStatus(): Promise<OllamaStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ollama/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error('❌ [OLLAMA] Status check failed:', error);
    return {
      available: false,
      error: error.message || 'Failed to check Ollama status',
    };
  }
}

/**
 * Analyze candlestick patterns using Ollama
 */
export async function analyzeCandlesticks(
  symbol: string,
  candles: any[],
  currentPrice: number,
  volume: number,
  avgVolume: number,
  detectedPatterns?: any[] | null
): Promise<OllamaAnalysisResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ollama/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        symbol,
        candles,
        currentPrice,
        volume,
        avgVolume,
        detectedPatterns: detectedPatterns || undefined,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('❌ [OLLAMA] Analysis failed:', error);
    return {
      success: false,
      error: error.message || 'Failed to analyze candlesticks',
    };
  }
}

/**
 * Get AI trading decision (BUY/SELL/HOLD)
 */
export async function getTradeDecision(
  symbol: string,
  candles: any[],
  currentPrice: number,
  volume: number,
  avgVolume: number,
  accountBalance: number = 0,
  riskTolerance: 'LOW' | 'MEDIUM' | 'HIGH' = 'MEDIUM'
): Promise<TradeDecisionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ollama/trade-decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        symbol,
        candles,
        currentPrice,
        volume,
        avgVolume,
        accountBalance,
        riskTolerance,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('❌ [OLLAMA] Trade decision failed:', error);
    return {
      success: false,
      error: error.message || 'Failed to get trade decision',
    };
  }
}

/**
 * Teach Ollama a new candlestick pattern
 */
export async function teachPattern(
  patternName: string,
  description: string,
  examples: any[]
): Promise<{ success: boolean; message?: string; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ollama/teach`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        patternName,
        description,
        examples,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error('❌ [OLLAMA] Teaching failed:', error);
    return {
      success: false,
      error: error.message || 'Failed to teach pattern',
    };
  }
}

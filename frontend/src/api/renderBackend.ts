/**
 * Render Backend API Client
 * 
 * Uses Save My Pet Emergency backend on Render to proxy Yahoo Finance
 * Benefits:
 * - Different IP address (bypasses rate limits)
 * - Redis caching (95% fewer API calls)
 * - No CORS issues
 * - OneSignal push notifications
 * 
 * LIMITS:
 * - Max 10 stocks per scan (Yahoo Finance limit)
 * - Minimum 20 seconds between scans (recommended)
 */

const RENDER_BACKEND_URL = 'https://savemypet-backend.onrender.com/api/trpc';

export interface StockData {
  symbol: string;
  name: string;
  price: number;
  previousClose: number;
  changePercent: number;
  volume: number;
  avgVolume: number;
  open: number;
  high: number;
  low: number;
  marketCap: number;
  float: number;
  candles: Array<{
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
}

export interface ScanCriteria {
  symbols: string[];
  minPrice?: number;
  maxPrice?: number;
  maxFloat?: number;
  minGainPercent?: number;
  volumeMultiplier?: number;
}

export interface ScanResult {
  success: boolean;
  stocks: StockData[];
  count: number;
  scannedAt: string;
}

/**
 * Scan multiple stocks via Render backend
 * LIMIT: Max 10 stocks per scan
 */
export async function scanStocks(criteria: ScanCriteria): Promise<ScanResult> {
  // Enforce Yahoo Finance limit: Max 10 stocks
  if (criteria.symbols.length > 10) {
    console.warn(`⚠️ Too many symbols (${criteria.symbols.length}). Limiting to 10 for Yahoo Finance.`);
    criteria.symbols = criteria.symbols.slice(0, 10);
  }

  // Using mutation (supports POST requests)
  const url = `${RENDER_BACKEND_URL}/stocks.scan`;
  const input = {
    symbols: criteria.symbols,
    minPrice: criteria.minPrice ?? 1,
    maxPrice: criteria.maxPrice ?? 200,
    maxFloat: criteria.maxFloat ?? 500000000,
    minGainPercent: criteria.minGainPercent ?? 2,
    volumeMultiplier: criteria.volumeMultiplier ?? 1.5,
  };

  console.log(`📡 Scanning ${criteria.symbols.length} stocks via Render backend...`);

  // Mutation supports POST requests - input goes directly in body (not wrapped)
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    throw new Error(`Render backend error: ${response.status}`);
  }

  const data = await response.json();
  return data.result.data;
}

/**
 * Get quote with candles for a single stock
 * Cached for 30 seconds on Render backend
 */
export async function getStockQuote(
  symbol: string,
  timeframe: '1m' | '5m' | '1h' | '24h' = '5m'
): Promise<StockData> {
  // Using mutation (supports POST requests)
  const url = `${RENDER_BACKEND_URL}/stocks.getQuote`;
  const input = { symbol, timeframe };

  console.log(`📊 Fetching ${symbol} (${timeframe}) via Render backend...`);

  // Mutation supports POST requests - input goes directly in body (not wrapped)
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    throw new Error(`Render backend error: ${response.status}`);
  }

  const data = await response.json();
  return data.result.data.stock;
}

/**
 * Send OneSignal push notification for qualifying stocks
 */
export async function sendStockAlert(
  userId: string,
  stocks: Array<{
    symbol: string;
    price: number;
    changePercent: number;
    volume: number;
  }>,
  title?: string,
  message?: string
): Promise<{ success: boolean; notificationId?: string; recipients?: number }> {
  const url = `${RENDER_BACKEND_URL}/stocks.notify`;

  console.log(`📲 Sending push notification for ${stocks.length} stocks...`);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userId,
      stocks,
      title,
      message,
    }),
  });

  if (!response.ok) {
    throw new Error(`Render backend error: ${response.status}`);
  }

  const data = await response.json();
  return data.result.data;
}

/**
 * Check if Render backend is healthy
 */
export async function checkBackendHealth(): Promise<{
  success: boolean;
  status: string;
  limits: {
    maxSymbols: number;
    minInterval: number;
    cacheTime: number;
  };
}> {
  const url = `${RENDER_BACKEND_URL}/stocks.health`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Render backend error: ${response.status}`);
  }

  const data = await response.json();
  return data.result.data;
}

/**
 * Helper: Enforce 20-second minimum interval between scans
 */
let lastScanTime = 0;

export function canScanNow(): boolean {
  const now = Date.now();
  const timeSinceLastScan = (now - lastScanTime) / 1000;
  return timeSinceLastScan >= 20;
}

export function getTimeUntilNextScan(): number {
  const now = Date.now();
  const timeSinceLastScan = (now - lastScanTime) / 1000;
  const remaining = Math.max(0, 20 - timeSinceLastScan);
  return Math.ceil(remaining);
}

export function markScanComplete(): void {
  lastScanTime = Date.now();
}

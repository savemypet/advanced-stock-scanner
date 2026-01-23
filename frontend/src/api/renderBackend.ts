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

const RENDER_BACKEND_URL = 'https://savemypet-backend.onrender.com';
const RENDER_BACKEND_TRPC = 'https://savemypet-backend.onrender.com/api/trpc';
const RENDER_BACKEND_REST = 'https://savemypet-backend.onrender.com/api/stocks';

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
  userId?: string; // Optional: OneSignal user ID for push notifications
  useYahoo?: boolean;
  useSerpAPI?: boolean;
  useAlphaVantage?: boolean;
  useMassive?: boolean;
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

  // Use simple REST endpoint (more reliable than tRPC)
  const input = {
    symbols: criteria.symbols,
    minPrice: criteria.minPrice ?? 1,
    maxPrice: criteria.maxPrice ?? 200,
    // maxFloat removed - no longer filtering by float
    minGainPercent: criteria.minGainPercent ?? 2,
    volumeMultiplier: criteria.volumeMultiplier ?? 1.5,
    userId: criteria.userId, // Optional: For push notifications when news is found
    // API Selection
    useYahoo: criteria.useYahoo ?? true,
    useSerpAPI: criteria.useSerpAPI ?? false,
    useAlphaVantage: criteria.useAlphaVantage ?? false,
    useMassive: criteria.useMassive ?? false,
  };

  console.log(`📡 Scanning ${criteria.symbols.length} stocks via Render backend...`);

  // Simple REST POST endpoint
  const response = await fetch(`${RENDER_BACKEND_REST}/scan`, {
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
  // Use simple REST endpoint (more reliable than tRPC)
  console.log(`📊 Fetching ${symbol} (${timeframe}) via Render backend...`);

  // Simple REST GET endpoint
  const response = await fetch(`${RENDER_BACKEND_REST}/quote/${symbol}?timeframe=${timeframe}`, {
    method: 'GET',
  });
  if (!response.ok) {
    throw new Error(`Render backend error: ${response.status}`);
  }

  const data = await response.json();
  // REST endpoint returns stock directly
  return data.stock;
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

  const response = await fetch(`${RENDER_BACKEND_TRPC}/stocks.notify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input: {
        userId,
        stocks,
        title,
        message,
      },
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
  const url = `${RENDER_BACKEND_TRPC}/stocks.health`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Render backend error: ${response.status}`);
  }

  const data = await response.json();
  return data.result.data.json;
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

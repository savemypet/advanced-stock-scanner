export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma20?: number;
  ma50?: number;
  ma200?: number;
}

export interface Stock {
  symbol: string;
  name: string;
  currentPrice: number;
  previousClose: number;
  openPrice: number;
  dayHigh: number;
  dayLow: number;
  volume: number;
  avgVolume: number;
  float: number;
  changePercent: number;
  changeAmount: number;
  candles: Candle[];
  chartData?: {
    '1m'?: Candle[];
    '5m'?: Candle[];
    '1h'?: Candle[];
    '24h'?: Candle[];
  };
  volumeProfile?: {
    '1m'?: { buy: number; sell: number };
    '5m'?: { buy: number; sell: number };
    '15m'?: { buy: number; sell: number };
    '1h'?: { buy: number; sell: number };
  };
  signal?: 'BUY' | 'SELL' | 'HOLD';
  isHot?: boolean;
  hasNews?: boolean;
  newsCount?: number;
  lastUpdated: string;
}

export interface NewsItem {
  headline: string;
  summary: string;
  source: string;
  url: string;
  timestamp: number;  // Unix timestamp
  category: string;
}

export type ChartTimeframe = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '24h' | '1week' | '1month';

export interface ScannerSettings {
  minPrice: number;
  maxPrice: number;
  maxFloat: number;
  minGainPercent: number;
  volumeMultiplier: number;
  displayCount: number;
  chartTimeframe: ChartTimeframe;
  autoAdd: boolean;
  realTimeUpdates: boolean;
  updateInterval: number; // seconds between updates
  notificationsEnabled: boolean;
  notifyOnNewStocks: boolean;
  // API Selection
  useYahoo: boolean;
  useSerpAPI: boolean;
  useAlphaVantage: boolean;
  useMassive: boolean;
}

export interface ScanResult {
  success: boolean;
  stocks: Stock[];
  timestamp: string;
  error?: string;
}

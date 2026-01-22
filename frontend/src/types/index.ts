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
    '2m'?: Candle[];
    '3m'?: Candle[];
    '5m'?: Candle[];
    '15m'?: Candle[];
    '30m'?: Candle[];
    '90m'?: Candle[];
    '1h'?: Candle[];
    '4h'?: Candle[];
    '24h'?: Candle[];
    '1week'?: Candle[];
    '3month'?: Candle[];
    '6month'?: Candle[];
    '1month'?: Candle[];
    '1year'?: Candle[];
    '2year'?: Candle[];
    '5year'?: Candle[];
    '10year'?: Candle[];
    'ytd'?: Candle[];
    'max'?: Candle[];
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

export type ChartTimeframe = '1m' | '2m' | '3m' | '5m' | '15m' | '30m' | '90m' | '1h' | '4h' | '24h' | '1week' | '3month' | '6month' | '1month' | '1year' | '2year' | '5year' | '10year' | 'ytd' | 'max';

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

export interface ApiStatus {
  activeSource: string;
  ibkrConnected: boolean;
  ibkrHost?: string;
  ibkrPort?: number;
  ibkrUsername?: string;
  fallbackAvailable?: boolean;
  recommendedInterval?: number;
  currentDelay?: number;
  autoAdjusted?: boolean;
  mode?: string;
  scanSpeed?: string;
  method?: string;
}

export interface ScanResult {
  success: boolean;
  stocks: Stock[];
  timestamp: string;
  error?: string;
  apiStatus?: ApiStatus;
}

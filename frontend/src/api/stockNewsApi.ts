/**
 * Stock News API Client
 * 
 * Fetches news from Render backend for stocks found in scanner
 */

const RENDER_BACKEND_URL = 'https://savemypet-backend.onrender.com/api/stocks';

export interface StockNews {
  id: string;
  symbol: string;
  title: string;
  source: string;
  url: string;
  snippet: string;
  publishedAt: string;
  foundAt: string;
}

/**
 * Get news for a stock symbol (today's news only)
 */
export async function getStockNews(symbol: string, date?: string): Promise<StockNews[]> {
  const dateParam = date ? `&date=${date}` : '';
  const response = await fetch(`${RENDER_BACKEND_URL}/news/${symbol}${dateParam ? '?' + dateParam : ''}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch news: ${response.status}`);
  }
  
  const data = await response.json();
  return data.news || [];
}

/**
 * Search for news on a stock and optionally send push notification
 */
export async function searchStockNews(
  symbol: string,
  userId?: string,
  sendNotification: boolean = true
): Promise<{ news: StockNews[]; notificationSent: boolean; notificationId?: string }> {
  const response = await fetch(`${RENDER_BACKEND_URL}/news/${symbol}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userId,
      sendNotification,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to search news: ${response.status}`);
  }
  
  const data = await response.json();
  return {
    news: data.news || [],
    notificationSent: data.notificationSent || false,
    notificationId: data.notificationId,
  };
}

/**
 * Get all news found today for all stocks
 */
export async function getAllNewsToday(): Promise<Record<string, StockNews[]>> {
  const response = await fetch(`${RENDER_BACKEND_URL}/news/all`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch all news: ${response.status}`);
  }
  
  const data = await response.json();
  return data.newsBySymbol || {};
}

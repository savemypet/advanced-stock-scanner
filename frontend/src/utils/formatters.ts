export function formatNumber(num: number | undefined | null): string {
  if (num == null || isNaN(num)) {
    return 'N/A'
  }
  if (num >= 1_000_000_000) {
    return `${(num / 1_000_000_000).toFixed(2)}B`
  }
  if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(2)}M`
  }
  if (num >= 1_000) {
    return `${(num / 1_000).toFixed(2)}K`
  }
  return num.toFixed(0)
}

export function formatCurrency(num: number | undefined | null): string {
  if (num == null || isNaN(num)) {
    return 'N/A'
  }
  return `$${num.toFixed(2)}`
}

export function formatPercent(num: number | undefined | null): string {
  if (num == null || isNaN(num)) {
    return 'N/A'
  }
  return `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`
}

export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

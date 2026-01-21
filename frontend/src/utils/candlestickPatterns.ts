import { Candle } from '../types'

export type PatternType = 
  // Neutral patterns
  | 'DOJI' | 'SPINNING_TOP' | 'MARUBOZU' | 'STAR'
  // Bullish single patterns
  | 'HAMMER' | 'INVERTED_HAMMER' | 'DRAGONFLY_DOJI' | 'BULLISH_SPINNING_TOP'
  // Bullish double patterns
  | 'BULLISH_KICKER' | 'BULLISH_ENGULFING' | 'BULLISH_HARAMI' | 'PIERCING_LINE' | 'TWEEZER_BOTTOM'
  // Bullish triple patterns
  | 'MORNING_STAR' | 'MORNING_DOJI_STAR' | 'BULLISH_ABANDONED_BABY' | 'THREE_WHITE_SOLDIERS' 
  | 'BULLISH_THREE_LINE_STRIKE' | 'THREE_INSIDE_UP' | 'THREE_OUTSIDE_UP'
  // Bearish single patterns
  | 'SHOOTING_STAR' | 'HANGING_MAN' | 'GRAVESTONE_DOJI' | 'BEARISH_SPINNING_TOP'
  // Bearish double patterns
  | 'BEARISH_KICKER' | 'BEARISH_ENGULFING' | 'BEARISH_HARAMI' | 'DARK_CLOUD_COVER' | 'TWEEZER_TOP'
  // Bearish triple patterns
  | 'EVENING_STAR' | 'EVENING_DOJI_STAR' | 'BEARISH_ABANDONED_BABY' | 'THREE_BLACK_CROWS'
  | 'BEARISH_THREE_LINE_STRIKE' | 'THREE_INSIDE_DOWN' | 'THREE_OUTSIDE_DOWN'

export interface PatternSignal {
  pattern: PatternType
  signal: 'BUY' | 'SELL'
  confidence: 'HIGH' | 'MEDIUM' | 'LOW'
  candleIndex: number
  description: string
}

// Helper functions to analyze candle characteristics
function getCandleBody(candle: Candle): number {
  return Math.abs(candle.close - candle.open)
}

function getUpperShadow(candle: Candle): number {
  return candle.high - Math.max(candle.open, candle.close)
}

function getLowerShadow(candle: Candle): number {
  return Math.min(candle.open, candle.close) - candle.low
}

function isBullish(candle: Candle): boolean {
  return candle.close > candle.open
}

function isBearish(candle: Candle): boolean {
  return candle.close < candle.open
}

function isDoji(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const totalRange = candle.high - candle.low
  return totalRange > 0 && body / totalRange < 0.1
}

function isSpinningTop(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const upperShadow = getUpperShadow(candle)
  const lowerShadow = getLowerShadow(candle)
  const totalRange = candle.high - candle.low
  
  return (
    body < totalRange * 0.3 &&
    upperShadow > body &&
    lowerShadow > body &&
    body > 0
  )
}

function isMarubozu(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const upperShadow = getUpperShadow(candle)
  const lowerShadow = getLowerShadow(candle)
  const totalRange = candle.high - candle.low
  
  return (
    body > totalRange * 0.95 &&
    upperShadow < totalRange * 0.025 &&
    lowerShadow < totalRange * 0.025
  )
}

function isStar(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const totalRange = candle.high - candle.low
  
  return (
    body < totalRange * 0.2 &&
    body > 0
  )
}

// SINGLE CANDLE PATTERNS

export function isHammer(candle: Candle, prevCandle?: Candle): boolean {
  const body = getCandleBody(candle)
  const lowerShadow = getLowerShadow(candle)
  const upperShadow = getUpperShadow(candle)
  
  return (
    lowerShadow > body * 2 &&
    upperShadow < body * 0.3 &&
    isBullish(candle) &&
    body > 0
  )
}

export function isInvertedHammer(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const lowerShadow = getLowerShadow(candle)
  const upperShadow = getUpperShadow(candle)
  
  return (
    upperShadow > body * 2 &&
    lowerShadow < body * 0.3 &&
    body > 0
  )
}

export function isDragonflyDoji(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const lowerShadow = getLowerShadow(candle)
  const upperShadow = getUpperShadow(candle)
  
  return (
    isDoji(candle) &&
    lowerShadow > (candle.high - candle.low) * 0.6 &&
    upperShadow < (candle.high - candle.low) * 0.1
  )
}

export function isShootingStar(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const lowerShadow = getLowerShadow(candle)
  const upperShadow = getUpperShadow(candle)
  
  return (
    upperShadow > body * 2 &&
    lowerShadow < body * 0.3 &&
    isBearish(candle) &&
    body > 0
  )
}

export function isHangingMan(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const lowerShadow = getLowerShadow(candle)
  const upperShadow = getUpperShadow(candle)
  
  return (
    lowerShadow > body * 2 &&
    upperShadow < body * 0.3 &&
    isBearish(candle) &&
    body > 0
  )
}

export function isGravestoneDoji(candle: Candle): boolean {
  const body = getCandleBody(candle)
  const lowerShadow = getLowerShadow(candle)
  const upperShadow = getUpperShadow(candle)
  
  return (
    isDoji(candle) &&
    upperShadow > (candle.high - candle.low) * 0.6 &&
    lowerShadow < (candle.high - candle.low) * 0.1
  )
}

// DOUBLE CANDLE PATTERNS

export function isBullishEngulfing(prev: Candle, current: Candle): boolean {
  return (
    isBearish(prev) &&
    isBullish(current) &&
    current.open < prev.close &&
    current.close > prev.open
  )
}

export function isBearishEngulfing(prev: Candle, current: Candle): boolean {
  return (
    isBullish(prev) &&
    isBearish(current) &&
    current.open > prev.close &&
    current.close < prev.open
  )
}

export function isBullishHarami(prev: Candle, current: Candle): boolean {
  return (
    isBearish(prev) &&
    isBullish(current) &&
    current.open > prev.close &&
    current.close < prev.open &&
    getCandleBody(current) < getCandleBody(prev) * 0.5
  )
}

export function isBearishHarami(prev: Candle, current: Candle): boolean {
  return (
    isBullish(prev) &&
    isBearish(current) &&
    current.open < prev.close &&
    current.close > prev.open &&
    getCandleBody(current) < getCandleBody(prev) * 0.5
  )
}

export function isPiercingLine(prev: Candle, current: Candle): boolean {
  return (
    isBearish(prev) &&
    isBullish(current) &&
    current.open < prev.low &&
    current.close > (prev.open + prev.close) / 2 &&
    current.close < prev.open
  )
}

export function isDarkCloudCover(prev: Candle, current: Candle): boolean {
  return (
    isBullish(prev) &&
    isBearish(current) &&
    current.open > prev.high &&
    current.close < (prev.open + prev.close) / 2 &&
    current.close > prev.open
  )
}

export function isTweezerBottom(prev: Candle, current: Candle): boolean {
  const tolerance = (prev.low + current.low) * 0.002 // 0.2% tolerance
  return Math.abs(prev.low - current.low) < tolerance && isBullish(current)
}

export function isTweezerTop(prev: Candle, current: Candle): boolean {
  const tolerance = (prev.high + current.high) * 0.002
  return Math.abs(prev.high - current.high) < tolerance && isBearish(current)
}

export function isBullishKicker(prev: Candle, current: Candle): boolean {
  return (
    isBearish(prev) &&
    isBullish(current) &&
    current.open > prev.close &&
    getCandleBody(prev) > (prev.high - prev.low) * 0.7 &&
    getCandleBody(current) > (current.high - current.low) * 0.7
  )
}

export function isBearishKicker(prev: Candle, current: Candle): boolean {
  return (
    isBullish(prev) &&
    isBearish(current) &&
    current.open < prev.close &&
    getCandleBody(prev) > (prev.high - prev.low) * 0.7 &&
    getCandleBody(current) > (current.high - current.low) * 0.7
  )
}

// TRIPLE CANDLE PATTERNS

export function isMorningStar(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBearish(first) &&
    getCandleBody(second) < getCandleBody(first) * 0.3 &&
    isBullish(third) &&
    third.close > (first.open + first.close) / 2
  )
}

export function isEveningStar(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBullish(first) &&
    getCandleBody(second) < getCandleBody(first) * 0.3 &&
    isBearish(third) &&
    third.close < (first.open + first.close) / 2
  )
}

export function isThreeWhiteSoldiers(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBullish(first) &&
    isBullish(second) &&
    isBullish(third) &&
    second.close > first.close &&
    third.close > second.close &&
    second.open > first.open &&
    second.open < first.close &&
    third.open > second.open &&
    third.open < second.close
  )
}

export function isThreeBlackCrows(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBearish(first) &&
    isBearish(second) &&
    isBearish(third) &&
    second.close < first.close &&
    third.close < second.close &&
    second.open < first.open &&
    second.open > first.close &&
    third.open < second.open &&
    third.open > second.close
  )
}

export function isThreeInsideUp(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBullishHarami(first, second) &&
    isBullish(third) &&
    third.close > second.close
  )
}

export function isThreeInsideDown(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBearishHarami(first, second) &&
    isBearish(third) &&
    third.close < second.close
  )
}

export function isThreeOutsideUp(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBullishEngulfing(first, second) &&
    isBullish(third) &&
    third.close > second.close
  )
}

export function isThreeOutsideDown(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBearishEngulfing(first, second) &&
    isBearish(third) &&
    third.close < second.close
  )
}

export function isMorningDojiStar(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBearish(first) &&
    isDoji(second) &&
    second.high < first.close &&
    isBullish(third) &&
    third.close > (first.open + first.close) / 2
  )
}

export function isEveningDojiStar(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBullish(first) &&
    isDoji(second) &&
    second.low > first.close &&
    isBearish(third) &&
    third.close < (first.open + first.close) / 2
  )
}

export function isBullishAbandonedBaby(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBearish(first) &&
    isDoji(second) &&
    second.high < first.low && // Gap down
    isBullish(third) &&
    third.open > second.high && // Gap up
    third.close > first.close
  )
}

export function isBearishAbandonedBaby(first: Candle, second: Candle, third: Candle): boolean {
  return (
    isBullish(first) &&
    isDoji(second) &&
    second.low > first.high && // Gap up
    isBearish(third) &&
    third.open < second.low && // Gap down
    third.close < first.close
  )
}

export function isBullishThreeLineStrike(first: Candle, second: Candle, third: Candle, fourth: Candle): boolean {
  return (
    isBullish(first) &&
    isBullish(second) &&
    isBullish(third) &&
    second.close > first.close &&
    third.close > second.close &&
    isBearish(fourth) &&
    fourth.open > third.close &&
    fourth.close < first.open
  )
}

export function isBearishThreeLineStrike(first: Candle, second: Candle, third: Candle, fourth: Candle): boolean {
  return (
    isBearish(first) &&
    isBearish(second) &&
    isBearish(third) &&
    second.close < first.close &&
    third.close < second.close &&
    isBullish(fourth) &&
    fourth.open < third.close &&
    fourth.close > first.open
  )
}

// MAIN PATTERN DETECTION FUNCTION
export function detectPatterns(candles: Candle[]): PatternSignal[] {
  const patterns: PatternSignal[] = []
  
  if (candles.length < 2) return patterns
  
  for (let i = 1; i < candles.length; i++) {
    const current = candles[i]
    const prev = i >= 1 ? candles[i - 1] : null
    const prevPrev = i >= 2 ? candles[i - 2] : null
    const prevPrevPrev = i >= 3 ? candles[i - 3] : null
    
    // Four candle patterns (highest priority)
    if (prevPrevPrev && prevPrev && prev) {
      if (isBullishThreeLineStrike(prevPrevPrev, prevPrev, prev, current)) {
        patterns.push({
          pattern: 'BULLISH_THREE_LINE_STRIKE',
          signal: 'BUY',
          confidence: 'HIGH',
          candleIndex: i,
          description: 'Bullish Three Line Strike - Powerful continuation'
        })
        continue
      } else if (isBearishThreeLineStrike(prevPrevPrev, prevPrev, prev, current)) {
        patterns.push({
          pattern: 'BEARISH_THREE_LINE_STRIKE',
          signal: 'SELL',
          confidence: 'HIGH',
          candleIndex: i,
          description: 'Bearish Three Line Strike - Powerful continuation'
        })
        continue
      }
    }
    
    // Triple candle patterns (high priority)
    if (prevPrev && prev && isBullishAbandonedBaby(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'BULLISH_ABANDONED_BABY',
        signal: 'BUY',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Bullish Abandoned Baby - Extremely rare bullish reversal'
      })
    } else if (prevPrev && prev && isBearishAbandonedBaby(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'BEARISH_ABANDONED_BABY',
        signal: 'SELL',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Bearish Abandoned Baby - Extremely rare bearish reversal'
      })
    } else if (prevPrev && prev && isMorningDojiStar(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'MORNING_DOJI_STAR',
        signal: 'BUY',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Morning Doji Star - Strong bullish reversal with doji'
      })
    } else if (prevPrev && prev && isEveningDojiStar(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'EVENING_DOJI_STAR',
        signal: 'SELL',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Evening Doji Star - Strong bearish reversal with doji'
      })
    } else if (prevPrev && prev && isMorningStar(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'MORNING_STAR',
        signal: 'BUY',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Morning Star - Strong bullish reversal'
      })
    } else if (prevPrev && prev && isEveningStar(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'EVENING_STAR',
        signal: 'SELL',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Evening Star - Strong bearish reversal'
      })
    } else if (prevPrev && prev && isThreeWhiteSoldiers(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'THREE_WHITE_SOLDIERS',
        signal: 'BUY',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Three White Soldiers - Strong uptrend'
      })
    } else if (prevPrev && prev && isThreeBlackCrows(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'THREE_BLACK_CROWS',
        signal: 'SELL',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Three Black Crows - Strong downtrend'
      })
    } else if (prevPrev && prev && isThreeInsideUp(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'THREE_INSIDE_UP',
        signal: 'BUY',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Three Inside Up - Bullish confirmation'
      })
    } else if (prevPrev && prev && isThreeInsideDown(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'THREE_INSIDE_DOWN',
        signal: 'SELL',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Three Inside Down - Bearish confirmation'
      })
    } else if (prevPrev && prev && isThreeOutsideUp(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'THREE_OUTSIDE_UP',
        signal: 'BUY',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Three Outside Up - Strong bullish signal'
      })
    } else if (prevPrev && prev && isThreeOutsideDown(prevPrev, prev, current)) {
      patterns.push({
        pattern: 'THREE_OUTSIDE_DOWN',
        signal: 'SELL',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Three Outside Down - Strong bearish signal'
      })
    }
    // Double candle patterns (medium priority)
    else if (prev && isBullishKicker(prev, current)) {
      patterns.push({
        pattern: 'BULLISH_KICKER',
        signal: 'BUY',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Bullish Kicker - Extremely strong reversal'
      })
    } else if (prev && isBearishKicker(prev, current)) {
      patterns.push({
        pattern: 'BEARISH_KICKER',
        signal: 'SELL',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Bearish Kicker - Extremely strong reversal'
      })
    } else if (prev && isBullishEngulfing(prev, current)) {
      patterns.push({
        pattern: 'BULLISH_ENGULFING',
        signal: 'BUY',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Bullish Engulfing - Strong buy signal'
      })
    } else if (prev && isBearishEngulfing(prev, current)) {
      patterns.push({
        pattern: 'BEARISH_ENGULFING',
        signal: 'SELL',
        confidence: 'HIGH',
        candleIndex: i,
        description: 'Bearish Engulfing - Strong sell signal'
      })
    } else if (prev && isBullishHarami(prev, current)) {
      patterns.push({
        pattern: 'BULLISH_HARAMI',
        signal: 'BUY',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Bullish Harami - Potential reversal'
      })
    } else if (prev && isBearishHarami(prev, current)) {
      patterns.push({
        pattern: 'BEARISH_HARAMI',
        signal: 'SELL',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Bearish Harami - Potential reversal'
      })
    } else if (prev && isPiercingLine(prev, current)) {
      patterns.push({
        pattern: 'PIERCING_LINE',
        signal: 'BUY',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Piercing Line - Bullish reversal'
      })
    } else if (prev && isDarkCloudCover(prev, current)) {
      patterns.push({
        pattern: 'DARK_CLOUD_COVER',
        signal: 'SELL',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Dark Cloud Cover - Bearish reversal'
      })
    } else if (prev && isTweezerBottom(prev, current)) {
      patterns.push({
        pattern: 'TWEEZER_BOTTOM',
        signal: 'BUY',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Tweezer Bottom - Support level'
      })
    } else if (prev && isTweezerTop(prev, current)) {
      patterns.push({
        pattern: 'TWEEZER_TOP',
        signal: 'SELL',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Tweezer Top - Resistance level'
      })
    }
    // Single candle patterns (lower priority)
    else if (prev && isHammer(current, prev)) {
      patterns.push({
        pattern: 'HAMMER',
        signal: 'BUY',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Hammer - Bullish reversal'
      })
    } else if (isInvertedHammer(current)) {
      patterns.push({
        pattern: 'INVERTED_HAMMER',
        signal: 'BUY',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Inverted Hammer - Potential reversal'
      })
    } else if (isDragonflyDoji(current)) {
      patterns.push({
        pattern: 'DRAGONFLY_DOJI',
        signal: 'BUY',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Dragonfly Doji - Bullish signal'
      })
    } else if (isShootingStar(current)) {
      patterns.push({
        pattern: 'SHOOTING_STAR',
        signal: 'SELL',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Shooting Star - Bearish reversal'
      })
    } else if (isHangingMan(current)) {
      patterns.push({
        pattern: 'HANGING_MAN',
        signal: 'SELL',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Hanging Man - Bearish signal'
      })
    } else if (isGravestoneDoji(current)) {
      patterns.push({
        pattern: 'GRAVESTONE_DOJI',
        signal: 'SELL',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: 'Gravestone Doji - Bearish signal'
      })
    }
    // Neutral patterns (informational, trend depends on context)
    else if (isMarubozu(current)) {
      patterns.push({
        pattern: 'MARUBOZU',
        signal: isBullish(current) ? 'BUY' : 'SELL',
        confidence: 'MEDIUM',
        candleIndex: i,
        description: `${isBullish(current) ? 'Bullish' : 'Bearish'} Marubozu - Strong momentum`
      })
    } else if (isDoji(current)) {
      patterns.push({
        pattern: 'DOJI',
        signal: prev && isBullish(prev) ? 'SELL' : 'BUY',
        confidence: 'LOW',
        candleIndex: i,
        description: 'Doji - Indecision, potential reversal'
      })
    } else if (isSpinningTop(current)) {
      patterns.push({
        pattern: 'SPINNING_TOP',
        signal: prev && isBullish(prev) ? 'SELL' : 'BUY',
        confidence: 'LOW',
        candleIndex: i,
        description: 'Spinning Top - Market indecision'
      })
    } else if (isStar(current)) {
      patterns.push({
        pattern: 'STAR',
        signal: prev && isBullish(prev) ? 'SELL' : 'BUY',
        confidence: 'LOW',
        candleIndex: i,
        description: 'Star - Small body, potential reversal'
      })
    }
  }
  
  return patterns
}

// Get the most recent pattern signal
export function getLatestSignal(candles: Candle[]): PatternSignal | null {
  const patterns = detectPatterns(candles)
  if (patterns.length === 0) return null
  
  // Return the most recent pattern
  return patterns[patterns.length - 1]
}

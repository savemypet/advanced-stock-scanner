import { useState, useEffect } from 'react';
import { Brain, Loader2, TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import { analyzeCandlesticks, checkOllamaStatus, OllamaAnalysis, OllamaStatus } from '../api/ollamaApi';
import { Stock } from '../types';
import { toast } from 'sonner';

interface OllamaAnalysisComponentProps {
  stock: Stock;
  onClose?: () => void;
}

export default function OllamaAnalysisComponent({ stock, onClose }: OllamaAnalysisComponentProps) {
  const [analysis, setAnalysis] = useState<OllamaAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState<OllamaStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    const status = await checkOllamaStatus();
    setOllamaStatus(status);
    if (status.available) {
      analyzeStock();
    } else {
      setError(status.error || 'Ollama is not available');
    }
  };

  const analyzeStock = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get candles from stock data
      const candles = stock.candles || [];
      if (candles.length === 0) {
        setError('No candle data available for analysis');
        setLoading(false);
        return;
      }

      // Get detected patterns from stock if available
      const detectedPatterns = stock.detectedPattern ? [{
        pattern: stock.detectedPattern.name,
        signal: stock.detectedPattern.signal,
        confidence: stock.detectedPattern.confidence,
        description: stock.detectedPattern.description
      }] : null;

      const result = await analyzeCandlesticks(
        stock.symbol,
        candles,
        stock.currentPrice,
        stock.volume,
        stock.avgVolume,
        detectedPatterns
      );

      if (result.success && result.analysis) {
        setAnalysis(result.analysis);
        toast.success(`AI Analysis: ${result.analysis.signal} signal (${result.analysis.confidence} confidence)`);
      } else {
        setError(result.error || 'Analysis failed');
        toast.error('AI analysis failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to analyze stock');
      toast.error('AI analysis error');
    } finally {
      setLoading(false);
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'SELL':
        return <TrendingDown className="w-5 h-5 text-red-500" />;
      default:
        return <Minus className="w-5 h-5 text-gray-500" />;
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'HIGH':
        return 'text-green-500 bg-green-500/10 border-green-500/20';
      case 'MEDIUM':
        return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'LOW':
        return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
      default:
        return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
    }
  };

  const getConfidenceIcon = (confidence: string) => {
    switch (confidence) {
      case 'HIGH':
        return <CheckCircle2 className="w-4 h-4" />;
      case 'MEDIUM':
        return <AlertCircle className="w-4 h-4" />;
      case 'LOW':
        return <XCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  if (!ollamaStatus) {
    return (
      <div className="p-4 bg-card border border-border rounded-lg">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Checking Ollama connection...</span>
        </div>
      </div>
    );
  }

  if (!ollamaStatus.available) {
    return (
      <div className="p-4 bg-card border border-border rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-foreground mb-1">Ollama Not Available</h3>
            <p className="text-sm text-muted-foreground mb-3">
              {ollamaStatus.error || 'Ollama is not running or not accessible'}
            </p>
            <button
              onClick={checkStatus}
              className="px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Retry Connection
            </button>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <XCircle className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 bg-card border border-border rounded-lg space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-500" />
          <h3 className="font-semibold text-foreground">AI Analysis: {stock.symbol}</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={analyzeStock}
            disabled={loading}
            className="px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Brain className="w-4 h-4" />
                <span>Analyze</span>
              </>
            )}
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <XCircle className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-md">
          <p className="text-sm text-red-500">{error}</p>
        </div>
      )}

      {loading && !analysis && (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">AI is analyzing candlestick patterns...</p>
            <p className="text-xs text-muted-foreground mt-1">This may take 10-30 seconds</p>
          </div>
        </div>
      )}

      {analysis && (
        <div className="space-y-4">
          {/* Signal Card */}
          <div className="p-4 bg-background border border-border rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                {getSignalIcon(analysis.signal)}
                <div>
                  <h4 className="font-semibold text-foreground">Signal: {analysis.signal}</h4>
                  <p className="text-xs text-muted-foreground">
                    {analysis.pattern || 'No specific pattern detected'}
                  </p>
                </div>
              </div>
              <div className={`px-3 py-1.5 rounded-md border flex items-center gap-2 ${getConfidenceColor(analysis.confidence)}`}>
                {getConfidenceIcon(analysis.confidence)}
                <span className="text-sm font-medium">{analysis.confidence} Confidence</span>
              </div>
            </div>

            {/* Reasoning */}
            <div className="mt-3 pt-3 border-t border-border">
              <p className="text-sm text-muted-foreground mb-2">AI Reasoning:</p>
              <p className="text-sm text-foreground leading-relaxed">{analysis.reasoning}</p>
            </div>
          </div>

          {/* Trading Recommendations */}
          {(analysis.entryPrice || analysis.stopLoss || analysis.takeProfit) && (
            <div className="p-4 bg-background border border-border rounded-lg">
              <h4 className="font-semibold text-foreground mb-3">Trading Recommendations</h4>
              <div className="grid grid-cols-3 gap-3 mb-3">
                {analysis.entryPrice && (
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Entry Price</p>
                    <p className="text-sm font-semibold text-foreground">${analysis.entryPrice.toFixed(2)}</p>
                  </div>
                )}
                {analysis.stopLoss && (
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Stop Loss</p>
                    <p className="text-sm font-semibold text-red-500">${analysis.stopLoss.toFixed(2)}</p>
                  </div>
                )}
                {analysis.takeProfit && (
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Take Profit</p>
                    <p className="text-sm font-semibold text-green-500">${analysis.takeProfit.toFixed(2)}</p>
                  </div>
                )}
              </div>
              {analysis.riskRewardRatio && (
                <div className="pt-3 border-t border-border">
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-muted-foreground">Risk-Reward Ratio</p>
                    <p className={`text-sm font-semibold ${analysis.riskRewardRatio >= 2 ? 'text-green-500' : analysis.riskRewardRatio >= 1.5 ? 'text-yellow-500' : 'text-red-500'}`}>
                      {analysis.riskRewardRatio.toFixed(2)}:1
                    </p>
                  </div>
                  {analysis.riskRewardRatio < 1.5 && (
                    <p className="text-xs text-yellow-500 mt-1">⚠️ Low risk-reward ratio - consider waiting for better setup</p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Metadata */}
          <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t border-border">
            <span>Analyzed {analysis.candleCount || 0} candles</span>
            {analysis.volumeRatio && (
              <span>Volume: {analysis.volumeRatio.toFixed(2)}x average</span>
            )}
            {analysis.timestamp && (
              <span>{new Date(analysis.timestamp).toLocaleTimeString()}</span>
            )}
          </div>
        </div>
      )}

      {!loading && !analysis && !error && (
        <div className="text-center py-4">
          <p className="text-sm text-muted-foreground">Click "Analyze" to get AI candlestick analysis</p>
        </div>
      )}
    </div>
  );
}

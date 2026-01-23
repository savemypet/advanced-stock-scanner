import { useState } from 'react';
import { Brain, Loader2, CheckCircle2, XCircle, BookOpen } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function OllamaTeaching() {
  const [teaching, setTeaching] = useState(false);
  const [taught, setTaught] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const teachAllPatterns = async () => {
    setTeaching(true);
    setError(null);
    setTaught(false);

    try {
      const response = await fetch(`${API_BASE_URL}/api/ollama/teach-all`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (result.success) {
        setTaught(true);
        toast.success('✅ All candlestick patterns taught to Ollama!', {
          description: `${result.patterns_taught || 36} patterns learned`,
          duration: 5000,
        });
      } else {
        setError(result.error || 'Teaching failed');
        toast.error('Failed to teach patterns', {
          description: result.error,
        });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to teach patterns');
      toast.error('Teaching error', {
        description: err.message,
      });
    } finally {
      setTeaching(false);
    }
  };

  return (
    <div className="p-4 bg-card border border-border rounded-lg">
      <div className="flex items-start gap-3">
        <BookOpen className="w-5 h-5 text-purple-500 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-foreground mb-1">Teach Ollama All Patterns</h3>
          <p className="text-sm text-muted-foreground mb-3">
            Teach Ollama all 36+ candlestick patterns from your codebase. This will improve AI analysis accuracy.
          </p>
          
          {error && (
            <div className="p-2 bg-red-500/10 border border-red-500/20 rounded-md mb-3">
              <p className="text-xs text-red-500">{error}</p>
            </div>
          )}

          {taught && (
            <div className="p-2 bg-green-500/10 border border-green-500/20 rounded-md mb-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <p className="text-xs text-green-500">All patterns taught successfully!</p>
              </div>
            </div>
          )}

          <button
            onClick={teachAllPatterns}
            disabled={teaching || taught}
            className="px-4 py-2 text-sm bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {teaching ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Teaching Patterns...</span>
              </>
            ) : taught ? (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>Patterns Taught</span>
              </>
            ) : (
              <>
                <Brain className="w-4 h-4" />
                <span>Teach All Patterns</span>
              </>
            )}
          </button>

          <p className="text-xs text-muted-foreground mt-2">
            This will teach Ollama: Single patterns (8), Double patterns (10), Triple patterns (14), Four-candle patterns (2), and Neutral patterns (4)
          </p>
        </div>
      </div>
    </div>
  );
}

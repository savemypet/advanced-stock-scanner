import { useState, useEffect, useRef } from 'react'
import { Activity, ChevronDown, ChevronUp, Wifi, WifiOff, AlertCircle, CheckCircle, X } from 'lucide-react'

interface LogEntry {
  id: string
  timestamp: Date
  type: 'info' | 'success' | 'error' | 'warning'
  message: string
  details?: string
}

interface ConnectionLogProps {
  isOpen: boolean
  onToggle: () => void
}

export default function ConnectionLog({ isOpen, onToggle }: ConnectionLogProps) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking')
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const logEndRef = useRef<HTMLDivElement>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (logEndRef.current && isOpen) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, isOpen])

  // Poll for connection status and logs
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/health')
        const data = await response.json()
        setConnectionStatus(data.ibkrConnected ? 'connected' : 'disconnected')
        setLastUpdate(new Date())
        
        // Add status log
        addLog(
          data.ibkrConnected ? 'success' : 'error',
          `IBKR ${data.ibkrConnected ? 'Connected' : 'Disconnected'}`,
          data.ibkrConnected 
            ? `Port: ${data.ibkrPort || 'N/A'}, Host: ${data.ibkrHost || 'N/A'}`
            : 'Check TWS/IB Gateway is running'
        )
      } catch (error) {
        setConnectionStatus('disconnected')
        addLog('error', 'Backend not responding', 'Cannot reach backend API')
      }
    }

    // Initial fetch
    fetchStatus()

    // Poll every 5 seconds
    intervalRef.current = setInterval(fetchStatus, 5000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  // Listen to console logs from the app
  useEffect(() => {
    const originalLog = console.log
    const originalError = console.error
    const originalWarn = console.warn

    console.log = (...args: any[]) => {
      originalLog(...args)
      const message = args.join(' ')
      if (message.includes('[SCANNER]') || message.includes('[SEARCH]') || message.includes('[IBKR]') || message.includes('[API]')) {
        addLog('info', message)
      }
    }

    console.error = (...args: any[]) => {
      originalError(...args)
      const message = args.join(' ')
      if (message.includes('[SCANNER]') || message.includes('[SEARCH]') || message.includes('[IBKR]') || message.includes('[API]')) {
        addLog('error', message)
      }
    }

    console.warn = (...args: any[]) => {
      originalWarn(...args)
      const message = args.join(' ')
      if (message.includes('[SCANNER]') || message.includes('[SEARCH]') || message.includes('[IBKR]') || message.includes('[API]')) {
        addLog('warning', message)
      }
    }

    return () => {
      console.log = originalLog
      console.error = originalError
      console.warn = originalWarn
    }
  }, [])

  const addLog = (type: LogEntry['type'], message: string, details?: string) => {
    const newLog: LogEntry = {
      id: `${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
      type,
      message: message.substring(0, 200), // Limit message length
      details
    }
    setLogs(prev => {
      const updated = [...prev, newLog]
      // Keep only last 100 logs
      return updated.slice(-100)
    })
  }

  const clearLogs = () => {
    setLogs([])
  }

  const getLogIcon = (type: LogEntry['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />
      default:
        return <Activity className="w-4 h-4 text-blue-500" />
    }
  }

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'success':
        return 'text-green-400'
      case 'error':
        return 'text-red-400'
      case 'warning':
        return 'text-yellow-400'
      default:
        return 'text-gray-300'
    }
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-background border-t border-border shadow-lg">
      {/* Header */}
      <div 
        className="flex items-center justify-between px-4 py-2 bg-muted/50 cursor-pointer hover:bg-muted/80 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {connectionStatus === 'connected' ? (
              <Wifi className="w-5 h-5 text-green-500" />
            ) : connectionStatus === 'checking' ? (
              <Activity className="w-5 h-5 text-yellow-500 animate-pulse" />
            ) : (
              <WifiOff className="w-5 h-5 text-red-500" />
            )}
            <span className="font-semibold text-sm">
              IBKR Connection Log
              {connectionStatus === 'connected' && (
                <span className="ml-2 text-xs text-green-500">● Connected</span>
              )}
              {connectionStatus === 'disconnected' && (
                <span className="ml-2 text-xs text-red-500">● Disconnected</span>
              )}
            </span>
          </div>
          <span className="text-xs text-muted-foreground">
            {logs.length} entries
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isOpen && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                clearLogs()
              }}
              className="text-xs text-muted-foreground hover:text-foreground px-2 py-1 rounded"
              title="Clear logs"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          {isOpen ? (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronUp className="w-4 h-4 text-muted-foreground" />
          )}
        </div>
      </div>

      {/* Log Content */}
      {isOpen && (
        <div className="h-64 overflow-y-auto bg-black/90 text-green-400 font-mono text-xs p-4">
          {logs.length === 0 ? (
            <div className="text-muted-foreground text-center py-8">
              No logs yet. Activity will appear here...
            </div>
          ) : (
            <div className="space-y-1">
              {logs.map((log) => (
                <div key={log.id} className="flex items-start gap-2 hover:bg-white/5 px-2 py-1 rounded">
                  <div className="flex-shrink-0 mt-0.5">
                    {getLogIcon(log.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500">
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                      <span className={`${getLogColor(log.type)} break-words`}>
                        {log.message}
                      </span>
                    </div>
                    {log.details && (
                      <div className="text-gray-500 text-xs ml-6 mt-0.5">
                        {log.details}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={logEndRef} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

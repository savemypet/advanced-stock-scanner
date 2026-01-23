import { useState, useEffect, useRef } from 'react'
import { Activity, ChevronDown, ChevronUp, Wifi, WifiOff, AlertCircle, CheckCircle, X, Copy, Check } from 'lucide-react'
import { toast } from 'sonner'

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
  const [logsCopied, setLogsCopied] = useState(false)
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
    let lastLogCount = 0
    let statusLogged = false
    
    const fetchStatusAndLogs = async () => {
      try {
        // Fetch health status
        const healthResponse = await fetch('/api/health')
        const healthData = await healthResponse.json()
        setConnectionStatus(healthData.ibkrConnected ? 'connected' : 'disconnected')
        setLastUpdate(new Date())
        
        // Add detailed status log with error info (only once per status change)
        if (!statusLogged) {
          if (healthData.ibkrConnected) {
            addLog(
              'success',
              `IBKR Connected`,
              `Host: ${healthData.ibkrHost || 'N/A'}, Port: ${healthData.ibkrPort || 'N/A'}, Username: ${healthData.ibkrUsername || 'N/A'}`
            )
          } else {
            addLog(
              'error',
              `IBKR Disconnected`,
              healthData.connectionError || `Host: ${healthData.ibkrHost || 'N/A'}, Port: ${healthData.ibkrPort || 'N/A'}. Check TWS/IB Gateway is running and API is enabled.`
            )
          }
          statusLogged = true
        }
        
        // Fetch detailed logs from backend
        try {
          const logsResponse = await fetch('/api/logs')
          const logsData = await logsResponse.json()
          
          if (logsData.success && logsData.logs) {
            // Only add new logs (compare count)
            if (logsData.count > lastLogCount) {
              const newLogs = logsData.logs.slice(lastLogCount)
              newLogs.forEach((log: any) => {
                const level = log.level?.toLowerCase() || 'info'
                let logType: LogEntry['type'] = 'info'
                if (level === 'error' || level === 'critical') {
                  logType = 'error'
                } else if (level === 'warning') {
                  logType = 'warning'
                } else if (level === 'info' && log.message?.includes('✅')) {
                  logType = 'success'
                }
                
                addLog(
                  logType,
                  log.message || 'No message',
                  log.module ? `Module: ${log.module}, Function: ${log.funcName}, Line: ${log.lineno}` : undefined
                )
              })
              lastLogCount = logsData.count
            }
          }
        } catch (logError) {
          // Silently fail - logs endpoint might not be available
        }
      } catch (error) {
        setConnectionStatus('disconnected')
        if (!statusLogged) {
          addLog('error', 'Backend not responding', `Cannot reach backend API: ${error instanceof Error ? error.message : 'Unknown error'}`)
          statusLogged = true
        }
      }
    }

    // Initial fetch
    fetchStatusAndLogs()

    // Poll every 3 seconds for more responsive updates
    intervalRef.current = setInterval(fetchStatusAndLogs, 3000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isOpen]) // Re-run when panel opens/closes

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
    // Avoid duplicate logs (same message within 1 second)
    const now = Date.now()
    setLogs(prev => {
      const recent = prev.filter(log => 
        log.message === message && 
        now - log.timestamp.getTime() < 1000
      )
      if (recent.length > 0) {
        return prev // Skip duplicate
      }
      
      const newLog: LogEntry = {
        id: `${now}-${Math.random()}`,
        timestamp: new Date(),
        type,
        message: message.substring(0, 500), // Increased limit for detailed errors
        details: details ? details.substring(0, 300) : undefined
      }
      const updated = [...prev, newLog]
      // Keep only last 200 logs for more history
      return updated.slice(-200)
    })
  }

  const clearLogs = () => {
    setLogs([])
  }

  const copyLogs = async () => {
    if (logs.length === 0) {
      toast.error('No logs to copy')
      return
    }

    try {
      // Fetch health status for additional context
      let healthInfo = ''
      try {
        const healthResponse = await fetch('/api/health')
        const healthData = await healthResponse.json()
        healthInfo = `\n\n=== BACKEND HEALTH ===\n`
        healthInfo += `Status: ${healthData.status}\n`
        healthInfo += `IBKR Available: ${healthData.ibkrAvailable}\n`
        healthInfo += `IBKR Connected: ${healthData.ibkrConnected}\n`
        healthInfo += `IBKR Host: ${healthData.ibkrHost}\n`
        healthInfo += `IBKR Port: ${healthData.ibkrPort}\n`
        healthInfo += `IBKR Username: ${healthData.ibkrUsername}\n`
        if (healthData.connectionError) {
          healthInfo += `Connection Error: ${healthData.connectionError}\n`
        }
        healthInfo += `Timestamp: ${healthData.timestamp}\n`
      } catch (e) {
        healthInfo = `\n\n=== BACKEND HEALTH ===\nError fetching health status\n`
      }

      // Format logs
      const logText = `========================================\n`
        + `IBKR CONNECTION LOGS\n`
        + `Generated: ${new Date().toLocaleString()}\n`
        + `========================================\n`
        + healthInfo
        + `\n=== LOG ENTRIES (${logs.length}) ===\n\n`
        + logs.map(log => {
          const timestamp = log.timestamp.toLocaleString()
          const type = log.type.toUpperCase()
          let logLine = `[${timestamp}] [${type}] ${log.message}`
          if (log.details) {
            logLine += `\n  Details: ${log.details}`
          }
          return logLine
        }).join('\n\n')
        + `\n\n========================================\n`
        + `END OF LOGS\n`
        + `========================================\n`

      await navigator.clipboard.writeText(logText)
      setLogsCopied(true)
      toast.success('Logs copied to clipboard!')
      setTimeout(() => setLogsCopied(false), 3000)
    } catch (error) {
      console.error('Failed to copy logs:', error)
      toast.error('Failed to copy logs')
    }
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
            <>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  copyLogs()
                }}
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground px-2 py-1 rounded transition-colors"
                title="Copy logs to clipboard"
              >
                {logsCopied ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
                <span className="hidden sm:inline">{logsCopied ? 'Copied!' : 'Copy'}</span>
              </button>
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
            </>
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
        <div className="h-80 overflow-y-auto bg-black/95 text-green-400 font-mono text-xs p-4">
          {logs.length === 0 ? (
            <div className="text-muted-foreground text-center py-8">
              No logs yet. Activity will appear here...
            </div>
          ) : (
            <div className="space-y-1">
              {logs.map((log) => (
                <div key={log.id} className="flex items-start gap-2 hover:bg-white/10 px-2 py-1 rounded border-l-2 border-transparent hover:border-white/20 transition-colors">
                  <div className="flex-shrink-0 mt-0.5">
                    {getLogIcon(log.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-2 flex-wrap">
                      <span className="text-gray-500 flex-shrink-0">
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                      <span className={`${getLogColor(log.type)} break-words flex-1`}>
                        {log.message}
                      </span>
                    </div>
                    {log.details && (
                      <div className="text-gray-400 text-xs ml-6 mt-1 italic border-l-2 border-gray-700 pl-2">
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

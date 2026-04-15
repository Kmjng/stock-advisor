import { createContext, useContext, useState, useRef, useCallback, useEffect } from 'react'

const AdvisorContext = createContext(null)

export function AdvisorProvider({ children }) {
  const [result, setResult] = useState(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)
  const [savedAt, setSavedAt] = useState(null)
  const [completedNodes, setCompletedNodes] = useState([])
  const [nodeMeta, setNodeMeta] = useState({})
  const abortRef = useRef(null)

  // Load saved result on mount
  useEffect(() => {
    fetch('/api/advisor/saved')
      .then(r => r.json())
      .then(data => {
        if (data.status === 'ok' && data.result) {
          setResult(data.result)
          setSavedAt(data.saved_at)
        }
      })
      .catch(() => {})
  }, [])

  const runAnalysis = useCallback(async (market) => {
    if (abortRef.current) abortRef.current.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setRunning(true)
    setCompletedNodes([])
    setResult(null)
    setError(null)
    setNodeMeta({})

    try {
      const resp = await fetch('/api/advisor/run/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ market: market || null }),
        signal: controller.signal,
      })

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            if (data.status === 'done') {
              setResult(data.advisor_result)
              setSavedAt(new Date().toISOString())
            } else if (data.status === 'completed') {
              setCompletedNodes(prev => [...prev, data.node])
              setNodeMeta(prev => ({ ...prev, [data.node]: data }))
            }
          } catch {}
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        setError(`분석 중 오류가 발생했습니다: ${e.message}`)
      }
    } finally {
      if (!controller.signal.aborted) {
        setRunning(false)
      }
    }
  }, [])

  return (
    <AdvisorContext.Provider value={{
      result, running, error, savedAt,
      completedNodes, nodeMeta, runAnalysis,
    }}>
      {children}
    </AdvisorContext.Provider>
  )
}

export function useAdvisor() {
  return useContext(AdvisorContext)
}

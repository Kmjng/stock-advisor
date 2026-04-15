import { createContext, useContext, useState, useRef, useCallback, useEffect } from 'react'

const AnalysisContext = createContext(null)

export function AnalysisProvider({ children }) {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [savedAt, setSavedAt] = useState(null)
  const abortRef = useRef(null)

  // Load saved results on mount
  useEffect(() => {
    fetch('/api/analysis/saved')
      .then(r => r.json())
      .then(data => {
        if (data.status === 'ok' && data.results?.length > 0) {
          setResults(data.results)
          setSavedAt(data.saved_at)
        }
      })
      .catch(() => {})
  }, [])

  const runAnalysis = useCallback(async (market) => {
    if (abortRef.current) abortRef.current.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setLoading(true)
    setError(null)

    try {
      const param = market ? `?market=${market}` : ''
      const res = await fetch(`/api/analysis/${param}`, { signal: controller.signal })
      if (!res.ok) throw new Error('분석 요청 실패')
      const data = await res.json()
      setResults(data)
      setSavedAt(new Date().toISOString())
    } catch (e) {
      if (e.name !== 'AbortError') {
        setError(e.message)
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false)
      }
    }
  }, [])

  return (
    <AnalysisContext.Provider value={{ results, loading, error, savedAt, runAnalysis }}>
      {children}
    </AnalysisContext.Provider>
  )
}

export function useAnalysis() {
  return useContext(AnalysisContext)
}

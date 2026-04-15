import { useState } from 'react'
import StockCard from '../components/StockCard'
import MarketFilter from '../components/MarketFilter'
import { useAnalysis } from '../contexts/AnalysisContext'

export default function Dashboard() {
  const { results, loading, error, savedAt, runAnalysis } = useAnalysis()
  const [market, setMarket] = useState('')

  const handleMarketChange = (m) => {
    setMarket(m)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800">AI 주식 분석 대시보드</h1>
        <div className="flex items-center gap-3">
          <MarketFilter value={market} onChange={handleMarketChange} />
          <button
            onClick={() => runAnalysis(market)}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? '분석 중...' : 'AI 뉴스분석 시작'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 mb-4 text-sm">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-20">
          <div className="inline-block w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="mt-3 text-slate-500">AI가 뉴스를 분석하고 있습니다...</p>
          <p className="mt-1 text-xs text-slate-400">다른 탭으로 이동해도 분석이 계속 진행됩니다</p>
        </div>
      )}

      {!loading && results.length === 0 && !error && (
        <div className="text-center py-20 text-slate-400">
          <div className="text-4xl mb-3">📊</div>
          <p className="text-sm">AI 뉴스분석 시작 버튼을 눌러 분석을 시작하세요</p>
          <p className="text-xs mt-1">보유종목의 최근 뉴스를 수집하고 AI가 매수/매도/관망 추천을 제공합니다</p>
        </div>
      )}

      {!loading && results.length > 0 && savedAt && (
        <div className="text-xs text-slate-400 mb-3">
          마지막 분석: {new Date(savedAt).toLocaleString('ko-KR')}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {results.map((r) => (
          <StockCard key={r.stock_code} data={r} />
        ))}
      </div>
    </div>
  )
}

import { useState } from 'react'
import MarketFilter from '../components/MarketFilter'
import { useAdvisor } from '../contexts/AdvisorContext'

const STEPS = [
  { node: 'gather_portfolio', label: '포트폴리오 데이터 수집', icon: '📊' },
  { node: 'search_market_news', label: '시장 뉴스 검색', icon: '🔍' },
  { node: 'search_trade_news', label: '매매시점 뉴스 검색', icon: '📰' },
  { node: 'analyze_trades', label: 'AI 매매 분석', icon: '🤖' },
]

const TIMING_COLORS = {
  good: 'text-red-600 bg-red-50',
  neutral: 'text-slate-600 bg-slate-100',
  poor: 'text-blue-600 bg-blue-50',
}
const TIMING_LABELS = { good: '적절', neutral: '보통', poor: '부적절' }

export default function TradeAnalysis() {
  const [market, setMarket] = useState('')
  const { running, completedNodes, result, error, nodeMeta, savedAt, runAnalysis } = useAdvisor()

  const currentStep = running
    ? STEPS.findIndex(s => !completedNodes.includes(s.node))
    : -1

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800">AI 매매분석</h1>
        <div className="flex items-center gap-3">
          <MarketFilter value={market} onChange={setMarket} />
          <button
            onClick={() => runAnalysis(market)}
            disabled={running}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              running
                ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            }`}
          >
            {running ? '분석 중...' : '분석 실행'}
          </button>
        </div>
      </div>

      {/* Progress Steps */}
      {(running || completedNodes.length > 0) && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">진행 상황</h2>
          <div className="grid grid-cols-4 gap-3">
            {STEPS.map((step, i) => {
              const isDone = completedNodes.includes(step.node)
              const isCurrent = currentStep === i
              const meta = nodeMeta[step.node]
              return (
                <div
                  key={step.node}
                  className={`rounded-lg border p-3 text-center transition-all ${
                    isDone
                      ? 'border-emerald-200 bg-emerald-50'
                      : isCurrent
                        ? 'border-indigo-300 bg-indigo-50 animate-pulse'
                        : 'border-slate-200 bg-slate-50'
                  }`}
                >
                  <div className="text-2xl mb-1">{step.icon}</div>
                  <div className={`text-xs font-medium ${isDone ? 'text-emerald-700' : isCurrent ? 'text-indigo-700' : 'text-slate-400'}`}>
                    {step.label}
                  </div>
                  {isDone && (
                    <div className="text-[10px] text-emerald-600 mt-1">
                      {meta?.holdings_count != null && `${meta.holdings_count}종목`}
                      {meta?.transactions_count != null && ` / ${meta.transactions_count}건`}
                      {meta?.news_count != null && `${meta.news_count}건`}
                      {!meta?.holdings_count && !meta?.news_count && '완료'}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-6 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Last analysis timestamp */}
      {!running && result && savedAt && (
        <div className="text-xs text-slate-400 mb-3">
          마지막 분석: {new Date(savedAt).toLocaleString('ko-KR')}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Overall Assessment */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <h2 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500" />
              종합 평가
            </h2>
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
              {result.overall_assessment}
            </p>
          </div>

          {/* Per-stock Analysis */}
          {result.stock_analyses?.length > 0 && (
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                종목별 분석
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.stock_analyses.map((sa, i) => (
                  <div key={i} className="border border-slate-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-slate-800 text-sm">
                        {sa.stock_name} <span className="text-slate-400 font-mono text-xs">{sa.stock_code}</span>
                      </span>
                      {sa.timing_score && (
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TIMING_COLORS[sa.timing_score] || TIMING_COLORS.neutral}`}>
                          {TIMING_LABELS[sa.timing_score] || sa.timing_score}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 mb-2">{sa.assessment}</p>
                    {sa.suggestion && (
                      <p className="text-xs text-indigo-600 bg-indigo-50 rounded px-2 py-1">
                        💡 {sa.suggestion}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations & Warnings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.recommendations?.length > 0 && (
              <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
                <h2 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  추천 전략
                </h2>
                <ul className="space-y-2">
                  {result.recommendations.map((r, i) => (
                    <li key={i} className="text-sm text-slate-600 flex gap-2">
                      <span className="text-emerald-500 shrink-0">→</span>
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {result.risk_warnings?.length > 0 && (
              <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
                <h2 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-red-500" />
                  리스크 경고
                </h2>
                <ul className="space-y-2">
                  {result.risk_warnings.map((w, i) => (
                    <li key={i} className="text-sm text-slate-600 flex gap-2">
                      <span className="text-red-500 shrink-0">⚠</span>
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!running && !result && !error && (
        <div className="text-center py-20 text-slate-400">
          <div className="text-4xl mb-3">🤖</div>
          <p className="text-sm">분석 실행 버튼을 눌러 AI 매매 분석을 시작하세요</p>
          <p className="text-xs mt-1">보유종목, 거래내역, 시장 뉴스를 종합하여 매매 판단을 분석합니다</p>
        </div>
      )}
    </div>
  )
}

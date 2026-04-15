import { useState } from 'react'

const today = () => new Date().toISOString().slice(0, 10)
const daysAgo = (n) => {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d.toISOString().slice(0, 10)
}

export default function NHSyncModal({ onClose }) {
  const [syncHoldings, setSyncHoldings] = useState(true)
  const [syncTx, setSyncTx] = useState(true)
  const [startDate, setStartDate] = useState(daysAgo(7))
  const [endDate, setEndDate] = useState(today())
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleSync = async () => {
    setLoading(true)
    setResult(null)
    try {
      const body = {
        sync_holdings: syncHoldings,
        sync_transactions: syncTx,
        start_date: syncTx ? startDate.replace(/-/g, '') : null,
        end_date: syncTx ? endDate.replace(/-/g, '') : null,
      }
      const resp = await fetch('/api/nh/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await resp.json()
      setResult(data)
    } catch (e) {
      setResult({ success: false, message: `요청 실패: ${e.message}` })
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    if (!loading) onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={handleClose}>
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
          <h2 className="font-semibold text-slate-800">나무증권 전체 동기화</h2>
          <button onClick={handleClose} className="text-slate-400 hover:text-slate-600 text-xl leading-none">&times;</button>
        </div>

        <div className="px-5 py-4 space-y-4">
          <p className="text-sm text-slate-600">모든 계좌(CMA, IRP, ISA중개형, 금현물)를 한번에 동기화합니다.</p>

          {/* 동기화 항목 선택 */}
          <div>
            <p className="text-xs font-medium text-slate-500 mb-2">동기화 항목</p>
            <div className="flex gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={syncHoldings}
                  onChange={e => setSyncHoldings(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-slate-700">보유종목</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={syncTx}
                  onChange={e => setSyncTx(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-slate-700">거래내역</span>
              </label>
            </div>
          </div>

          {/* 거래내역 기간 */}
          {syncTx && (
            <div>
              <p className="text-xs font-medium text-slate-500 mb-2">거래내역 조회 기간</p>
              <div className="flex items-center gap-2">
                <input
                  type="date"
                  value={startDate}
                  onChange={e => setStartDate(e.target.value)}
                  className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                />
                <span className="text-slate-400 text-sm">~</span>
                <input
                  type="date"
                  value={endDate}
                  onChange={e => setEndDate(e.target.value)}
                  className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                />
                <div className="flex gap-1 ml-auto">
                  {[['오늘', 0], ['1주', 7], ['1달', 30]].map(([label, days]) => (
                    <button key={label} type="button"
                      onClick={() => { setStartDate(daysAgo(days)); setEndDate(today()) }}
                      className="px-2 py-1 text-xs bg-slate-100 text-slate-600 rounded hover:bg-slate-200 transition-colors">
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 결과 */}
          {result && (
            <div className={`rounded-lg p-3 text-sm ${result.success ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200'}`}>
              <p className={`font-medium mb-1 ${result.success ? 'text-emerald-700' : 'text-red-700'}`}>
                {result.success ? '동기화 완료' : '동기화 실패'}
              </p>
              {result.message && <p className="text-slate-600">{result.message}</p>}
              {result.output && (
                <pre className="mt-2 text-xs bg-white/60 rounded p-2 overflow-auto max-h-48 whitespace-pre-wrap text-slate-600">
                  {result.output}
                </pre>
              )}
            </div>
          )}
        </div>

        <div className="px-5 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button onClick={handleClose} disabled={loading}
            className="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50">
            닫기
          </button>
          <button
            onClick={handleSync}
            disabled={loading || (!syncHoldings && !syncTx)}
            className="px-4 py-2 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading && (
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
            )}
            {loading ? '전체 동기화 중...' : '전체 동기화'}
          </button>
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'

const ACCOUNT_ALIASES = {
  '20501321618': 'CMA',
  '20503321618': '금현물',
  '20802652222': 'ISA중개형',
  '20502321618': 'IRP',
}

export default function Accounts() {
  const [data, setData] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/portfolio/by-account')
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const accounts = Object.entries(data)

  const formatPrice = (s) => s.currency === 'USD'
    ? `$${s.avg_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : `${s.avg_price?.toLocaleString()}원`

  const formatTotal = (s) => {
    const total = s.quantity * s.avg_price
    return s.currency === 'USD'
      ? `$${total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
      : `${total.toLocaleString()}원`
  }

  const formatCurrency = (val, currency) => {
    if (val == null) return '-'
    return currency === 'USD'
      ? `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
      : `${val.toLocaleString()}원`
  }

  const accountTotal = (stocks) => {
    const krw = stocks.filter(s => s.currency !== 'USD').reduce((sum, s) => sum + s.quantity * s.avg_price, 0)
    const usd = stocks.filter(s => s.currency === 'USD').reduce((sum, s) => sum + s.quantity * s.avg_price, 0)
    const parts = []
    if (krw > 0) parts.push(`${krw.toLocaleString()}원`)
    if (usd > 0) parts.push(`$${usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`)
    return parts.join(' + ') || '0원'
  }

  const accountProfitTotal = (stocks) => {
    const withData = stocks.filter(s => s.profit_loss != null)
    if (withData.length === 0) return null
    const krw = withData.filter(s => s.currency !== 'USD').reduce((sum, s) => sum + (s.profit_loss || 0), 0)
    const usd = withData.filter(s => s.currency === 'USD').reduce((sum, s) => sum + (s.profit_loss || 0), 0)
    return { krw, usd }
  }

  const hasAnyProfitData = (stocks) => stocks.some(s => s.current_price != null)

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-400">
        <svg className="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
        로딩 중...
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-6">계좌별 현황</h1>

      {accounts.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center text-slate-400">
          동기화된 계좌 데이터가 없습니다. 나무증권 동기화를 먼저 실행하세요.
        </div>
      ) : (
        <div className="space-y-6">
          {accounts.map(([accountNo, stocks]) => (
            <div key={accountNo} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-slate-800">
                    {ACCOUNT_ALIASES[accountNo] || accountNo}
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">{accountNo}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500">총 매수금액</p>
                  <p className="font-semibold text-slate-800">{accountTotal(stocks)}</p>
                </div>
              </div>

              {stocks.length === 0 ? (
                <div className="px-5 py-6 text-center text-sm text-slate-400">보유종목 없음</div>
              ) : (
                <>
                  {/* 보유종목 테이블 */}
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200">
                      <tr>
                        <th className="text-left px-4 py-2.5 font-medium text-slate-600">시장</th>
                        <th className="text-left px-4 py-2.5 font-medium text-slate-600">종목코드</th>
                        <th className="text-left px-4 py-2.5 font-medium text-slate-600">종목명</th>
                        <th className="text-right px-4 py-2.5 font-medium text-slate-600">보유수량</th>
                        <th className="text-right px-4 py-2.5 font-medium text-slate-600">평균매수가</th>
                        <th className="text-right px-4 py-2.5 font-medium text-slate-600">매수금액</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stocks.map(s => (
                        <tr key={s.id} className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="px-4 py-2.5">{s.market === 'US' ? '🇺🇸' : '🇰🇷'}</td>
                          <td className="px-4 py-2.5 font-mono text-slate-600">{s.stock_code}</td>
                          <td className="px-4 py-2.5 font-medium text-slate-800">{s.stock_name}</td>
                          <td className="px-4 py-2.5 text-right">
                            {s.quantity % 1 === 0 ? `${s.quantity}주` : `${s.quantity.toFixed(4)}주`}
                          </td>
                          <td className="px-4 py-2.5 text-right">{formatPrice(s)}</td>
                          <td className="px-4 py-2.5 text-right font-medium">{formatTotal(s)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {/* 수익률 테이블 */}
                  {hasAnyProfitData(stocks) && (
                    <div className="border-t border-slate-200">
                      <div className="px-5 py-3 bg-slate-50 flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-slate-700">수익률 현황</h3>
                        {(() => {
                          const totals = accountProfitTotal(stocks)
                          if (!totals) return null
                          const parts = []
                          if (totals.krw !== 0) parts.push(
                            <span key="krw" className={totals.krw >= 0 ? 'text-red-600' : 'text-blue-600'}>
                              {totals.krw >= 0 ? '+' : ''}{totals.krw.toLocaleString()}원
                            </span>
                          )
                          if (totals.usd !== 0) parts.push(
                            <span key="usd" className={totals.usd >= 0 ? 'text-red-600' : 'text-blue-600'}>
                              {totals.usd >= 0 ? '+' : ''}${Math.abs(totals.usd).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                          )
                          return parts.length > 0 && (
                            <span className="text-sm font-semibold">
                              총 평가손익: {parts.reduce((acc, el, i) => i === 0 ? [el] : [...acc, ' + ', el], [])}
                            </span>
                          )
                        })()}
                      </div>
                      <table className="w-full text-sm">
                        <thead className="bg-slate-50 border-b border-slate-200">
                          <tr>
                            <th className="text-left px-4 py-2.5 font-medium text-slate-600">종목명</th>
                            <th className="text-right px-4 py-2.5 font-medium text-slate-600">현재가</th>
                            <th className="text-right px-4 py-2.5 font-medium text-slate-600">평가금액</th>
                            <th className="text-right px-4 py-2.5 font-medium text-slate-600">평가손익</th>
                            <th className="text-right px-4 py-2.5 font-medium text-slate-600">수익률</th>
                          </tr>
                        </thead>
                        <tbody>
                          {stocks.map(s => {
                            const hasData = s.current_price != null
                            const plColor = hasData && s.profit_loss != null
                              ? (s.profit_loss >= 0 ? 'text-red-600' : 'text-blue-600')
                              : 'text-slate-400'
                            const rateColor = hasData && s.return_rate != null
                              ? (s.return_rate >= 0 ? 'text-red-600' : 'text-blue-600')
                              : 'text-slate-400'
                            return (
                              <tr key={s.id} className="border-b border-slate-100 hover:bg-slate-50">
                                <td className="px-4 py-2.5 font-medium text-slate-800">{s.stock_name}</td>
                                <td className="px-4 py-2.5 text-right">
                                  {hasData ? formatCurrency(s.current_price, s.currency) : '-'}
                                </td>
                                <td className="px-4 py-2.5 text-right">
                                  {hasData ? formatCurrency(s.eval_amount, s.currency) : '-'}
                                </td>
                                <td className={`px-4 py-2.5 text-right font-medium ${plColor}`}>
                                  {hasData && s.profit_loss != null
                                    ? `${s.profit_loss >= 0 ? '+' : ''}${formatCurrency(s.profit_loss, s.currency)}`
                                    : '-'}
                                </td>
                                <td className={`px-4 py-2.5 text-right font-bold ${rateColor}`}>
                                  {hasData && s.return_rate != null
                                    ? `${s.return_rate >= 0 ? '+' : ''}${s.return_rate.toFixed(2)}%`
                                    : '-'}
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

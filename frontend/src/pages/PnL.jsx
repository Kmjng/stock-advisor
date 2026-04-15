import { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Cell,
} from 'recharts'
import MarketFilter from '../components/MarketFilter'

const formatCurrency = (val, short) => {
  if (val == null) return '-'
  if (short && Math.abs(val) >= 1000000) return `${(val / 1000000).toFixed(1)}M`
  if (short && Math.abs(val) >= 1000) return `${(val / 1000).toFixed(0)}K`
  return val.toLocaleString()
}

export default function PnL() {
  const [market, setMarket] = useState('')
  const [pnl, setPnl] = useState(null)
  const [byStock, setByStock] = useState([])
  const [selectedStock, setSelectedStock] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchData = () => {
    setLoading(true)
    const param = market ? `?market=${market}` : ''
    Promise.all([
      fetch(`/api/transactions/pnl${param}`).then(r => r.json()),
      fetch(`/api/transactions/by-stock${param}`).then(r => r.json()),
    ]).then(([p, s]) => {
      setPnl(p)
      setByStock(s)
    }).catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(fetchData, [market])

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

  if (!pnl || pnl.total_trades === 0) {
    return (
      <div>
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-slate-800">수익분석</h1>
          <MarketFilter value={market} onChange={setMarket} />
        </div>
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center text-slate-400">
          매도 거래가 없어 분석할 데이터가 없습니다.
        </div>
      </div>
    )
  }

  const profitColor = pnl.total_profit >= 0 ? 'text-red-600' : 'text-blue-600'
  const profitBg = pnl.total_profit >= 0 ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200'

  const stocksWithSells = byStock.filter(s => s.sell_count > 0)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800">수익분석</h1>
        <MarketFilter value={market} onChange={setMarket} />
      </div>

      {/* 요약 카드 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className={`rounded-xl border p-4 ${profitBg}`}>
          <p className="text-xs font-medium text-slate-500 mb-1">총 실현손익</p>
          <p className={`text-xl font-bold ${profitColor}`}>
            {pnl.total_profit >= 0 ? '+' : ''}{formatCurrency(Math.round(pnl.total_profit))}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-medium text-slate-500 mb-1">매도 횟수</p>
          <p className="text-xl font-bold text-slate-800">{pnl.total_trades}회</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-medium text-slate-500 mb-1">승률</p>
          <p className="text-xl font-bold text-slate-800">{pnl.win_rate}%</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-medium text-slate-500 mb-1">수익 / 손실</p>
          <p className="text-xl font-bold">
            <span className="text-red-600">{pnl.win_count}</span>
            <span className="text-slate-400 mx-1">/</span>
            <span className="text-blue-600">{pnl.loss_count}</span>
          </p>
        </div>
      </div>

      {/* 누적 수익 추이 */}
      {pnl.cumulative.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">누적 실현손익 추이</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={pnl.cumulative} margin={{ top: 5, right: 20, bottom: 5, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="date"
                tickFormatter={v => {
                  const d = new Date(v)
                  return `${d.getMonth() + 1}/${d.getDate()}`
                }}
                tick={{ fontSize: 12 }}
                stroke="#94a3b8"
              />
              <YAxis
                tickFormatter={v => formatCurrency(v, true)}
                tick={{ fontSize: 12 }}
                stroke="#94a3b8"
              />
              <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
              <Tooltip
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null
                  const d = payload[0].payload
                  return (
                    <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm">
                      <div className="font-bold text-slate-800">{d.stock_name}</div>
                      <div className={d.profit >= 0 ? 'text-red-600' : 'text-blue-600'}>
                        실현손익: {d.profit >= 0 ? '+' : ''}{Math.round(d.profit).toLocaleString()}
                      </div>
                      <div className="text-slate-600">
                        누적: {d.cumulative >= 0 ? '+' : ''}{Math.round(d.cumulative).toLocaleString()}
                      </div>
                      <div className="text-slate-400 text-xs">{new Date(d.date).toLocaleDateString('ko-KR')}</div>
                    </div>
                  )
                }}
              />
              <Line
                type="monotone"
                dataKey="cumulative"
                stroke="#6366f1"
                strokeWidth={2}
                dot={{ r: 4, fill: '#6366f1' }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* 월별 실현손익 */}
      {pnl.monthly.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6 shadow-sm">
          <h2 className="font-semibold text-slate-700 mb-4">월별 실현손익</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={pnl.monthly} margin={{ top: 5, right: 20, bottom: 5, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="#94a3b8" />
              <YAxis
                tickFormatter={v => formatCurrency(v, true)}
                tick={{ fontSize: 12 }}
                stroke="#94a3b8"
              />
              <ReferenceLine y={0} stroke="#94a3b8" />
              <Tooltip
                formatter={(val) => [`${Math.round(val).toLocaleString()}`, '실현손익']}
                labelFormatter={l => `${l}`}
              />
              <Bar dataKey="profit" radius={[4, 4, 0, 0]}>
                {pnl.monthly.map((entry, i) => (
                  <Cell key={i} fill={entry.profit >= 0 ? '#ef4444' : '#3b82f6'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* 종목별 실현손익 랭킹 */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">종목별 실현손익</h2>
        {stocksWithSells.length === 0 ? (
          <p className="text-slate-400 text-center py-4">매도 거래가 있는 종목이 없습니다</p>
        ) : (
          <>
            <ResponsiveContainer width="100%" height={Math.max(200, stocksWithSells.length * 40)}>
              <BarChart
                data={stocksWithSells}
                layout="vertical"
                margin={{ top: 5, right: 20, bottom: 5, left: 80 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  type="number"
                  tickFormatter={v => formatCurrency(v, true)}
                  tick={{ fontSize: 12 }}
                  stroke="#94a3b8"
                />
                <YAxis
                  type="category"
                  dataKey="stock_name"
                  tick={{ fontSize: 12 }}
                  stroke="#94a3b8"
                  width={70}
                />
                <ReferenceLine x={0} stroke="#94a3b8" />
                <Tooltip
                  formatter={(val) => [`${Math.round(val).toLocaleString()}`, '실현손익']}
                />
                <Bar
                  dataKey="realized_profit"
                  radius={[0, 4, 4, 0]}
                  cursor="pointer"
                  onClick={(data) => setSelectedStock(
                    selectedStock?.stock_code === data.stock_code ? null : data
                  )}
                >
                  {stocksWithSells.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={entry.realized_profit >= 0 ? '#ef4444' : '#3b82f6'}
                      opacity={selectedStock && selectedStock.stock_code !== entry.stock_code ? 0.3 : 1}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            {/* 종목 상세 */}
            {selectedStock && (
              <div className="mt-4 border-t border-slate-200 pt-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-slate-700">
                    {selectedStock.stock_name} ({selectedStock.stock_code}) 매매내역
                  </h3>
                  <button
                    onClick={() => setSelectedStock(null)}
                    className="text-xs text-slate-400 hover:text-slate-600"
                  >
                    닫기
                  </button>
                </div>
                <div className="grid grid-cols-4 gap-3 mb-3">
                  <div className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">총 매수금액</p>
                    <p className="font-semibold text-slate-800">
                      {Math.round(selectedStock.total_buy_amount).toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">총 매도금액</p>
                    <p className="font-semibold text-slate-800">
                      {Math.round(selectedStock.total_sell_amount).toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">실현손익</p>
                    <p className={`font-semibold ${selectedStock.realized_profit >= 0 ? 'text-red-600' : 'text-blue-600'}`}>
                      {selectedStock.realized_profit >= 0 ? '+' : ''}{Math.round(selectedStock.realized_profit).toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">매매횟수</p>
                    <p className="font-semibold text-slate-800">
                      매수 {selectedStock.buy_count} / 매도 {selectedStock.sell_count}
                    </p>
                  </div>
                </div>
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="text-left px-3 py-2 font-medium text-slate-600">거래일</th>
                      <th className="text-center px-3 py-2 font-medium text-slate-600">유형</th>
                      <th className="text-right px-3 py-2 font-medium text-slate-600">수량</th>
                      <th className="text-right px-3 py-2 font-medium text-slate-600">가격</th>
                      <th className="text-right px-3 py-2 font-medium text-slate-600">금액</th>
                      <th className="text-right px-3 py-2 font-medium text-slate-600">실현손익</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedStock.transactions.map(t => (
                      <tr key={t.id} className="border-b border-slate-100 hover:bg-slate-50">
                        <td className="px-3 py-2 text-slate-500 text-xs">
                          {new Date(t.traded_at).toLocaleDateString('ko-KR')}
                        </td>
                        <td className="px-3 py-2 text-center">
                          <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${t.trade_type === 'buy' ? 'bg-green-100 text-green-700' : 'bg-purple-100 text-purple-700'}`}>
                            {t.trade_type === 'buy' ? '매수' : '매도'}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-right">{t.quantity}</td>
                        <td className="px-3 py-2 text-right">{t.price.toLocaleString()}</td>
                        <td className="px-3 py-2 text-right">{Math.round(t.total_amount).toLocaleString()}</td>
                        <td className={`px-3 py-2 text-right font-medium ${
                          t.realized_profit == null ? 'text-slate-400'
                          : t.realized_profit >= 0 ? 'text-red-600' : 'text-blue-600'
                        }`}>
                          {t.realized_profit != null
                            ? `${t.realized_profit >= 0 ? '+' : ''}${Math.round(t.realized_profit).toLocaleString()}`
                            : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

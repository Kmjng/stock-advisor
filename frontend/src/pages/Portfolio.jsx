import { useState, useEffect } from 'react'
import MarketFilter from '../components/MarketFilter'
import StockPriceChart from '../components/StockPriceChart'

export default function Portfolio() {
  const [stocks, setStocks] = useState([])
  const [market, setMarket] = useState('')
  const [form, setForm] = useState({ stock_code: '', stock_name: '', quantity: '', avg_price: '', market: 'US', currency: 'USD' })

  const fetchStocks = (m) => {
    const param = m ? `?market=${m}` : ''
    fetch(`/api/portfolio/${param}`).then(r => r.json()).then(setStocks).catch(() => {})
  }

  useEffect(() => fetchStocks(market), [market])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const body = {
      ...form,
      quantity: parseFloat(form.quantity),
      avg_price: parseFloat(form.avg_price),
    }
    await fetch('/api/portfolio/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    setForm({ stock_code: '', stock_name: '', quantity: '', avg_price: '', market: 'US', currency: 'USD' })
    fetchStocks(market)
  }

  const handleDelete = async (id) => {
    await fetch(`/api/portfolio/${id}`, { method: 'DELETE' })
    fetchStocks(market)
  }

  const handleMarketSelect = (m) => {
    setForm({ ...form, market: m, currency: m === 'US' ? 'USD' : 'KRW' })
  }

  const formatPrice = (s) => s.currency === 'USD'
    ? `$${s.avg_price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
    : `${s.avg_price?.toLocaleString()}원`

  const formatTotal = (s) => s.currency === 'USD'
    ? `$${(s.quantity * s.avg_price)?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
    : `${(s.quantity * s.avg_price)?.toLocaleString()}원`

  const formatQty = (s) => s.quantity % 1 === 0 ? `${s.quantity}주` : `${s.quantity.toFixed(4)}주`

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800">보유종목 관리</h1>
        <MarketFilter value={market} onChange={setMarket} />
      </div>

      {stocks.length > 0 && (
        <div className="mb-6">
          <h2 className="font-semibold text-slate-700 mb-3">보유종목 시세</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {stocks.map(s => (
              <StockPriceChart
                key={s.stock_code}
                stockCode={s.stock_code}
                stockName={s.stock_name}
                market={s.market}
                currency={s.currency}
                avgPrice={s.avg_price}
              />
            ))}
          </div>
        </div>
      )}

      <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 mb-4 text-sm text-amber-800">
        해외주식은 NH API로 불러올 수 없어 직접 입력해야 합니다. 국내주식은 나무증권 동기화를 이용하세요.
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-5 mb-6 shadow-sm">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="hidden">
            <input type="hidden" value="US" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">종목코드</label>
            <input type="text" placeholder="AAPL"
              value={form.stock_code} onChange={e => setForm({ ...form, stock_code: e.target.value })} required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">종목명</label>
            <input type="text" placeholder="Apple"
              value={form.stock_name} onChange={e => setForm({ ...form, stock_name: e.target.value })} required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">보유수량</label>
            <input type="number" placeholder="100" step="any"
              value={form.quantity} onChange={e => setForm({ ...form, quantity: e.target.value })} required min="0"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">평균매수가 (USD)</label>
            <input type="number" placeholder="150.00" step="any"
              value={form.avg_price} onChange={e => setForm({ ...form, avg_price: e.target.value })} required min="0"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
          </div>
        </div>
        <button type="submit"
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
          종목 추가
        </button>
      </form>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">시장</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">종목코드</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">종목명</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">보유수량</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">평균매수가</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">매수금액</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {stocks.length === 0 && (
              <tr><td colSpan={7} className="text-center py-8 text-slate-400">보유종목이 없습니다</td></tr>
            )}
            {stocks.map(s => (
              <tr key={s.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-3">{s.market === 'US' ? '🇺🇸' : '🇰🇷'}</td>
                <td className="px-4 py-3 font-mono text-slate-600">{s.stock_code}</td>
                <td className="px-4 py-3 font-medium text-slate-800">{s.stock_name}</td>
                <td className="px-4 py-3 text-right">{formatQty(s)}</td>
                <td className="px-4 py-3 text-right">{formatPrice(s)}</td>
                <td className="px-4 py-3 text-right font-medium">{formatTotal(s)}</td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => handleDelete(s.id)} className="text-red-500 hover:text-red-700 text-xs font-medium">삭제</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

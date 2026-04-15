import { useState, useEffect } from 'react'
import Timeline from '../components/Timeline'
import MarketFilter from '../components/MarketFilter'

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [stocks, setStocks] = useState([])
  const [filter, setFilter] = useState('')
  const [market, setMarket] = useState('')
  const [form, setForm] = useState({
    stock_code: '', stock_name: '', trade_type: 'buy',
    quantity: '', price: '', traded_at: '', market: 'US', currency: 'USD',
  })

  const fetchTransactions = () => {
    const params = new URLSearchParams()
    if (filter) params.set('stock_code', filter)
    if (market) params.set('market', market)
    const qs = params.toString() ? `?${params}` : ''
    fetch(`/api/transactions/${qs}`).then(r => r.json()).then(setTransactions).catch(() => {})
  }

  useEffect(() => {
    fetch('/api/portfolio/').then(r => r.json()).then(setStocks).catch(() => {})
  }, [])

  useEffect(fetchTransactions, [filter, market])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const body = {
      ...form,
      quantity: parseFloat(form.quantity),
      price: parseFloat(form.price),
      traded_at: new Date(form.traded_at).toISOString(),
    }
    await fetch('/api/transactions/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    setForm({ stock_code: '', stock_name: '', trade_type: 'buy', quantity: '', price: '', traded_at: '', market: 'US', currency: 'USD' })
    fetchTransactions()
    fetch('/api/portfolio/').then(r => r.json()).then(setStocks).catch(() => {})
  }

  const handleDelete = async (id) => {
    await fetch(`/api/transactions/${id}`, { method: 'DELETE' })
    fetchTransactions()
    fetch('/api/portfolio/').then(r => r.json()).then(setStocks).catch(() => {})
  }

  const handleStockSelect = (code) => {
    const stock = stocks.find(s => s.stock_code === code)
    if (stock) {
      setForm({ ...form, stock_code: code, stock_name: stock.stock_name, market: stock.market, currency: stock.currency })
    }
  }

  const handleMarketSelect = (m) => {
    setForm({ ...form, market: m, currency: m === 'US' ? 'USD' : 'KRW' })
  }

  const formatPrice = (t) => t.currency === 'USD'
    ? `$${t.price?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
    : `${t.price?.toLocaleString()}원`

  const formatTotal = (t) => t.currency === 'USD'
    ? `$${t.total_amount?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
    : `${t.total_amount?.toLocaleString()}원`

  const formatQty = (t) => t.quantity % 1 === 0 ? `${t.quantity}주` : `${t.quantity.toFixed(4)}주`

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800">거래내역</h1>
        <MarketFilter value={market} onChange={setMarket} />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-slate-700">거래 타임라인</h2>
          <select value={filter} onChange={e => setFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none">
            <option value="">전체 종목</option>
            {stocks.map(s => (
              <option key={s.stock_code} value={s.stock_code}>
                {s.market === 'US' ? '🇺🇸' : '🇰🇷'} {s.stock_name} ({s.stock_code})
              </option>
            ))}
          </select>
        </div>
        <Timeline transactions={transactions} />
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 mb-4 text-sm text-amber-800">
        해외주식은 NH API로 불러올 수 없어 직접 입력해야 합니다. 국내 거래내역은 나무증권 동기화를 이용하세요.
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-5 mb-6 shadow-sm">
        <h2 className="font-semibold text-slate-700 mb-4">해외주식 거래 추가</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="hidden">
            <input type="hidden" value="US" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">종목코드</label>
            <input type="text" placeholder="IONQ" value={form.stock_code}
              onChange={e => setForm({ ...form, stock_code: e.target.value })} required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">종목명</label>
            <input type="text" placeholder="IonQ Inc" value={form.stock_name}
              onChange={e => setForm({ ...form, stock_name: e.target.value })} required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">거래유형</label>
            <div className="flex gap-2 mt-1">
              <button type="button" onClick={() => setForm({ ...form, trade_type: 'buy' })}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${form.trade_type === 'buy' ? 'bg-green-100 text-green-700 ring-1 ring-green-300' : 'bg-slate-100 text-slate-500'}`}>
                매수
              </button>
              <button type="button" onClick={() => setForm({ ...form, trade_type: 'sell' })}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${form.trade_type === 'sell' ? 'bg-purple-100 text-purple-700 ring-1 ring-purple-300' : 'bg-slate-100 text-slate-500'}`}>
                매도
              </button>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">수량</label>
            <input type="number" placeholder="100" step="any" value={form.quantity}
              onChange={e => setForm({ ...form, quantity: e.target.value })} required min="0"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">가격 (USD)</label>
            <input type="number" placeholder="150.00" step="any" value={form.price}
              onChange={e => setForm({ ...form, price: e.target.value })} required min="0"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">거래일시</label>
            <input type="datetime-local" value={form.traded_at}
              onChange={e => setForm({ ...form, traded_at: e.target.value })} required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>
        <button type="submit"
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
          거래 추가
        </button>
      </form>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">거래일시</th>
              <th className="text-center px-3 py-3 font-medium text-slate-600">시장</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">종목</th>
              <th className="text-center px-4 py-3 font-medium text-slate-600">유형</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">수량</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">가격</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">총금액</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 && (
              <tr><td colSpan={8} className="text-center py-8 text-slate-400">거래내역이 없습니다</td></tr>
            )}
            {transactions.map(t => (
              <tr key={t.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-3 text-slate-500 text-xs">{new Date(t.traded_at).toLocaleString('ko-KR')}</td>
                <td className="px-3 py-3 text-center">{t.market === 'US' ? '🇺🇸' : '🇰🇷'}</td>
                <td className="px-4 py-3">
                  <span className="font-medium text-slate-800">{t.stock_name}</span>
                  <span className="text-slate-400 text-xs ml-1">{t.stock_code}</span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${t.trade_type === 'buy' ? 'bg-green-100 text-green-700' : 'bg-purple-100 text-purple-700'}`}>
                    {t.trade_type === 'buy' ? '매수' : '매도'}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">{formatQty(t)}</td>
                <td className="px-4 py-3 text-right">{formatPrice(t)}</td>
                <td className="px-4 py-3 text-right font-medium">{formatTotal(t)}</td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => handleDelete(t.id)} className="text-red-500 hover:text-red-700 text-xs font-medium">삭제</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

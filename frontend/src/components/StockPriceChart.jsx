import { useState, useEffect } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'

const PERIODS = [
  { key: '1m', label: '1개월' },
  { key: '3m', label: '3개월' },
  { key: '6m', label: '6개월' },
  { key: '1y', label: '1년' },
]

const formatPrice = (val, currency) => {
  if (val == null) return '-'
  if (currency === 'USD') return `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  return `${val.toLocaleString()}원`
}

const formatDateTick = (dateStr) => {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  return `${parseInt(parts[1])}/${parseInt(parts[2])}`
}

const formatVolume = (vol) => {
  if (vol >= 1000000) return `${(vol / 1000000).toFixed(1)}M`
  if (vol >= 1000) return `${(vol / 1000).toFixed(0)}K`
  return vol.toLocaleString()
}

export default function StockPriceChart({ stockCode, stockName, market, currency, avgPrice }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [period, setPeriod] = useState('3m')

  useEffect(() => {
    setLoading(true)
    setError(false)
    fetch(`/api/chart/${stockCode}?period=${period}&market=${market}`)
      .then(r => r.json())
      .then(res => {
        setData(res.prices || [])
        setLoading(false)
      })
      .catch(() => {
        setError(true)
        setLoading(false)
      })
  }, [stockCode, period, market])

  const lastPrice = data.length > 0 ? data[data.length - 1].close : null
  const priceChange = lastPrice && avgPrice > 0 ? lastPrice - avgPrice : null
  const changeRate = priceChange && avgPrice > 0 ? (priceChange / avgPrice * 100) : null
  const isUp = priceChange >= 0

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm">{market === 'US' ? '🇺🇸' : '🇰🇷'}</span>
          <span className="font-semibold text-slate-800 text-sm">{stockName}</span>
          <span className="text-xs text-slate-400 font-mono">{stockCode}</span>
        </div>
        <div className="flex gap-1">
          {PERIODS.map(p => (
            <button
              key={p.key}
              onClick={() => setPeriod(p.key)}
              className={`px-2 py-0.5 text-xs rounded-md transition-colors ${
                period === p.key
                  ? 'bg-slate-800 text-white'
                  : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Price summary */}
      {!loading && !error && lastPrice != null && (
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-lg font-bold text-slate-800">{formatPrice(lastPrice, currency)}</span>
          {changeRate != null && (
            <span className={`text-xs font-medium ${isUp ? 'text-red-500' : 'text-blue-500'}`}>
              {isUp ? '+' : ''}{formatPrice(priceChange, currency)} ({isUp ? '+' : ''}{changeRate.toFixed(2)}%)
            </span>
          )}
        </div>
      )}

      {/* Chart */}
      {loading ? (
        <div className="h-[180px] flex items-center justify-center">
          <svg className="animate-spin h-5 w-5 text-slate-300" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        </div>
      ) : error ? (
        <div className="h-[180px] flex items-center justify-center text-sm text-slate-400">
          차트 데이터를 불러올 수 없습니다
        </div>
      ) : data.length === 0 ? (
        <div className="h-[180px] flex items-center justify-center text-sm text-slate-400">
          데이터가 없습니다
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDateTick}
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={{ stroke: '#e2e8f0' }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tickFormatter={(v) => currency === 'USD' ? `$${v.toLocaleString()}` : v.toLocaleString()}
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
              width={currency === 'USD' ? 60 : 70}
              domain={['auto', 'auto']}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null
                const d = payload[0].payload
                return (
                  <div className="bg-white border border-slate-200 rounded-lg px-3 py-2 shadow-lg text-xs">
                    <div className="font-medium text-slate-700 mb-1">{d.date}</div>
                    <div className="text-slate-600">종가: <span className="font-medium">{formatPrice(d.close, currency)}</span></div>
                    {d.high != null && (
                      <div className="text-slate-500">고가: {formatPrice(d.high, currency)} / 저가: {formatPrice(d.low, currency)}</div>
                    )}
                    <div className="text-slate-500">거래량: {formatVolume(d.volume)}</div>
                  </div>
                )
              }}
            />
            {avgPrice > 0 && (
              <ReferenceLine
                y={avgPrice}
                stroke="#f59e0b"
                strokeDasharray="4 4"
                strokeWidth={1.5}
                label={{ value: '평균매수가', position: 'insideTopRight', fill: '#f59e0b', fontSize: 10 }}
              />
            )}
            <Line
              type="monotone"
              dataKey="close"
              stroke={isUp ? '#ef4444' : '#3b82f6'}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 3, strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

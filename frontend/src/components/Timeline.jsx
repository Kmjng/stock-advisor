import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'

const formatDate = (ts) => {
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  const isBuy = d.trade_type === 'buy'
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm">
      <div className="font-bold text-slate-800">{d.stock_name} ({d.stock_code})</div>
      <div className={isBuy ? 'text-green-600' : 'text-purple-600'}>
        {isBuy ? '매수' : '매도'} {d.quantity.toLocaleString()}주
      </div>
      <div className="text-slate-600">
        @ {d.currency === 'USD'
          ? `$${d.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
          : `${d.price.toLocaleString()}원`}
      </div>
      <div className="text-slate-600">
        총 {d.currency === 'USD'
          ? `$${Math.abs(d.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}`
          : `${Math.abs(d.amount).toLocaleString()}원`}
      </div>
      {d.realized_profit != null && (
        <div className={d.realized_profit >= 0 ? 'text-red-600 font-medium' : 'text-blue-600 font-medium'}>
          실현손익: {d.realized_profit >= 0 ? '+' : ''}
          {Math.round(d.realized_profit).toLocaleString()}
        </div>
      )}
      <div className="text-slate-400 text-xs mt-1">{new Date(d.traded_at).toLocaleString('ko-KR')}</div>
    </div>
  )
}

export default function Timeline({ transactions }) {
  if (!transactions?.length) {
    return (
      <div className="text-center py-12 text-slate-400">
        거래내역이 없습니다. 아래에서 거래를 추가해주세요.
      </div>
    )
  }

  // 매수는 양수, 매도는 음수로 표시
  const data = transactions
    .slice()
    .sort((a, b) => new Date(a.traded_at) - new Date(b.traded_at))
    .map(t => ({
      ...t,
      date: formatDate(t.traded_at),
      amount: t.trade_type === 'buy' ? t.total_amount : -t.total_amount,
    }))

  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          stroke="#94a3b8"
        />
        <YAxis
          tickFormatter={(v) => {
            const abs = Math.abs(v)
            if (abs >= 1000000) return `${(v / 1000000).toFixed(1)}M`
            if (abs >= 1000) return `${(v / 1000).toFixed(0)}K`
            return v
          }}
          tick={{ fontSize: 12 }}
          stroke="#94a3b8"
        />
        <ReferenceLine y={0} stroke="#94a3b8" />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="amount" radius={[4, 4, 4, 4]} maxBarSize={40}>
          {data.map((entry, i) => (
            <Cell
              key={i}
              fill={entry.trade_type === 'buy' ? '#22c55e' : '#a855f7'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

const config = {
  buy: { label: '매수', bg: 'bg-green-100', text: 'text-green-700', ring: 'ring-green-300' },
  sell: { label: '매도', bg: 'bg-purple-100', text: 'text-purple-700', ring: 'ring-purple-300' },
  hold: { label: '관망', bg: 'bg-yellow-100', text: 'text-yellow-700', ring: 'ring-yellow-300' },
}

export default function RecommendBadge({ recommendation }) {
  const c = config[recommendation] || config.hold
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ring-1 ${c.bg} ${c.text} ${c.ring}`}>
      {c.label}
    </span>
  )
}

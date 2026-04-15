import RecommendBadge from './RecommendBadge'

export default function StockCard({ data }) {
  const { stock_name, stock_code, quantity, avg_price, news_count, articles, analysis, market, currency } = data
  const score = analysis?.sentiment_score ?? 0
  const scorePercent = ((score + 1) / 2) * 100
  const isUS = market === 'US'
  const currencyLabel = isUS ? '$' : ''
  const currencySuffix = isUS ? '' : '원'
  const flag = isUS ? '🇺🇸' : '🇰🇷'
  const formatPrice = (p) => isUS ? `$${p?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : `${p?.toLocaleString()}원`
  const formatQty = (q) => q % 1 === 0 ? `${q}주` : `${q.toFixed(4)}주`

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-bold text-slate-800 text-lg">{flag} {stock_name}</h3>
          <p className="text-sm text-slate-500">{stock_code}</p>
        </div>
        <RecommendBadge recommendation={analysis?.recommendation || 'hold'} />
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4 text-sm">
        <div className="bg-slate-50 rounded-lg p-2 text-center">
          <div className="text-slate-500">보유수량</div>
          <div className="font-semibold text-slate-800">{formatQty(quantity)}</div>
        </div>
        <div className="bg-slate-50 rounded-lg p-2 text-center">
          <div className="text-slate-500">평균매수가</div>
          <div className="font-semibold text-slate-800">{formatPrice(avg_price)}</div>
        </div>
        <div className="bg-slate-50 rounded-lg p-2 text-center">
          <div className="text-slate-500">뉴스</div>
          <div className="font-semibold text-slate-800">{news_count}건</div>
        </div>
      </div>

      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-red-500">부정</span>
          <span className="font-medium text-slate-600">감성점수: {score.toFixed(2)}</span>
          <span className="text-green-500">긍정</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all"
            style={{
              width: `${scorePercent}%`,
              background: score > 0 ? '#22c55e' : score < 0 ? '#ef4444' : '#eab308',
            }}
          />
        </div>
      </div>

      <p className="text-sm text-slate-600 mb-3">{analysis?.summary}</p>

      {analysis?.reasons?.length > 0 && (
        <ul className="text-xs text-slate-500 space-y-1 mb-3">
          {analysis.reasons.map((r, i) => (
            <li key={i} className="flex gap-1">
              <span className="text-slate-400">•</span> {r}
            </li>
          ))}
        </ul>
      )}

      {articles?.length > 0 && (
        <div className="border-t border-slate-100 pt-3">
          <div className="text-xs font-medium text-slate-500 mb-2">최근 뉴스</div>
          <div className="space-y-1.5">
            {articles.slice(0, 3).map((a, i) => (
              <a
                key={i}
                href={a.link}
                target="_blank"
                rel="noopener noreferrer"
                className="block text-xs text-slate-600 hover:text-blue-600 truncate"
              >
                [{a.date}] {a.title}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

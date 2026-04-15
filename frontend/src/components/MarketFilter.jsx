const tabs = [
  { value: '', label: '전체' },
  { value: 'KR', label: '국내' },
  { value: 'US', label: '해외' },
]

export default function MarketFilter({ value, onChange }) {
  return (
    <div className="flex gap-1 bg-slate-100 rounded-lg p-0.5">
      {tabs.map(tab => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            value === tab.value
              ? 'bg-white text-slate-800 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

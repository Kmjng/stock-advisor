import { useState } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Portfolio from './pages/Portfolio'
import Transactions from './pages/Transactions'
import Accounts from './pages/Accounts'
import PnL from './pages/PnL'
import TradeAnalysis from './pages/TradeAnalysis'
import NHSyncModal from './components/NHSyncModal'
import { AnalysisProvider } from './contexts/AnalysisContext'
import { AdvisorProvider } from './contexts/AdvisorContext'

function App() {
  const [showSync, setShowSync] = useState(false)

  return (
    <BrowserRouter>
    <AnalysisProvider>
    <AdvisorProvider>
      <div className="min-h-screen bg-slate-50">
        <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 flex items-center h-14 gap-8">
            <span className="font-bold text-lg text-slate-800">Stock Advisor</span>
            <div className="flex gap-1">
              {[
                ['/', '대시보드'],
                ['/portfolio', '보유종목'],
                ['/transactions', '거래내역'],
                ['/accounts', '계좌별 현황'],
                ['/pnl', '수익분석'],
                ['/analysis', 'AI매매분석'],
              ].map(([to, label]) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </div>
            <div className="ml-auto">
              <button
                onClick={() => setShowSync(true)}
                className="px-3 py-1.5 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 transition-colors"
              >
                나무증권 동기화
              </button>
            </div>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/accounts" element={<Accounts />} />
            <Route path="/pnl" element={<PnL />} />
            <Route path="/analysis" element={<TradeAnalysis />} />
          </Routes>
        </main>
        {showSync && <NHSyncModal onClose={() => setShowSync(false)} />}
      </div>
    </AdvisorProvider>
    </AnalysisProvider>
    </BrowserRouter>
  )
}

export default App

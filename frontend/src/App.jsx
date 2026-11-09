import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Sidebar  from './components/Sidebar';
import TopBar   from './components/TopBar';

import DashboardPage  from './pages/DashboardPage';
import IndicatorsPage from './pages/IndicatorsPage';
import SearchPage     from './pages/SearchPage';
import FeedsPage      from './pages/FeedsPage';
import MonitoringPage from './pages/MonitoringPage';
import ReportsPage    from './pages/ReportsPage';

import { checkBackendHealth } from './services/api';

function Layout() {
  const [health,      setHealth]      = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [pingLatency, setPingLatency] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    const t0 = performance.now();
    try {
      const data = await checkBackendHealth();
      setHealth(data);
      setPingLatency(Math.round(performance.now() - t0));
      setLastChecked(new Date().toLocaleTimeString());
    } catch {
      setHealth(null);
      setPingLatency(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    const id = setInterval(fetchHealth, 60_000);
    return () => clearInterval(id);
  }, [fetchHealth]);

  return (
    <div className="flex h-screen bg-[#0B1120] text-[#F8FAFC] overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar
          health={health}
          loading={loading}
          pingLatency={pingLatency}
          lastChecked={lastChecked}
          onRefresh={fetchHealth}
        />

        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/"           element={<DashboardPage />}  />
            <Route path="/indicators" element={<IndicatorsPage />} />
            <Route path="/search"     element={<SearchPage />}     />
            <Route path="/feeds"      element={<FeedsPage />}      />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route path="/reports"    element={<ReportsPage />}    />
          </Routes>
        </main>

        <footer className="shrink-0 border-t border-slate-800 bg-[#020617] py-2 px-6 text-center text-[10px] text-slate-600">
          ThreatView Cybersecurity Threat Intelligence Platform &bull; FastAPI · React · PostgreSQL · Recharts · ReportLab
        </footer>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  );
}

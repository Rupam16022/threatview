import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Activity, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Server, 
  Database, 
  Layers, 
  Radio, 
  Cpu, 
  ExternalLink,
  Terminal
} from 'lucide-react';
import { checkBackendHealth } from './services/api';

function App() {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pingLatency, setPingLatency] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    const startTime = performance.now();
    try {
      const data = await checkBackendHealth();
      const endTime = performance.now();
      setHealthData(data);
      setPingLatency(Math.round(endTime - startTime));
      setLastChecked(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to communicate with backend API:', err);
      setError(err.message || 'Cannot reach FastAPI backend server on http://localhost:8000');
      setHealthData(null);
      setPingLatency(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="min-h-screen bg-[#0B1120] text-[#F8FAFC] flex flex-col selection:bg-sky-500/30 selection:text-sky-300">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800 bg-[#020617]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-sky-500/10 border border-sky-500/20 rounded-lg text-[#38BDF8]">
            <ShieldAlert className="w-6 h-6 text-[#38BDF8]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-bold text-lg tracking-wider text-white">THREAT<span className="text-[#38BDF8]">VIEW</span></h1>
              <span className="px-2 py-0.5 text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded">
                v0.1.0 DEV
              </span>
            </div>
            <p className="text-xs text-[#94A3B8]">Cybersecurity Threat Intelligence Dashboard</p>
          </div>
        </div>

        {/* Live Status Badge */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-[#94A3B8]">System Pipeline:</span>
            {loading ? (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-[#F59E0B] border border-amber-500/20">
                <RefreshCw className="w-3 h-3 mr-1 animate-spin" /> Handshaking...
              </span>
            ) : healthData ? (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-[#22C55E] border border-emerald-500/20">
                <CheckCircle2 className="w-3 h-3 mr-1" /> API Connected ({pingLatency}ms)
              </span>
            ) : (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-[#EF4444] border border-rose-500/20">
                <XCircle className="w-3 h-3 mr-1" /> Offline
              </span>
            )}
          </div>

          <a 
            href="http://localhost:8000/docs" 
            target="_blank" 
            rel="noreferrer" 
            className="flex items-center space-x-1.5 text-xs text-[#38BDF8] hover:text-sky-300 transition-colors bg-sky-950/40 px-3 py-1.5 rounded-lg border border-sky-800/40"
          >
            <span>Interactive API Docs</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-8">
        
        {/* Banner */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-[#1E293B] to-slate-900 border border-slate-800 p-8 shadow-xl">
          <div className="relative z-10 max-w-3xl space-y-3">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-xs text-[#38BDF8] font-mono">
              <Radio className="w-3.5 h-3.5 animate-pulse text-[#38BDF8]" />
              <span>DAY 4: DUAL THREAT FEEDS (OTX + URLHAUS) INTEGRATED &amp; DE-DUPLICATED</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Threat Intelligence Operational Platform
            </h2>
            <p className="text-sm md:text-base text-[#94A3B8] leading-relaxed">
              ThreatView aggregates open-source threat intelligence (OSINT) from verified global security feeds 
              (AlienVault OTX, URLhaus) into a normalized indicator store for monitoring malicious IPs, domains, and URLs.
            </p>
          </div>
          
          <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-10 flex items-center justify-center pointer-events-none">
            <ShieldAlert className="w-80 h-80 text-sky-400" />
          </div>
        </div>

        {/* System Architecture Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Card 1: Frontend Client */}
          <div className="bg-[#1E293B] border border-slate-800 rounded-xl p-6 shadow-lg flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="p-3 bg-sky-500/10 border border-sky-500/20 rounded-lg text-[#38BDF8]">
                  <Layers className="w-6 h-6" />
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-sky-400 border border-slate-700">
                  Port 5173
                </span>
              </div>
              <div>
                <h3 className="font-semibold text-lg text-white">React 19 Frontend</h3>
                <p className="text-xs text-[#94A3B8] mt-1">
                  Vite build system, Tailwind CSS dark theme engine, and Axios HTTP client with reverse proxy.
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-[#94A3B8]">Status</span>
              <span className="text-[#22C55E] font-medium flex items-center">
                <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                Active (Localhost)
              </span>
            </div>
          </div>

          {/* Card 2: Backend API */}
          <div className="bg-[#1E293B] border border-slate-800 rounded-xl p-6 shadow-lg flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-[#22C55E]">
                  <Server className="w-6 h-6" />
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-slate-700">
                  Port 8000
                </span>
              </div>
              <div>
                <h3 className="font-semibold text-lg text-white">FastAPI Core API</h3>
                <p className="text-xs text-[#94A3B8] mt-1">
                  High-performance Python asynchronous REST API with Pydantic validation, CORS middleware, and Uvicorn.
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-[#94A3B8]">Backend Endpoint</span>
              <span className={`font-medium flex items-center ${healthData ? 'text-[#22C55E]' : 'text-[#EF4444]'}`}>
                <span className={`w-2 h-2 rounded-full mr-1.5 ${healthData ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                {healthData ? `${healthData.status.toUpperCase()} (${healthData.version})` : 'Offline / Unreachable'}
              </span>
            </div>
          </div>

          {/* Card 3: Storage Engine */}
          <div className="bg-[#1E293B] border border-slate-800 rounded-xl p-6 shadow-lg flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
                  <Database className="w-6 h-6" />
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">
                  Port 5432
                </span>
              </div>
              <div>
                <h3 className="font-semibold text-lg text-white">PostgreSQL Data Store</h3>
                <p className="text-xs text-[#94A3B8] mt-1">
                  Relational indicator &amp; observation tables, SQLAlchemy ORM, and Alembic schema migrations.
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-[#94A3B8]">Database Status</span>
              <span className={`font-medium flex items-center ${healthData?.database === 'connected' ? 'text-[#22C55E]' : 'text-amber-400'}`}>
                <span className={`w-2 h-2 rounded-full mr-1.5 ${healthData?.database === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'}`}></span>
                {healthData?.database === 'connected' ? 'Connected & Migrated' : 'Connecting...'}
              </span>
            </div>
          </div>
        </div>

        {/* Live Connection Diagnostics Console */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="bg-slate-900/90 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Terminal className="w-5 h-5 text-sky-400" />
              <h3 className="font-semibold text-sm text-white">Live Health Diagnostics Console (GET /api/health)</h3>
            </div>
            <div className="flex items-center space-x-3">
              {lastChecked && (
                <span className="text-xs text-[#94A3B8]">Last pinged: {lastChecked}</span>
              )}
              <button
                onClick={fetchHealth}
                disabled={loading}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-sky-500/10 hover:bg-sky-500/20 text-[#38BDF8] border border-sky-500/30 transition-all cursor-pointer disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Test Connection</span>
              </button>
            </div>
          </div>

          <div className="p-6">
            {loading && !healthData ? (
              <div className="flex items-center justify-center py-8 text-[#94A3B8] space-x-3">
                <RefreshCw className="w-5 h-5 animate-spin text-[#38BDF8]" />
                <span className="text-sm">Querying backend API status...</span>
              </div>
            ) : error ? (
              <div className="bg-rose-500/10 border border-rose-500/20 rounded-lg p-4 space-y-2">
                <div className="flex items-center space-x-2 text-[#EF4444]">
                  <XCircle className="w-5 h-5" />
                  <span className="font-semibold text-sm">Failed to connect to FastAPI Backend</span>
                </div>
                <p className="text-xs text-[#94A3B8] font-mono">{error}</p>
                <p className="text-xs text-slate-400 pt-1">
                  Ensure the backend server is running via: <code className="bg-slate-900 px-2 py-0.5 rounded text-sky-400">.\venv\Scripts\python -m uvicorn app.main:app --reload</code>
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-[#0B1120] border border-slate-800 rounded-lg p-3">
                    <span className="text-xs text-[#94A3B8] block">API Service</span>
                    <span className="text-sm font-semibold text-white">{healthData?.service}</span>
                  </div>
                  <div className="bg-[#0B1120] border border-slate-800 rounded-lg p-3">
                    <span className="text-xs text-[#94A3B8] block">Health Status</span>
                    <span className="text-sm font-semibold text-[#22C55E] flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> {healthData?.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="bg-[#0B1120] border border-slate-800 rounded-lg p-3">
                    <span className="text-xs text-[#94A3B8] block">API Version</span>
                    <span className="text-sm font-semibold text-sky-400 font-mono">v{healthData?.version}</span>
                  </div>
                  <div className="bg-[#0B1120] border border-slate-800 rounded-lg p-3">
                    <span className="text-xs text-[#94A3B8] block">Round-Trip Latency</span>
                    <span className="text-sm font-semibold text-emerald-400 font-mono">{pingLatency} ms</span>
                  </div>
                </div>

                <div className="bg-[#0B1120] border border-slate-800 rounded-lg p-4 font-mono text-xs overflow-x-auto text-slate-300">
                  <div className="text-sky-400 font-semibold mb-2 flex items-center justify-between">
                    <span>// Raw JSON Response from http://127.0.0.1:8000/api/health</span>
                    <span className="text-[10px] text-slate-500">200 OK</span>
                  </div>
                  <pre>{JSON.stringify(healthData, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 17-Day Roadmap Tracker */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-[#38BDF8]" />
              <h3 className="font-semibold text-base text-white">17-Day Internship Roadmap Tracker</h3>
            </div>
            <span className="text-xs text-[#94A3B8]">Day 4 of 17</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
            <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg flex items-center justify-between">
              <div>
                <span className="font-bold text-white">Day 1: Project Setup</span>
                <p className="text-[#94A3B8]">FastAPI + React + API Comms</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-medium border border-emerald-500/20">PASSED</span>
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg flex items-center justify-between">
              <div>
                <span className="font-bold text-white">Day 2: Threat Feed 1</span>
                <p className="text-[#94A3B8]">AlienVault OTX + ETL Normalizer</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-medium border border-emerald-500/20">PASSED</span>
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg flex items-center justify-between">
              <div>
                <span className="font-bold text-white">Day 3: Database Engine</span>
                <p className="text-[#94A3B8]">PostgreSQL + SQLAlchemy + Alembic</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-medium border border-emerald-500/20">PASSED</span>
            </div>

            <div className="p-3 bg-sky-500/10 border border-sky-500/30 rounded-lg flex items-center justify-between">
              <div>
                <span className="font-bold text-sky-400">Day 4: Threat Feed 2</span>
                <p className="text-[#94A3B8]">URLhaus Ingestion &amp; Normalization</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 font-medium">COMPLETED</span>
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg flex items-center justify-between opacity-80">
              <div>
                <span className="font-bold text-white">Day 5: Auto Scheduler</span>
                <p className="text-[#94A3B8]">APScheduler Background Engine</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-amber-400 font-medium">UP NEXT</span>
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg flex items-center justify-between opacity-80">
              <div>
                <span className="font-bold text-white">Day 6-17: Dashboard & Beyond</span>
                <p className="text-[#94A3B8]">Search, Maps, Alerts, Reports</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400">QUEUED</span>
            </div>
          </div>
        </div>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-[#020617] py-4 px-6 text-center text-xs text-[#94A3B8]">
        ThreatView Cybersecurity Threat Intelligence Platform &bull; Built with FastAPI, React, and PostgreSQL
      </footer>
    </div>
  );
}

export default App;

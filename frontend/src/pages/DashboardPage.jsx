import React, { useState, useEffect, useCallback } from 'react';
import {
  AreaChart, Area,
  BarChart, Bar,
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import {
  Database, TrendingUp, Globe, Zap,
  Radio, Activity, RefreshCw, AlertTriangle,
} from 'lucide-react';

import StatCard from '../components/StatCard';
import {
  fetchDashboardStats,
  fetchTrends,
  fetchCategories,
  fetchSources,
  fetchSchedulerStatus,
} from '../services/api';

/* ── palette ─────────────────────────────────────────────────────────────── */
const PIE_COLORS = ['#38BDF8','#818CF8','#34D399','#FBBF24','#F87171','#A78BFA'];

/* ── custom tooltip ───────────────────────────────────────────────────────── */
function DarkTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs shadow-xl">
      {label && <p className="text-slate-400 mb-1">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || p.fill }} className="font-semibold">
          {p.name ?? 'count'}: {p.value}
        </p>
      ))}
    </div>
  );
}

/* ── Section wrapper ──────────────────────────────────────────────────────── */
function Section({ title, icon: Icon, children, className = '' }) {
  return (
    <div className={`bg-[#1E293B] border border-slate-800 rounded-xl p-5 shadow-lg ${className}`}>
      <div className="flex items-center space-x-2 mb-4">
        <Icon className="w-4 h-4 text-sky-400" />
        <h3 className="text-sm font-semibold text-white">{title}</h3>
      </div>
      {children}
    </div>
  );
}

/* ── empty state ──────────────────────────────────────────────────────────── */
function EmptyChart({ message }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-slate-600 space-y-2 py-10">
      <AlertTriangle className="w-8 h-8" />
      <p className="text-xs text-center max-w-xs">{message}</p>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════ */
export default function DashboardPage() {
  const [stats,      setStats]      = useState(null);
  const [trends,     setTrends]     = useState([]);
  const [categories, setCategories] = useState([]);
  const [sources,    setSources]    = useState([]);
  const [scheduler,  setScheduler]  = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(null);
  const [lastFetch,  setLastFetch]  = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, t, c, src, sch] = await Promise.all([
        fetchDashboardStats(),
        fetchTrends(30),
        fetchCategories(),
        fetchSources(),
        fetchSchedulerStatus(),
      ]);
      setStats(s);
      setTrends(t);
      setCategories(c);
      setSources(src);
      setScheduler(sch);
      setLastFetch(new Date().toLocaleTimeString());
    } catch (err) {
      console.error(err);
      setError('Failed to fetch dashboard data. Is the backend running on port 8000?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  /* ── error banner ─────────────────────────────────────────────────────── */
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center space-y-4 p-12">
        <AlertTriangle className="w-12 h-12 text-rose-500" />
        <h2 className="text-lg font-semibold text-white">Backend Unreachable</h2>
        <p className="text-sm text-slate-400 max-w-sm">{error}</p>
        <button
          onClick={load}
          className="flex items-center space-x-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" /> <span>Retry</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">

      {/* ── Page header ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-extrabold text-white tracking-tight">Threat Intelligence Overview</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Live data · {lastFetch ? `Updated ${lastFetch}` : 'Loading…'}
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sm text-white rounded-lg border border-slate-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* ── Day 7 Banner ────────────────────────────────────────────────── */}
      <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-sky-500/20 px-6 py-4">
        <div className="flex items-center space-x-3">
          <Radio className="w-4 h-4 text-sky-400 animate-pulse" />
          <span className="text-xs font-mono text-sky-400">DAY 7: DASHBOARD UI LAYOUT & LIVE CHARTS VERIFIED</span>
        </div>
        <div className="absolute inset-0 bg-sky-500/5 pointer-events-none" />
      </div>

      {/* ── Stat cards ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          icon={Database} label="Total Indicators"
          value={stats?.total_indicators?.toLocaleString()}
          sub="All feeds combined"
          color="sky" loading={loading}
        />
        <StatCard
          icon={TrendingUp} label="New (Last 24h)"
          value={stats?.new_today?.toLocaleString()}
          sub="Fresh IoCs ingested"
          color="emerald" loading={loading}
        />
        <StatCard
          icon={Globe} label="IP Indicators"
          value={stats?.ip_indicators?.toLocaleString()}
          sub="IPv4 + IPv6"
          color="violet" loading={loading}
        />
        <StatCard
          icon={Zap} label="URL Indicators"
          value={stats?.url_indicators?.toLocaleString()}
          sub="Malicious URLs"
          color="amber" loading={loading}
        />
      </div>

      {/* ── Row 2: Trend chart + Pie chart ──────────────────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

        {/* Area chart — 30-day trend */}
        <Section title="30-Day Indicator Trend" icon={TrendingUp} className="xl:col-span-2">
          {loading ? (
            <div className="h-52 bg-slate-800/50 animate-pulse rounded-lg" />
          ) : trends.length === 0 ? (
            <EmptyChart message="No trend data yet. Trigger a feed ingestion to start tracking daily new indicators." />
          ) : (
            <ResponsiveContainer width="100%" height={210}>
              <AreaChart data={trends} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#38BDF8" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#38BDF8" stopOpacity={0}   />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip content={<DarkTooltip />} />
                <Area
                  type="monotone" dataKey="count" name="New Indicators"
                  stroke="#38BDF8" fill="url(#areaGrad)" strokeWidth={2} dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </Section>

        {/* Pie chart — categories */}
        <Section title="Threat Categories" icon={Activity}>
          {loading ? (
            <div className="h-52 bg-slate-800/50 animate-pulse rounded-lg" />
          ) : categories.length === 0 ? (
            <EmptyChart message="No category data. Ingest threat feeds first." />
          ) : (
            <div>
              <ResponsiveContainer width="100%" height={170}>
                <PieChart>
                  <Pie
                    data={categories} cx="50%" cy="50%"
                    innerRadius={45} outerRadius={75}
                    dataKey="count" nameKey="category"
                    paddingAngle={2}
                  >
                    {categories.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<DarkTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1.5 mt-2">
                {categories.map((c, i) => (
                  <div key={c.category} className="flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} />
                      <span className="text-slate-300 capitalize">{c.category}</span>
                    </div>
                    <span className="text-slate-400 font-mono">{c.count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Section>
      </div>

      {/* ── Row 3: Source bar chart + Scheduler status ───────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

        {/* Bar chart — source attribution */}
        <Section title="Observations by Source Feed" icon={Radio}>
          {loading ? (
            <div className="h-40 bg-slate-800/50 animate-pulse rounded-lg" />
          ) : sources.length === 0 ? (
            <EmptyChart message="No source data yet." />
          ) : (
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={sources} layout="vertical" margin={{ left: 10, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#64748B', fontSize: 10 }} tickLine={false} axisLine={false} allowDecimals={false} />
                <YAxis dataKey="source_name" type="category" tick={{ fill: '#94A3B8', fontSize: 11 }} width={120} tickLine={false} axisLine={false} />
                <Tooltip content={<DarkTooltip />} />
                <Bar dataKey="count" name="Observations" fill="#38BDF8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Section>

        {/* Scheduler status card */}
        <Section title="Background Scheduler" icon={Activity}>
          {loading ? (
            <div className="space-y-2">
              {[1,2,3].map(i => <div key={i} className="h-6 bg-slate-700/50 animate-pulse rounded" />)}
            </div>
          ) : !scheduler ? (
            <EmptyChart message="Could not reach scheduler status endpoint." />
          ) : (
            <div className="space-y-3">
              {/* Running badge */}
              <div className="flex items-center space-x-3">
                <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
                  scheduler.scheduler_running
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                }`}>
                  <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${scheduler.scheduler_running ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
                  {scheduler.scheduler_running ? 'Scheduler Running' : 'Scheduler Stopped'}
                </span>
                <span className="text-xs text-slate-500">
                  {scheduler.active_jobs_count} active job{scheduler.active_jobs_count !== 1 ? 's' : ''}
                </span>
              </div>

              {/* Jobs list */}
              <div className="space-y-2">
                {(scheduler.jobs ?? []).map(job => (
                  <div key={job.id} className="bg-slate-900/60 border border-slate-700/50 rounded-lg px-3 py-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-300 font-mono">{job.name ?? job.id}</span>
                      <span className="text-sky-400">
                        {job.next_run_time
                          ? `Next: ${new Date(job.next_run_time).toLocaleTimeString()}`
                          : 'Paused'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Manual trigger buttons */}
              <div className="flex space-x-2 pt-1">
                {['otx','urlhaus'].map(src => (
                  <button
                    key={src}
                    onClick={async () => {
                      try {
                        const r = await fetch(`http://localhost:8000/api/scheduler/trigger/${src}`, { method: 'POST' });
                        const d = await r.json();
                        alert(d.message);
                      } catch { alert('Trigger failed'); }
                    }}
                    className="px-3 py-1 text-xs bg-sky-600/20 hover:bg-sky-600/40 text-sky-300 border border-sky-700/40 rounded-lg transition-colors font-mono"
                  >
                    ▶ {src.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          )}
        </Section>
      </div>

      {/* ── Roadmap tracker ─────────────────────────────────────────────── */}
      <div className="bg-[#1E293B] border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-sky-400" />
            <h3 className="text-sm font-semibold text-white">17-Day Internship Roadmap</h3>
          </div>
          <span className="text-xs text-slate-500">Day 7 of 17</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          {[
            { day: 1,      title: 'Project Setup',         status: 'PASSED'    },
            { day: 2,      title: 'Threat Feed 1 (OTX)',   status: 'PASSED'    },
            { day: 3,      title: 'Database Engine',       status: 'PASSED'    },
            { day: 4,      title: 'Threat Feed 2 (URLh.)', status: 'PASSED'    },
            { day: 5,      title: 'Auto Scheduler',        status: 'PASSED'    },
            { day: 6,      title: 'Dashboard APIs',        status: 'PASSED'    },
            { day: 7,      title: 'Dashboard UI & Charts', status: 'COMPLETED' },
            { day: '8–17', title: 'Search, Alerts & More', status: 'QUEUED'   },
          ].map(item => (
            <div
              key={item.day}
              className={`px-3 py-2 rounded-lg border flex items-center justify-between ${
                item.status === 'COMPLETED'
                  ? 'bg-sky-500/10 border-sky-500/25 text-sky-300'
                  : item.status === 'PASSED'
                  ? 'bg-emerald-500/5 border-emerald-800/40 text-emerald-400'
                  : 'bg-slate-900/60 border-slate-800 text-slate-500'
              }`}
            >
              <span className="font-medium truncate mr-2">Day {item.day}: {item.title}</span>
              <span className={`shrink-0 text-[10px] font-bold ${
                item.status === 'COMPLETED' ? 'text-sky-400'
                : item.status === 'PASSED'   ? 'text-emerald-400'
                : 'text-slate-600'
              }`}>{item.status}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}

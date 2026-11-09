import React, { useState, useEffect } from 'react';
import { Radio, RefreshCw, CheckCircle2, XCircle, Clock } from 'lucide-react';
import api from '../services/api';

function statusBadge(status) {
  const map = {
    completed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    running:   'bg-sky-500/10 text-sky-400 border-sky-500/20',
    failed:    'bg-rose-500/10 text-rose-400 border-rose-500/20',
    skipped:   'bg-slate-700 text-slate-400 border-slate-600',
  };
  return map[status] ?? 'bg-slate-700 text-slate-400';
}

export default function FeedsPage() {
  const [jobs,      setJobs]      = useState([]);
  const [scheduler, setScheduler] = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [triggering, setTriggering] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [j, s] = await Promise.all([
        api.get('/scheduler/jobs', { params: { limit: 30 } }),
        api.get('/scheduler/status'),
      ]);
      setJobs(j.data);
      setScheduler(s.data);
    } catch { /* backend offline */ }
    finally { setLoading(false); }
  };

  const trigger = async (source) => {
    setTriggering(source);
    try {
      const res = await api.post(`/scheduler/trigger/${source}`);
      alert(res.data.message);
      setTimeout(load, 2000); // reload after 2s
    } catch (e) {
      alert(`Trigger failed: ${e.message}`);
    } finally {
      setTriggering('');
    }
  };

  useEffect(() => { load(); }, []);

  const feeds = [
    {
      key: 'otx',
      name: 'AlienVault OTX',
      description: 'Open Threat Exchange – global threat sharing community with IP, domain, URL, and file hash pulses.',
      docs: 'https://otx.alienvault.com/api',
      color: 'sky',
    },
    {
      key: 'urlhaus',
      name: 'URLhaus (abuse.ch)',
      description: 'Malware URL database tracking active malware download sites and C2 infrastructure.',
      docs: 'https://urlhaus-api.abuse.ch',
      color: 'violet',
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-extrabold text-white">Threat Feed Sources</h2>
          <p className="text-xs text-slate-400 mt-0.5">Manage and monitor active OSINT intelligence feeds</p>
        </div>
        <button
          onClick={load}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg transition-colors"
        >
          <RefreshCw className="w-3 h-3" /><span>Refresh</span>
        </button>
      </div>

      {/* Scheduler status banner */}
      {scheduler && (
        <div className={`flex items-center space-x-3 px-4 py-3 rounded-xl border text-sm ${
          scheduler.scheduler_running
            ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400'
            : 'bg-rose-500/5 border-rose-500/20 text-rose-400'
        }`}>
          {scheduler.scheduler_running
            ? <CheckCircle2 className="w-4 h-4" />
            : <XCircle className="w-4 h-4" />}
          <span>
            Background scheduler is <strong>{scheduler.scheduler_running ? 'running' : 'stopped'}</strong>
            {' '}— {scheduler.active_jobs_count} job{scheduler.active_jobs_count !== 1 ? 's' : ''} registered
          </span>
        </div>
      )}

      {/* Feed cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {feeds.map(feed => (
          <div key={feed.key} className="bg-[#1E293B] border border-slate-800 rounded-xl p-5 space-y-4 shadow-lg">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className={`p-2.5 rounded-lg border ${feed.color === 'sky' ? 'bg-sky-500/10 border-sky-500/20 text-sky-400' : 'bg-violet-500/10 border-violet-500/20 text-violet-400'}`}>
                  <Radio className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-white text-sm">{feed.name}</h3>
                  <a href={feed.docs} target="_blank" rel="noreferrer" className="text-[10px] text-sky-500 hover:text-sky-400">
                    {feed.docs}
                  </a>
                </div>
              </div>
              <span className="px-2 py-0.5 text-[10px] rounded border bg-emerald-500/10 text-emerald-400 border-emerald-500/20 font-semibold">ACTIVE</span>
            </div>

            <p className="text-xs text-slate-400">{feed.description}</p>

            {/* Last job stats */}
            {(() => {
              const last = jobs.find(j => j.source_name?.toLowerCase().includes(feed.key));
              if (!last) return <p className="text-xs text-slate-600">No runs recorded yet.</p>;
              return (
                <div className="grid grid-cols-3 gap-2 text-[10px]">
                  {[
                    ['Inserted', last.records_inserted],
                    ['Updated',  last.records_updated],
                    ['Received', last.records_received],
                  ].map(([k, v]) => (
                    <div key={k} className="bg-slate-900/60 rounded-lg px-2 py-1.5 text-center">
                      <p className="text-slate-500">{k}</p>
                      <p className="text-white font-bold text-sm mt-0.5">{v ?? 0}</p>
                    </div>
                  ))}
                </div>
              );
            })()}

            <button
              onClick={() => trigger(feed.key)}
              disabled={triggering === feed.key}
              className={`w-full py-2 rounded-lg text-xs font-medium transition-colors border ${
                feed.color === 'sky'
                  ? 'bg-sky-600/20 hover:bg-sky-600/40 text-sky-300 border-sky-700/40'
                  : 'bg-violet-600/20 hover:bg-violet-600/40 text-violet-300 border-violet-700/40'
              } disabled:opacity-40`}
            >
              {triggering === feed.key ? '⏳ Triggering…' : `▶ Trigger ${feed.name} Now`}
            </button>
          </div>
        ))}
      </div>

      {/* Ingestion history */}
      <div className="bg-[#1E293B] border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="flex items-center space-x-2 px-5 py-4 border-b border-slate-800">
          <Clock className="w-4 h-4 text-sky-400" />
          <h3 className="text-sm font-semibold text-white">Ingestion Job History</h3>
        </div>
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-slate-900/50 text-slate-400 text-left border-b border-slate-800">
              <th className="px-4 py-3 font-medium">Source</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Started</th>
              <th className="px-4 py-3 font-medium">Inserted</th>
              <th className="px-4 py-3 font-medium">Updated</th>
              <th className="px-4 py-3 font-medium">Error</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b border-slate-800/50">
                  {Array.from({ length: 6 }).map((_, j) => (
                    <td key={j} className="px-4 py-3"><div className="h-3 bg-slate-700/50 animate-pulse rounded" /></td>
                  ))}
                </tr>
              ))
            ) : jobs.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-slate-500">No jobs run yet. Use the trigger buttons above.</td></tr>
            ) : (
              jobs.map(job => (
                <tr key={job.id} className="border-b border-slate-800/40 hover:bg-slate-800/20 transition-colors">
                  <td className="px-4 py-3 text-slate-300 font-medium">{job.source_name}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded border text-[10px] font-semibold uppercase ${statusBadge(job.status)}`}>{job.status}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-400">{job.started_at ? new Date(job.started_at).toLocaleString() : '—'}</td>
                  <td className="px-4 py-3 text-emerald-400 font-mono">{job.records_inserted ?? 0}</td>
                  <td className="px-4 py-3 text-sky-400 font-mono">{job.records_updated ?? 0}</td>
                  <td className="px-4 py-3 text-rose-400 font-mono max-w-xs truncate">{job.error_message ?? '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

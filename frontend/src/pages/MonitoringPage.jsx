import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Trash2, RefreshCw, Bell, BellOff, ShieldAlert, CheckCircle2, Globe } from 'lucide-react';
import api from '../services/api';

/* ── tiny helpers ───────────────────────────────────────────────────────── */
function Badge({ children, color = 'sky' }) {
  const cls = {
    sky:     'bg-sky-500/10 text-sky-400 border-sky-500/25',
    rose:    'bg-rose-500/10 text-rose-400 border-rose-500/25',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25',
    slate:   'bg-slate-700 text-slate-400 border-slate-600',
  }[color];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-[10px] font-semibold uppercase ${cls}`}>
      {children}
    </span>
  );
}

export default function MonitoringPage() {
  const [domains,    setDomains]    = useState([]);
  const [alerts,     setAlerts]     = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [scanning,   setScanning]   = useState(false);
  const [newDomain,  setNewDomain]  = useState('');
  const [adding,     setAdding]     = useState(false);
  const [error,      setError]      = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [d, a] = await Promise.all([
        api.get('/monitoring/domains'),
        api.get('/monitoring/alerts'),
      ]);
      setDomains(d.data);
      setAlerts(a.data);
    } catch { /* backend may be offline */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const addDomain = async (e) => {
    e.preventDefault();
    if (!newDomain.trim()) return;
    setAdding(true);
    setError('');
    try {
      await api.post('/monitoring/domains', { domain: newDomain.trim() });
      setNewDomain('');
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add domain.');
    } finally {
      setAdding(false);
    }
  };

  const removeDomain = async (id) => {
    try {
      await api.delete(`/monitoring/domains/${id}`);
      await load();
    } catch { /* ignore */ }
  };

  const markRead = async (id) => {
    try {
      await api.post(`/monitoring/alerts/${id}/read`);
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, read_status: true } : a));
    } catch { /* ignore */ }
  };

  const triggerScan = async () => {
    setScanning(true);
    try {
      const res = await api.post('/monitoring/scan');
      alert(res.data.message);
      await load();
    } catch { alert('Scan failed.'); }
    finally { setScanning(false); }
  };

  const unreadCount = alerts.filter(a => !a.read_status).length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-extrabold text-white">Domain Monitoring</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Watch your domains for matches in the threat database
          </p>
        </div>
        <button
          onClick={triggerScan}
          disabled={scanning || domains.length === 0}
          className="flex items-center space-x-2 px-4 py-2 bg-sky-600/20 hover:bg-sky-600/40 text-sky-300 border border-sky-700/40 rounded-lg text-xs transition-colors disabled:opacity-40"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
          <span>{scanning ? 'Scanning…' : 'Scan Now'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Add domain + watchlist */}
        <div className="space-y-4">
          <div className="bg-[#1E293B] border border-slate-800 rounded-xl p-5 shadow-lg">
            <div className="flex items-center space-x-2 mb-4">
              <Globe className="w-4 h-4 text-sky-400" />
              <h3 className="text-sm font-semibold text-white">Monitored Domains</h3>
              <Badge color="sky">{domains.length}</Badge>
            </div>

            {/* Add form */}
            <form onSubmit={addDomain} className="flex space-x-2 mb-4">
              <input
                type="text"
                value={newDomain}
                onChange={e => setNewDomain(e.target.value)}
                placeholder="e.g. evil-corp.ru"
                className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
              <button
                type="submit"
                disabled={adding || !newDomain.trim()}
                className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs rounded-lg transition-colors disabled:opacity-40 flex items-center space-x-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>{adding ? 'Adding…' : 'Add'}</span>
              </button>
            </form>
            {error && <p className="text-xs text-rose-400 mb-3">{error}</p>}

            {/* Domain list */}
            {loading ? (
              <div className="space-y-2">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-10 bg-slate-800/60 animate-pulse rounded-lg" />
                ))}
              </div>
            ) : domains.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-6">
                No domains monitored yet. Add a domain above.
              </p>
            ) : (
              <div className="space-y-2">
                {domains.map(d => (
                  <div key={d.id} className="flex items-center justify-between bg-slate-900/60 border border-slate-700/50 rounded-lg px-3 py-2.5 text-sm">
                    <div className="flex items-center space-x-3">
                      <span className={`w-2 h-2 rounded-full ${d.is_active ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                      <span className="text-slate-200 font-mono text-xs">{d.domain}</span>
                    </div>
                    <button
                      onClick={() => removeDomain(d.id)}
                      className="text-slate-500 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Alerts panel */}
        <div className="bg-[#1E293B] border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Bell className="w-4 h-4 text-sky-400" />
              <h3 className="text-sm font-semibold text-white">In-App Alerts</h3>
              {unreadCount > 0 && (
                <span className="inline-flex items-center justify-center w-5 h-5 bg-rose-500 text-white text-[10px] font-bold rounded-full">
                  {unreadCount}
                </span>
              )}
            </div>
            <button onClick={load} className="text-slate-500 hover:text-slate-300 transition-colors">
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-14 bg-slate-800/60 animate-pulse rounded-lg" />
              ))}
            </div>
          ) : alerts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-slate-600 space-y-2">
              <BellOff className="w-8 h-8" />
              <p className="text-xs text-center">
                No alerts yet. Add domains to monitor and click "Scan Now."
              </p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
              {alerts.map(a => (
                <div
                  key={a.id}
                  className={`rounded-lg border px-3 py-2.5 text-xs transition-all ${
                    a.read_status
                      ? 'bg-slate-900/40 border-slate-800 opacity-60'
                      : 'bg-rose-500/5 border-rose-500/20'
                  }`}
                >
                  <div className="flex items-start justify-between space-x-2">
                    <div className="flex items-start space-x-2 flex-1 min-w-0">
                      <ShieldAlert className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${a.read_status ? 'text-slate-500' : 'text-rose-400'}`} />
                      <div className="min-w-0">
                        <p className="text-slate-300 leading-snug">{a.message}</p>
                        {a.indicator_value && (
                          <p className="font-mono text-sky-400 mt-0.5 truncate">{a.indicator_value}</p>
                        )}
                        <p className="text-slate-600 mt-1">{new Date(a.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                    {!a.read_status && (
                      <button
                        onClick={() => markRead(a.id)}
                        className="shrink-0 text-slate-500 hover:text-emerald-400 transition-colors"
                        title="Mark as read"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

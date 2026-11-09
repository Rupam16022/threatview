import React, { useState, useEffect } from 'react';
import { Activity, ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../services/api';

const TYPE_COLOR = {
  ipv4:   'bg-sky-500/10 text-sky-400 border-sky-500/25',
  ipv6:   'bg-sky-500/10 text-sky-400 border-sky-500/25',
  url:    'bg-violet-500/10 text-violet-400 border-violet-500/25',
  domain: 'bg-amber-500/10 text-amber-400 border-amber-500/25',
  md5:    'bg-emerald-500/10 text-emerald-400 border-emerald-500/25',
  sha256: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25',
};

const CAT_COLOR = {
  malware:    'text-rose-400',
  phishing:   'text-orange-400',
  c2:         'text-red-500',
  scanning:   'text-amber-400',
  suspicious: 'text-slate-400',
};

export default function IndicatorsPage() {
  const [rows,    setRows]    = useState([]);
  const [loading, setLoading] = useState(true);
  const [page,    setPage]    = useState(0);
  const [typeFilter, setTypeFilter] = useState('');
  const [plan,    setPlan]    = useState('pro');
  const limit = 25;

  const load = async () => {
    setLoading(true);
    try {
      const params = { limit, offset: page * limit, plan };
      if (typeFilter) params.indicator_type = typeFilter;
      const res = await api.get('/indicators', { params });
      setRows(res.data);
    } catch {
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [page, typeFilter, plan]);

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-extrabold text-white">Threat Indicators</h2>
          <p className="text-xs text-slate-400 mt-0.5">All ingested IoCs from active threat feeds</p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Plan Tier Selector */}
          <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => { setPlan('free'); setPage(0); }}
              className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                plan === 'free' ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' : 'text-slate-400 hover:text-white'
              }`}
            >
              Free (24h)
            </button>
            <button
              onClick={() => { setPlan('pro'); setPage(0); }}
              className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                plan === 'pro' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-400 hover:text-white'
              }`}
            >
              Pro (All)
            </button>
          </div>

          {/* Type filter */}
          <select
            value={typeFilter}
            onChange={e => { setTypeFilter(e.target.value); setPage(0); }}
            className="text-xs bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-sky-500"
          >
            <option value="">All Types</option>
            {['ipv4','ipv6','url','domain','md5','sha256'].map(t => (
              <option key={t} value={t}>{t.toUpperCase()}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-[#1E293B] border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/50 text-slate-400 text-left">
              <th className="px-4 py-3 font-medium">Type</th>
              <th className="px-4 py-3 font-medium">Indicator</th>
              <th className="px-4 py-3 font-medium">Category</th>
              <th className="px-4 py-3 font-medium">Country</th>
              <th className="px-4 py-3 font-medium">Confidence</th>
              <th className="px-4 py-3 font-medium">First Seen</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 8 }).map((_, i) => (
                <tr key={i} className="border-b border-slate-800/50">
                  {Array.from({ length: 6 }).map((_, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 bg-slate-700/50 animate-pulse rounded" />
                    </td>
                  ))}
                </tr>
              ))
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-slate-500">
                  No indicators found. Trigger a feed ingestion to populate data.
                </td>
              </tr>
            ) : (
              rows.map(row => (
                <tr key={row.id} className="border-b border-slate-800/40 hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded border text-[10px] font-semibold uppercase ${TYPE_COLOR[row.indicator_type] ?? 'bg-slate-700 text-slate-300 border-slate-600'}`}>
                      {row.indicator_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-slate-200 max-w-xs truncate">{row.indicator}</td>
                  <td className={`px-4 py-3 capitalize font-medium ${CAT_COLOR[row.category] ?? 'text-slate-400'}`}>
                    {row.category ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-400 font-mono">{row.country_code ?? '—'}</td>
                  <td className="px-4 py-3">
                    {row.confidence != null ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-16 h-1.5 bg-slate-700 rounded-full">
                          <div
                            className="h-1.5 rounded-full bg-sky-400"
                            style={{ width: `${row.confidence}%` }}
                          />
                        </div>
                        <span className="text-slate-400">{row.confidence}</span>
                      </div>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-500">
                    {row.first_seen ? new Date(row.first_seen).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800 bg-slate-900/30">
          <span className="text-xs text-slate-500">Page {page + 1}</span>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0 || loading}
              className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 hover:text-white disabled:opacity-30 transition-colors"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={rows.length < limit || loading}
              className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 hover:text-white disabled:opacity-30 transition-colors"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

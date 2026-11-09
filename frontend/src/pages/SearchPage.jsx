import React, { useState } from 'react';
import { Search, ShieldAlert, AlertTriangle, CheckCircle2 } from 'lucide-react';
import api from '../services/api';

export default function SearchPage() {
  const [query,   setQuery]   = useState('');
  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    setResult(null);
    try {
      const res = await api.get('/indicators/search', { params: { q: query.trim() } });
      setResult(res.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setResult(null);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-white">IoC Lookup</h2>
        <p className="text-xs text-slate-400 mt-0.5">Search for a specific IP, domain, URL, or file hash in the threat database</p>
      </div>

      {/* Search form */}
      <form onSubmit={handleSearch} className="flex space-x-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="e.g. 192.168.1.1 · example.com · http://evil.com/path"
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium rounded-xl transition-colors disabled:opacity-40"
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      {/* Result */}
      {searched && !loading && (
        result ? (
          <div className="bg-[#1E293B] border border-emerald-500/25 rounded-xl p-5 space-y-4">
            {/* Threat found header */}
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-rose-500/10 border border-rose-500/25 rounded-lg">
                <ShieldAlert className="w-5 h-5 text-rose-400" />
              </div>
              <div>
                <p className="text-sm font-bold text-rose-400">⚠ Threat Indicator Found</p>
                <p className="text-xs text-slate-400 font-mono break-all">{result.indicator}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              {[
                ['Type',       result.indicator_type?.toUpperCase()],
                ['Category',   result.category ?? '—'],
                ['Country',    result.country_code ?? '—'],
                ['Confidence', result.confidence != null ? `${result.confidence}/100` : '—'],
                ['First Seen', result.first_seen ? new Date(result.first_seen).toLocaleString() : '—'],
                ['Last Seen',  result.last_seen  ? new Date(result.last_seen).toLocaleString()  : '—'],
              ].map(([label, val]) => (
                <div key={label} className="bg-slate-900/60 rounded-lg px-3 py-2">
                  <p className="text-slate-500 text-[10px] uppercase tracking-wide">{label}</p>
                  <p className="text-slate-200 font-mono mt-0.5 capitalize">{val}</p>
                </div>
              ))}
            </div>

            {/* Observations */}
            {result.observations?.length > 0 && (
              <div>
                <p className="text-xs text-slate-400 font-semibold mb-2">Source Observations ({result.observations.length})</p>
                <div className="space-y-2">
                  {result.observations.map(obs => (
                    <div key={obs.id} className="bg-slate-900/60 rounded-lg px-3 py-2 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sky-400 font-medium">{obs.source_name}</span>
                        <span className="text-slate-500">{obs.collected_at ? new Date(obs.collected_at).toLocaleString() : ''}</span>
                      </div>
                      {obs.description && <p className="text-slate-400">{obs.description}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-[#1E293B] border border-emerald-500/20 rounded-xl p-8 text-center space-y-3">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <p className="text-sm font-semibold text-emerald-400">No Threats Found</p>
            <p className="text-xs text-slate-400">
              "<span className="font-mono text-slate-300">{query}</span>" is not in the current threat database.
            </p>
            <p className="text-[11px] text-slate-600">Note: database is populated only when threat feeds have been ingested.</p>
          </div>
        )
      )}

      {/* Hint when nothing searched */}
      {!searched && (
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 text-center text-slate-600 text-xs space-y-1">
          <Search className="w-8 h-8 mx-auto mb-2 opacity-30" />
          <p>Enter an IP address, domain, URL, or file hash above to look it up in the threat database.</p>
        </div>
      )}
    </div>
  );
}

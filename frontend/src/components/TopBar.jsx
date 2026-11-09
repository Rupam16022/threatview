import React from 'react';
import { RefreshCw, ExternalLink, CheckCircle2, XCircle } from 'lucide-react';

export default function TopBar({ health, loading, pingLatency, lastChecked, onRefresh }) {
  return (
    <header className="h-14 shrink-0 border-b border-slate-800 bg-[#020617]/90 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex items-center space-x-2 text-xs">
        <span className="text-slate-500">Pipeline:</span>
        {loading ? (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <RefreshCw className="w-3 h-3 mr-1 animate-spin" /> Connecting…
          </span>
        ) : health ? (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3 mr-1" /> API Online {pingLatency ? `· ${pingLatency}ms` : ''}
          </span>
        ) : (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3 mr-1" /> API Offline
          </span>
        )}
        {lastChecked && <span className="text-slate-600">· {lastChecked}</span>}
      </div>

      <div className="flex items-center space-x-3">
        <button
          onClick={onRefresh}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white transition-colors bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/40"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Refresh</span>
        </button>
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          className="flex items-center space-x-1.5 text-xs text-sky-400 hover:text-sky-300 bg-sky-950/40 px-3 py-1.5 rounded-lg border border-sky-800/40 transition-colors"
        >
          <span>API Docs</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </header>
  );
}

import React, { useState } from 'react';
import { FileText, Download, RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '../services/api';

export default function ReportsPage() {
  const [loading,  setLoading]  = useState(false);
  const [success,  setSuccess]  = useState(false);
  const [error,    setError]    = useState('');

  const downloadReport = async () => {
    setLoading(true);
    setSuccess(false);
    setError('');
    try {
      const res = await fetch(`${API_BASE_URL}/reports/weekly`);
      if (!res.ok) throw new Error(`Server error ${res.status}`);

      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);

      // Build filename from Content-Disposition or use default
      const cd = res.headers.get('content-disposition') || '';
      const match = cd.match(/filename="(.+?)"/);
      const filename = match ? match[1] : 'threatview_report.pdf';

      // Trigger browser download
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);

      setSuccess(true);
      setTimeout(() => setSuccess(false), 4000);
    } catch (err) {
      setError(`Download failed: ${err.message}. Is the backend running on port 8000?`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-white">Threat Intelligence Reports</h2>
        <p className="text-xs text-slate-400 mt-0.5">Generate downloadable PDF reports from live database stats</p>
      </div>

      {/* Report card */}
      <div className="bg-[#1E293B] border border-slate-800 rounded-xl p-6 shadow-lg space-y-5">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-sky-500/10 border border-sky-500/20 rounded-xl">
            <FileText className="w-6 h-6 text-sky-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Weekly Threat Intelligence Report</h3>
            <p className="text-xs text-slate-400 mt-1">
              Includes: executive summary stats, threat category breakdown, source feed attribution, and 30-day ingestion trend. Generated in real time from the PostgreSQL database.
            </p>
          </div>
        </div>

        {/* What's inside */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            '📊 Executive Summary (Total IoCs, New Today, IP, URL)',
            '🎯 Threat Category Distribution table',
            '🛡 Source Feed Attribution (OTX, URLhaus)',
            '📈 Last 10 days of ingestion trend',
            '📅 Timestamped report generation date',
            '🔒 Marked Confidential for professional use',
          ].map((item, i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-2 text-slate-300">
              {item}
            </div>
          ))}
        </div>

        {/* Success / error messages */}
        {success && (
          <div className="flex items-center space-x-2 text-emerald-400 text-sm bg-emerald-500/5 border border-emerald-500/20 rounded-lg px-4 py-3">
            <CheckCircle2 className="w-4 h-4" />
            <span>Report downloaded successfully!</span>
          </div>
        )}
        {error && (
          <div className="flex items-start space-x-2 text-rose-400 text-sm bg-rose-500/5 border border-rose-500/20 rounded-lg px-4 py-3">
            <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Download button */}
        <button
          onClick={downloadReport}
          disabled={loading}
          className="w-full flex items-center justify-center space-x-3 py-3 bg-sky-600 hover:bg-sky-500 text-white font-semibold rounded-xl transition-colors disabled:opacity-40"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Generating Report…</span>
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              <span>Download Weekly Report (PDF)</span>
            </>
          )}
        </button>

        <p className="text-[11px] text-slate-600 text-center">
          Note: If the database is empty (no ingestions yet), the report will show 0s — that is correct, not a bug.
        </p>
      </div>
    </div>
  );
}

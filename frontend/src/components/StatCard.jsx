import React from 'react';

const colorMap = {
  sky:     'text-sky-400    bg-sky-500/10    border-sky-500/25',
  emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
  amber:   'text-amber-400  bg-amber-500/10  border-amber-500/25',
  violet:  'text-violet-400 bg-violet-500/10 border-violet-500/25',
  rose:    'text-rose-400   bg-rose-500/10   border-rose-500/25',
};

export default function StatCard({ icon: Icon, label, value, sub, color = 'sky', loading }) {
  const cls = colorMap[color] ?? colorMap.sky;
  return (
    <div className={`rounded-xl border p-5 bg-[#1E293B] flex items-start space-x-4 ${cls}`}>
      <div className={`p-3 rounded-lg border ${cls} shrink-0`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="min-w-0">
        <p className="text-[11px] font-medium uppercase tracking-wider text-slate-400">{label}</p>
        {loading ? (
          <div className="h-7 w-20 bg-slate-700 animate-pulse rounded mt-1" />
        ) : (
          <p className="text-3xl font-extrabold text-white leading-none mt-1">
            {value ?? '—'}
          </p>
        )}
        {sub && !loading && (
          <p className="text-[11px] text-slate-500 mt-1">{sub}</p>
        )}
      </div>
    </div>
  );
}

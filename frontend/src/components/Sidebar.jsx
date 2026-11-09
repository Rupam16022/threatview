import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldAlert,
  LayoutDashboard,
  Activity,
  Search,
  Radio,
  Bell,
  FileText,
  ChevronRight,
} from 'lucide-react';

const navItems = [
  { to: '/',           icon: LayoutDashboard, label: 'Dashboard'   },
  { to: '/indicators', icon: Activity,        label: 'Indicators'  },
  { to: '/search',     icon: Search,          label: 'IoC Lookup'  },
  { to: '/feeds',      icon: Radio,           label: 'Threat Feeds'},
  { to: '/monitoring', icon: Bell,            label: 'Monitoring'  },
  { to: '/reports',    icon: FileText,        label: 'Reports'     },
];

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 bg-[#020617] border-r border-slate-800 flex flex-col h-screen sticky top-0 z-40">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="p-2 bg-sky-500/10 border border-sky-500/20 rounded-lg">
          <ShieldAlert className="w-5 h-5 text-sky-400" />
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-widest text-white">
            THREAT<span className="text-sky-400">VIEW</span>
          </h1>
          <p className="text-[10px] text-slate-500 font-mono">Threat Intel Platform</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all group ${
                isActive
                  ? 'bg-sky-500/15 text-sky-400 border border-sky-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                  <span>{label}</span>
                </div>
                {isActive && <ChevronRight className="w-3.5 h-3.5 text-sky-500" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer pill */}
      <div className="px-4 py-4 border-t border-slate-800">
        <div className="bg-slate-900 rounded-lg px-3 py-2 text-[10px] font-mono text-slate-500 space-y-0.5">
          <div className="flex justify-between"><span>Sprint</span><span className="text-sky-400">Day 1–2 / 3</span></div>
          <div className="flex justify-between"><span>Backend</span><span className="text-emerald-400">:8000</span></div>
          <div className="flex justify-between"><span>DB</span><span className="text-emerald-400">PostgreSQL</span></div>
        </div>
      </div>
    </aside>
  );
}

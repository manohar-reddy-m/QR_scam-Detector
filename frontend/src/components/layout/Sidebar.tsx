import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, QrCode, Globe } from 'lucide-react';

const nav = [
  { label: 'Overview',    to: '/',        icon: Home,   exact: true },
  { label: 'QR Analysis', to: '/analyze', icon: QrCode              },
  { label: 'URL Intel',   to: '/url',     icon: Globe               },
];

export const Sidebar: React.FC = () => (
  <aside className="w-56 border-r border-navy-800 flex-shrink-0 bg-navy-950 p-4 flex flex-col justify-between">
    <div>
      <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-500 px-3 mb-2 font-mono">
        Navigation
      </div>
      <nav className="space-y-1">
        {nav.map(({ label, to, icon: Icon, exact }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-navy-900 border border-transparent'
              }`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>

    <div className="rounded-lg bg-navy-900/60 border border-navy-800/80 p-3 text-[11px] text-gray-400 space-y-1 font-mono">
      <div className="flex items-center gap-1.5 text-gray-300 font-semibold">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        <span>QR Sentinel v1.0</span>
      </div>
      <p className="text-gray-500 text-[10px]">Zero-open · Safe scanning</p>
    </div>
  </aside>
);

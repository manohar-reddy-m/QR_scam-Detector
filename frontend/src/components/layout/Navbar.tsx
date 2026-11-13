import React from 'react';
import { ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useSystemHealth } from '../../hooks/useSystemHealth';

export const Navbar: React.FC = () => {
  const { isSuccess } = useSystemHealth();

  return (
    <header className="h-14 border-b border-navy-800 bg-navy-950 sticky top-0 z-40 px-5 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-2.5 text-white hover:text-blue-400 transition-colors">
        <ShieldCheck className="w-5 h-5 text-blue-500" />
        <span className="font-semibold text-sm tracking-wide">QR Sentinel</span>
        <span className="text-[10px] font-mono text-gray-500 hidden sm:block">AI Threat Detection</span>
      </Link>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className={`w-2 h-2 rounded-full ${isSuccess ? 'bg-emerald-500' : 'bg-gray-600'}`} />
          <span className={isSuccess ? 'text-emerald-400' : 'text-gray-500'}>
            {isSuccess ? 'Engine Online' : 'Connecting…'}
          </span>
        </div>
        <a
          href="http://localhost:8000/api/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors hidden sm:block"
        >
          API Docs
        </a>
      </div>
    </header>
  );
};

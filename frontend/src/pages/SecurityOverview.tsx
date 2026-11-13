import React from 'react';
import { Link } from 'react-router-dom';
import { QrCode, Globe, ShieldCheck, Zap, Eye, Lock } from 'lucide-react';
import { useSystemHealth } from '../hooks/useSystemHealth';

const features = [
  { icon: <Zap className="w-3.5 h-3.5" />, text: 'Instant decode' },
  { icon: <Eye className="w-3.5 h-3.5" />, text: 'Phishing detection' },
  { icon: <Lock className="w-3.5 h-3.5" />, text: 'Zero auto-fetch' },
];

export const SecurityOverview: React.FC = () => {
  const { data: health } = useSystemHealth();
  const isOnline = health?.status === 'healthy';

  return (
    <div className="flex flex-col items-center justify-center min-h-[72vh] text-center px-4">

      {/* Shield with subtle ring */}
      <div className="relative mb-6">
        <div className="absolute inset-0 rounded-full bg-blue-500/10 blur-2xl scale-150 pointer-events-none" />
        <div className="relative w-16 h-16 rounded-2xl bg-navy-900 border border-blue-500/25 flex items-center justify-center shadow-lg">
          <ShieldCheck className="w-8 h-8 text-blue-400" />
        </div>
        {/* Online dot */}
        <span className={`absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-navy-950 ${isOnline ? 'bg-emerald-500' : 'bg-red-500'}`} />
      </div>

      {/* Title */}
      <h1 className="text-3xl font-bold text-white tracking-tight mb-2">QR Sentinel</h1>
      <p className="text-sm text-gray-400 max-w-xs leading-relaxed mb-8">
        Scan any QR code or paste a link — know if it's safe before you tap.
      </p>

      {/* Action buttons */}
      <div className="flex flex-col sm:flex-row gap-3 mb-10">
        <Link
          to="/analyze"
          className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition-colors shadow-md"
        >
          <QrCode className="w-4 h-4" />
          Scan QR Code
        </Link>
        <Link
          to="/url"
          className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg border border-navy-700 bg-navy-900 hover:bg-navy-800 text-gray-200 text-sm font-medium transition-colors"
        >
          <Globe className="w-4 h-4" />
          Check a Link
        </Link>
      </div>

      {/* Feature pills */}
      <div className="flex flex-wrap justify-center gap-2">
        {features.map(({ icon, text }) => (
          <span
            key={text}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-navy-900 border border-navy-800 text-xs text-gray-400"
          >
            <span className="text-blue-400">{icon}</span>
            {text}
          </span>
        ))}
      </div>

    </div>
  );
};

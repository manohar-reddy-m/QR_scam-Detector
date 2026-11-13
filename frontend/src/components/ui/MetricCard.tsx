import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon?: React.ReactNode;
  color?: 'blue' | 'emerald' | 'amber' | 'rose' | 'purple' | 'cyan';
}

const textColor: Record<string, string> = {
  blue: 'text-blue-400', cyan: 'text-cyan-400', emerald: 'text-emerald-400',
  amber: 'text-amber-400', rose: 'text-rose-400', purple: 'text-purple-400',
};

export const MetricCard: React.FC<MetricCardProps> = ({
  label, value, subtext, icon, color = 'blue',
}) => (
  <div className="bg-navy-900 border border-navy-700 rounded-lg p-4">
    <div className="flex items-center justify-between mb-2">
      <span className="text-xs text-gray-400 uppercase tracking-wider">{label}</span>
      {icon && <span className={`${textColor[color] ?? 'text-blue-400'} opacity-80`}>{icon}</span>}
    </div>
    <div className={`text-xl font-bold font-mono ${textColor[color] ?? 'text-blue-400'}`}>{value}</div>
    {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
  </div>
);

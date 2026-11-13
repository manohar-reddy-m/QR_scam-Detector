import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  glow?: 'blue' | 'cyan' | 'red' | 'emerald' | 'amber' | 'none';
}

export const Card: React.FC<CardProps> = ({ children, className = '', glow = 'none' }) => {
  const borders: Record<string, string> = {
    red:     'border-rose-800/60',
    emerald: 'border-emerald-800/50',
    amber:   'border-amber-800/50',
    blue:    'border-blue-800/50',
    cyan:    'border-cyan-800/50',
    none:    'border-navy-700',
  };
  return (
    <div className={`bg-navy-900 border ${borders[glow] ?? borders.none} rounded-lg p-5 ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}> = ({ title, subtitle, icon, action }) => (
  <div className="flex items-start justify-between gap-4 mb-4 pb-3 border-b border-navy-800">
    <div className="flex items-center gap-2.5">
      {icon && <div className="text-gray-400">{icon}</div>}
      <div>
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        {subtitle && <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>}
      </div>
    </div>
    {action && <div>{action}</div>}
  </div>
);

import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, HelpCircle } from 'lucide-react';
import type { RiskLevel, QRPayloadType } from '../../types';

interface RiskBadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  size = 'md',
  showIcon = true,
}) => {
  const configs = {
    LOW:          { text: 'text-emerald-400', label: 'LOW RISK',      Icon: ShieldCheck   },
    MEDIUM:       { text: 'text-amber-400',   label: 'MEDIUM RISK',   Icon: AlertTriangle },
    HIGH:         { text: 'text-rose-400',    label: 'HIGH RISK',     Icon: AlertOctagon  },
    INCONCLUSIVE: { text: 'text-gray-400',    label: 'INCONCLUSIVE',  Icon: HelpCircle    },
  };

  const cfg = configs[level] ?? configs.INCONCLUSIVE;
  const { Icon } = cfg;

  const szCls = {
    sm: 'text-xs gap-1',
    md: 'text-xs gap-1.5 font-semibold',
    lg: 'text-sm gap-2 font-semibold',
  }[size];

  return (
    <span className={`inline-flex items-center font-mono ${cfg.text} ${szCls}`}>
      {showIcon && <Icon className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />}
      <span>{cfg.label}</span>
    </span>
  );
};

export const PayloadTypeBadge: React.FC<{ type: QRPayloadType }> = ({ type }) => {
  const color: Record<QRPayloadType, string> = {
    URL_HTTPS:   'text-blue-400',
    URL_HTTP:    'text-amber-400',
    UPI_PAYMENT: 'text-purple-400',
    TEXT:        'text-gray-400',
    EMAIL:       'text-cyan-400',
    PHONE:       'text-emerald-400',
    WIFI:        'text-indigo-400',
    VCARD:       'text-teal-400',
    UNKNOWN:     'text-gray-500',
  };

  return (
    <span className={`text-[11px] font-mono bg-navy-800 border border-navy-700 px-2 py-0.5 rounded ${color[type] ?? 'text-gray-500'}`}>
      {type}
    </span>
  );
};

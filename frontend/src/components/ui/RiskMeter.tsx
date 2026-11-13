import React from 'react';
import type { RiskLevel } from '../../types';

interface RiskMeterProps {
  score: number;
  level: RiskLevel;
  size?: number;
  strokeWidth?: number;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({
  score,
  level,
  size = 128,
  strokeWidth = 8,
}) => {
  const pct = Math.round(score * 100);
  const radius = (size - strokeWidth * 2) / 2;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (pct / 100) * circ;

  const colors = {
    LOW:          '#10b981',
    MEDIUM:       '#f59e0b',
    HIGH:         '#f43f5e',
    INCONCLUSIVE: '#6b7280',
  };

  const c = colors[level] ?? colors.INCONCLUSIVE;

  return (
    <div className="flex flex-col items-center">
      <div style={{ width: size, height: size }} className="relative flex items-center justify-center">
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="#1e2638" strokeWidth={strokeWidth} />
          <circle
            cx={size/2} cy={size/2} r={radius}
            fill="none" stroke={c} strokeWidth={strokeWidth}
            strokeDasharray={circ} strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold font-mono" style={{ color: c }}>{pct}%</span>
          <span className="text-[10px] text-gray-500 uppercase tracking-widest mt-0.5">score</span>
        </div>
      </div>
    </div>
  );
};

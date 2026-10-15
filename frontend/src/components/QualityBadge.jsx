import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

export default function QualityBadge({ score = 0, showBar = true, size = 'md' }) {
  const normalized = Math.max(0, Math.min(1, Number(score) || 0));
  const percentage = Math.round(normalized * 100);

  // Quality color mapping:
  // 0 - 0.30: Red
  // 0.30 - 0.60: Yellow
  // 0.60 - 1.0: Green
  let colorTheme = {
    bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    barBg: 'bg-emerald-500',
    glow: 'shadow-[0_0_12px_rgba(16,185,129,0.3)]',
    label: 'High Quality',
    icon: ShieldCheck,
  };

  if (normalized < 0.30) {
    colorTheme = {
      bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
      barBg: 'bg-rose-500',
      glow: 'shadow-[0_0_12px_rgba(244,63,94,0.3)]',
      label: 'Low Trust',
      icon: AlertOctagon,
    };
  } else if (normalized < 0.60) {
    colorTheme = {
      bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
      barBg: 'bg-amber-500',
      glow: 'shadow-[0_0_12px_rgba(245,158,11,0.3)]',
      label: 'Medium Trust',
      icon: AlertTriangle,
    };
  }

  const Icon = colorTheme.icon;

  if (size === 'sm') {
    return (
      <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-xs font-mono font-medium ${colorTheme.bg}`}>
        <Icon className="w-3 h-3" />
        <span>{(normalized).toFixed(2)}</span>
      </div>
    );
  }

  if (size === 'lg') {
    return (
      <div className="flex flex-col gap-1.5 w-full">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <Icon className={`w-4 h-4 ${colorTheme.bg.split(' ')[2]}`} />
            <span className="font-medium text-slate-300">Memory Quality Score</span>
          </div>
          <span className={`font-mono font-bold text-base ${colorTheme.bg.split(' ')[2]}`}>
            {(normalized).toFixed(2)} <span className="text-xs text-slate-400">({percentage}%)</span>
          </span>
        </div>
        {showBar && (
          <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden p-0.5 border border-slate-700/50">
            <div
              className={`h-full rounded-full transition-all duration-500 ${colorTheme.barBg} ${colorTheme.glow}`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-2">
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-mono font-semibold ${colorTheme.bg}`}>
        <Icon className="w-3.5 h-3.5" />
        <span>{(normalized).toFixed(2)}</span>
        <span className="text-[10px] opacity-75">Q-SCORE</span>
      </div>
      {showBar && (
        <div className="w-16 h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
          <div
            className={`h-full rounded-full transition-all duration-300 ${colorTheme.barBg}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}
    </div>
  );
}

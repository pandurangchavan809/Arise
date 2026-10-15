import React from 'react';
import { 
  Clock, 
  Archive, 
  Trash2, 
  Sparkles, 
  Layers, 
  Flame, 
  CalendarClock, 
  ShieldAlert,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import QualityBadge from './QualityBadge';

export const TYPE_CONFIG = {
  session: {
    label: 'Session Memory',
    badgeClass: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    borderClass: 'hover:border-blue-500/50',
    accentColor: 'text-blue-400',
    icon: Clock,
  },
  long_term: {
    label: 'Long-Term Memory',
    badgeClass: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    borderClass: 'hover:border-emerald-500/50',
    accentColor: 'text-emerald-400',
    icon: Layers,
  },
  experience: {
    label: 'Experience (RL)',
    badgeClass: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    borderClass: 'hover:border-amber-500/50',
    accentColor: 'text-amber-400',
    icon: Flame,
  },
  prospective: {
    label: 'Prospective (Action)',
    badgeClass: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
    borderClass: 'hover:border-purple-500/50',
    accentColor: 'text-purple-400',
    icon: CalendarClock,
  },
};

export default function MemoryCard({ memory, onArchive, onForget, showActions = true }) {
  if (!memory) return null;

  const typeConfig = TYPE_CONFIG[memory.type] || TYPE_CONFIG.session;
  const Icon = typeConfig.icon;

  const formattedDate = memory.created_at
    ? new Date(memory.created_at).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : 'Recent';

  const confidencePct = Math.round((memory.confidence || 0.8) * 100);
  const utilityPct = Math.round((memory.utility || 0.8) * 100);

  const isArchived = memory.status === 'archived';
  const isForgotten = memory.status === 'forgotten';

  return (
    <div
      className={`group relative flex flex-col justify-between rounded-xl bg-slate-900/90 border border-slate-800 p-5 shadow-lg backdrop-blur-sm transition-all duration-300 hover:shadow-xl ${typeConfig.borderClass} ${
        isArchived || isForgotten ? 'opacity-65 grayscale-[30%]' : ''
      }`}
    >
      <div>
        {/* Header: Type, Status, Quality */}
        <div className="flex items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border ${typeConfig.badgeClass}`}
            >
              <Icon className="w-3.5 h-3.5" />
              {typeConfig.label}
            </span>

            {/* Status indicator */}
            {memory.status && (
              <span
                className={`text-[11px] px-2 py-0.5 rounded font-mono uppercase tracking-wider ${
                  memory.status === 'active'
                    ? 'bg-slate-800 text-slate-300 border border-slate-700'
                    : memory.status === 'archived'
                    ? 'bg-amber-950/60 text-amber-300 border border-amber-800/60'
                    : 'bg-rose-950/60 text-rose-300 border border-rose-800/60'
                }`}
              >
                {memory.status}
              </span>
            )}

            {/* Risk level if elevated */}
            {memory.risk_level && memory.risk_level !== 'low' && (
              <span className="inline-flex items-center gap-1 text-[10px] text-rose-400 bg-rose-500/10 border border-rose-500/30 px-1.5 py-0.5 rounded font-mono">
                <AlertTriangle className="w-3 h-3" />
                {memory.risk_level.toUpperCase()} RISK
              </span>
            )}
          </div>

          <QualityBadge score={memory.quality_score || (memory.confidence + memory.utility) / 2} size="sm" />
        </div>

        {/* Content */}
        <div className="text-slate-200 text-sm leading-relaxed mb-4 font-normal">
          {memory.content}
        </div>

        {/* Metadata tag / trigger info if prospective */}
        {memory.metadata && Object.keys(memory.metadata).length > 0 && (
          <div className="mb-4 flex flex-wrap gap-1.5">
            {Object.entries(memory.metadata).map(([key, val]) => (
              <span
                key={key}
                className="text-[11px] font-mono bg-slate-950/80 text-slate-400 border border-slate-800 px-2 py-0.5 rounded"
              >
                <span className="text-slate-500">{key}:</span> {String(val)}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Metrics footer & actions */}
      <div className="pt-3 border-t border-slate-800/80">
        <div className="grid grid-cols-2 gap-4 mb-3">
          {/* Confidence */}
          <div>
            <div className="flex justify-between text-[11px] text-slate-400 mb-1">
              <span>Confidence</span>
              <span className="font-mono text-slate-300">{confidencePct}%</span>
            </div>
            <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-800">
              <div
                className="bg-blue-400 h-full rounded-full transition-all duration-300"
                style={{ width: `${confidencePct}%` }}
              />
            </div>
          </div>

          {/* Utility */}
          <div>
            <div className="flex justify-between text-[11px] text-slate-400 mb-1">
              <span>Calibrated Utility</span>
              <span className="font-mono text-slate-300">{utilityPct}%</span>
            </div>
            <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-800">
              <div
                className="bg-amber-400 h-full rounded-full transition-all duration-300"
                style={{ width: `${utilityPct}%` }}
              />
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-500">
          <span className="font-mono">{formattedDate}</span>

          {showActions && (
            <div className="flex items-center gap-1 opacity-90 group-hover:opacity-100 transition-opacity">
              {!isArchived && !isForgotten && onArchive && (
                <button
                  type="button"
                  onClick={() => onArchive(memory.id)}
                  title="Archive memory (suppresses automatic retrieval)"
                  className="flex items-center gap-1 px-2 py-1 rounded text-slate-400 hover:text-amber-300 hover:bg-slate-800 transition-colors"
                >
                  <Archive className="w-3.5 h-3.5" />
                  <span>Archive</span>
                </button>
              )}

              {!isForgotten && onForget && (
                <button
                  type="button"
                  onClick={() => onForget(memory.id)}
                  title="Forget memory (active suppression with retention policy)"
                  className="flex items-center gap-1 px-2 py-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Forget</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

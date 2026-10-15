import React from 'react';
import { X, ShieldCheck, Cpu, Zap, Activity, AlertOctagon, Info, Sparkles } from 'lucide-react';
import QualityBadge from './QualityBadge';
import { TYPE_CONFIG } from './MemoryCard';

export default function MemoryInspector({ isOpen, onClose, memories = [], query = '' }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
      <div 
        className="w-full max-w-xl h-full bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col justify-between overflow-hidden"
      >
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-1 rounded bg-blue-500/10 text-blue-400">
                <ShieldCheck className="w-4 h-4" />
              </span>
              <h3 className="text-lg font-bold text-white">Memory Quality Inspector</h3>
            </div>
            <p className="text-xs text-slate-400">
              Verified {memories.length} memory records injected into agent context
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content list */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {query && (
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs">
              <span className="text-slate-500 font-mono uppercase tracking-wider block mb-1">Context Query</span>
              <p className="text-slate-200 font-medium italic">"{query}"</p>
            </div>
          )}

          {memories.length === 0 ? (
            <div className="text-center py-16 text-slate-500">
              <AlertOctagon className="w-10 h-10 mx-auto mb-3 opacity-40" />
              <p className="text-sm">No memories were injected for this message turn.</p>
              <p className="text-xs text-slate-600 mt-1">The query was answered directly from base reasoning.</p>
            </div>
          ) : (
            memories.map((mem, index) => {
              const typeCfg = TYPE_CONFIG[mem.type] || TYPE_CONFIG.session;
              const TypeIcon = typeCfg.icon;
              const breakdown = mem.breakdown || {
                relevance: mem.relevance || 0.88,
                utility: mem.utility || 0.85,
                confidence: mem.confidence || 0.90,
                recency: mem.recency || 0.80,
                conflict_risk: mem.conflict_risk || 0.05,
              };

              return (
                <div
                  key={mem.id || index}
                  className="rounded-xl bg-slate-950 border border-slate-800 p-5 space-y-4 shadow-sm hover:border-slate-700 transition-colors"
                >
                  {/* Card top */}
                  <div className="flex items-center justify-between gap-2">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${typeCfg.badgeClass}`}>
                      <TypeIcon className="w-3.5 h-3.5" />
                      {typeCfg.label}
                    </span>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                        INCLUDED
                      </span>
                      <QualityBadge score={mem.quality_score || 0.88} size="sm" />
                    </div>
                  </div>

                  {/* Memory text */}
                  <div className="text-sm text-slate-200 leading-relaxed font-normal bg-slate-900/60 p-3 rounded-lg border border-slate-800/80">
                    {mem.content}
                  </div>

                  {/* Quality Breakdown Bars */}
                  <div className="space-y-2.5 pt-2 border-t border-slate-800/80">
                    <div className="flex justify-between items-center text-xs font-semibold text-slate-400">
                      <span>Quality Metrics Breakdown</span>
                      <span className="text-[10px] font-mono text-slate-500">Weight-Calibrated</span>
                    </div>

                    {/* Relevance */}
                    <div>
                      <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                        <span>Relevance (Semantic Match)</span>
                        <span className="font-mono text-slate-300">{Math.round(breakdown.relevance * 100)}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="bg-blue-400 h-full rounded-full" style={{ width: `${breakdown.relevance * 100}%` }} />
                      </div>
                    </div>

                    {/* Utility */}
                    <div>
                      <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                        <span>Historical Utility (Outcome RL)</span>
                        <span className="font-mono text-slate-300">{Math.round(breakdown.utility * 100)}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="bg-amber-400 h-full rounded-full" style={{ width: `${breakdown.utility * 100}%` }} />
                      </div>
                    </div>

                    {/* Confidence */}
                    <div>
                      <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                        <span>Confidence (Source Reliability)</span>
                        <span className="font-mono text-slate-300">{Math.round(breakdown.confidence * 100)}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${breakdown.confidence * 100}%` }} />
                      </div>
                    </div>

                    {/* Conflict Risk */}
                    <div>
                      <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                        <span>Contradiction / Conflict Risk</span>
                        <span className="font-mono text-slate-300">{Math.round(breakdown.conflict_risk * 100)}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="bg-rose-400 h-full rounded-full" style={{ width: `${breakdown.conflict_risk * 100}%` }} />
                      </div>
                    </div>
                  </div>

                  {/* Token budget cost */}
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                    <span>Context Cost: ~{mem.tokens || Math.ceil(mem.content.length / 4)} tokens</span>
                    <span>ID: {mem.id}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1.5">
            <Zap className="w-4 h-4 text-emerald-400" />
            <span>Edge Budgeting Active (Zero Context Bloat)</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

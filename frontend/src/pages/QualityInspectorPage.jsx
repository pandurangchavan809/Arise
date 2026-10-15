import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Search, 
  Sparkles, 
  AlertTriangle, 
  SlidersHorizontal, 
  Zap, 
  CheckCircle2, 
  XCircle, 
  ArrowRight, 
  Cpu,
  Layers,
  Info
} from 'lucide-react';
import { api } from '../api/client';
import QualityBadge from '../components/QualityBadge';
import { TYPE_CONFIG } from '../components/MemoryCard';

export default function QualityInspectorPage() {
  const [query, setQuery] = useState('Python architecture guidelines and PDF handling');
  const [loading, setLoading] = useState(false);
  const [maxTokens, setMaxTokens] = useState(400);
  const [recallData, setRecallData] = useState(null);

  const sampleQueries = [
    'Python architecture guidelines and PDF handling',
    'PostgreSQL pgvector cluster configuration',
    'SQLite migration details and deprecated storage',
    'Trigger distillation when session context reaches limit',
  ];

  const runRecallTest = async (testQuery = query) => {
    if (!testQuery.trim() || loading) return;
    setLoading(true);
    try {
      const data = await api.recall(testQuery, 'usr_default', { max_tokens: maxTokens });
      setRecallData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runRecallTest();
  }, []);

  const selectedList = recallData?.selected_memories || [];
  const suppressedList = recallData?.suppressed_memories || [];
  const budget = recallData?.budget || {
    total_allowed_tokens: maxTokens,
    tokens_used: 0,
    count_selected: 0,
    count_candidates: 0,
  };

  const budgetPercentage = Math.min(100, Math.round((budget.tokens_used / (budget.total_allowed_tokens || 1)) * 100));

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1 rounded bg-blue-500/10 text-blue-400">
              <ShieldCheck className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold text-white tracking-tight">Memory Quality Inspector (MQM)</h1>
          </div>
          <p className="text-sm text-slate-400">
            Real-time recall testing, utility scoring, and edge token budget enforcement.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg">
          <Zap className="w-4 h-4" />
          <span>Active Edge Guard: No Prompt Stuffing</span>
        </div>
      </div>

      {/* Query Testing Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <label className="text-sm font-semibold text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Search className="w-4 h-4 text-blue-400" />
            Simulate Agent Recall Query
          </span>
          <span className="text-xs font-mono text-slate-500">
            Test how memories are scored and filtered
          </span>
        </label>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            runRecallTest();
          }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a scenario, agent prompt, or query to test retrieval..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-normal"
          />

          <div className="flex items-center gap-2">
            <div className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 flex items-center gap-2 text-xs text-slate-400 font-mono">
              <span>Token Budget:</span>
              <select
                value={maxTokens}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  setMaxTokens(val);
                }}
                className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="250">250 tokens</option>
                <option value="400">400 tokens</option>
                <option value="800">800 tokens</option>
                <option value="1500">1500 tokens</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition-all shadow-md shadow-blue-600/20 disabled:opacity-50 whitespace-nowrap"
            >
              {loading ? 'Evaluating...' : 'Evaluate Recall'}
            </button>
          </div>
        </form>

        {/* Quick sample chips */}
        <div className="flex flex-wrap items-center gap-2 pt-2">
          <span className="text-[11px] font-mono text-slate-500">Presets:</span>
          {sampleQueries.map((sample, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setQuery(sample);
                runRecallTest(sample);
              }}
              className="text-xs font-mono bg-slate-950 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 px-2.5 py-1 rounded-lg transition-colors"
            >
              {sample}
            </button>
          ))}
        </div>
      </div>

      {/* Budget & Decision Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Token Budget Meter */}
        <div className="md:col-span-2 p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span className="font-medium flex items-center gap-1.5">
                <Zap className="w-4 h-4 text-emerald-400" />
                Edge Token Budget Consumption
              </span>
              <span className="font-mono text-slate-200">
                {budget.tokens_used} / {budget.total_allowed_tokens} Tokens ({budgetPercentage}%)
              </span>
            </div>
            <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  budgetPercentage > 90
                    ? 'bg-amber-500 shadow-[0_0_12px_rgba(245,158,11,0.5)]'
                    : 'bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.5)]'
                }`}
                style={{ width: `${budgetPercentage}%` }}
              />
            </div>
          </div>
          <div className="text-[11px] text-slate-500 mt-3 flex items-center justify-between font-mono">
            <span>Enforced ceiling: {budget.total_allowed_tokens} tokens</span>
            <span>Eliminated context pollution</span>
          </div>
        </div>

        {/* Selected count */}
        <div className="p-5 rounded-xl bg-slate-900 border border-emerald-500/30 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-mono">Trusted for Injection</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400 font-mono">{selectedList.length}</div>
          <div className="text-[11px] text-emerald-400/80 font-mono mt-1">High utility & low conflict</div>
        </div>

        {/* Suppressed count */}
        <div className="p-5 rounded-xl bg-slate-900 border border-rose-500/30 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 font-mono">Safely Suppressed</span>
            <span className="w-2 h-2 rounded-full bg-rose-400" />
          </div>
          <div className="text-3xl font-extrabold text-rose-400 font-mono">{suppressedList.length}</div>
          <div className="text-[11px] text-rose-400/80 font-mono mt-1">Below trust threshold or over budget</div>
        </div>
      </div>

      {/* Side-by-Side: Selected vs Suppressed Memories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        
        {/* Left Column: SELECTED / INCLUDED */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-emerald-500/30">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <h3 className="font-bold text-white text-base">Selected Memories (Context Injected)</h3>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              {selectedList.length} INCLUDED
            </span>
          </div>

          {selectedList.length === 0 ? (
            <div className="p-8 rounded-xl bg-slate-900/40 border border-dashed border-slate-800 text-center text-slate-500 text-xs">
              No memories met the strict quality threshold for this prompt query.
            </div>
          ) : (
            selectedList.map((mem) => {
              const typeCfg = TYPE_CONFIG[mem.type] || TYPE_CONFIG.session;
              const TypeIcon = typeCfg.icon;
              const bd = mem.breakdown || {
                relevance: 0.9,
                utility: 0.85,
                confidence: 0.9,
                recency: 0.8,
                conflict_risk: 0.05,
              };

              return (
                <div
                  key={mem.id}
                  className="rounded-xl bg-slate-900 border-2 border-emerald-500/30 p-5 space-y-4 shadow-lg hover:border-emerald-500/60 transition-all"
                >
                  {/* Header */}
                  <div className="flex items-center justify-between">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${typeCfg.badgeClass}`}>
                      <TypeIcon className="w-3.5 h-3.5" />
                      {typeCfg.label}
                    </span>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">
                        INCLUDED
                      </span>
                      <QualityBadge score={mem.quality_score} size="sm" />
                    </div>
                  </div>

                  {/* Content */}
                  <div className="text-sm text-slate-200 leading-relaxed font-normal bg-slate-950 p-3 rounded-lg border border-slate-800">
                    {mem.content}
                  </div>

                  {/* Quality Breakdown Bars */}
                  <div className="space-y-2 bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>Relevance:</span>
                      <span className="font-mono text-slate-200">{Math.round(bd.relevance * 100)}%</span>
                    </div>
                    <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                      <div className="bg-blue-400 h-full" style={{ width: `${bd.relevance * 100}%` }} />
                    </div>

                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>Utility (Outcome RL):</span>
                      <span className="font-mono text-slate-200">{Math.round(bd.utility * 100)}%</span>
                    </div>
                    <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                      <div className="bg-amber-400 h-full" style={{ width: `${bd.utility * 100}%` }} />
                    </div>

                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>Confidence:</span>
                      <span className="font-mono text-slate-200">{Math.round(bd.confidence * 100)}%</span>
                    </div>
                    <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                      <div className="bg-emerald-400 h-full" style={{ width: `${bd.confidence * 100}%` }} />
                    </div>

                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>Conflict Risk:</span>
                      <span className="font-mono text-emerald-400">{Math.round(bd.conflict_risk * 100)}% (Safe)</span>
                    </div>
                    <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                      <div className="bg-rose-400 h-full" style={{ width: `${bd.conflict_risk * 100}%` }} />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-1">
                    <span>Context Cost: ~{mem.tokens} tokens</span>
                    <span>ID: {mem.id}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: SUPPRESSED */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-rose-500/30">
            <div className="flex items-center gap-2">
              <XCircle className="w-5 h-5 text-rose-400" />
              <h3 className="font-bold text-white text-base">Suppressed Candidates (Blocked)</h3>
            </div>
            <span className="text-xs font-mono text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
              {suppressedList.length} SUPPRESSED
            </span>
          </div>

          {suppressedList.length === 0 ? (
            <div className="p-8 rounded-xl bg-slate-900/40 border border-dashed border-slate-800 text-center text-slate-500 text-xs">
              Zero candidates suppressed. All retrieved records fit within budget and passed trust thresholds.
            </div>
          ) : (
            suppressedList.map((mem) => {
              const typeCfg = TYPE_CONFIG[mem.type] || TYPE_CONFIG.session;
              const TypeIcon = typeCfg.icon;
              const bd = mem.breakdown || {
                relevance: 0.4,
                utility: 0.3,
                confidence: 0.6,
                recency: 0.5,
                conflict_risk: 0.6,
              };

              return (
                <div
                  key={mem.id}
                  className="rounded-xl bg-slate-900/60 border border-rose-500/20 p-5 space-y-4 shadow-sm opacity-80 hover:opacity-100 transition-opacity"
                >
                  {/* Header */}
                  <div className="flex items-center justify-between">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${typeCfg.badgeClass}`}>
                      <TypeIcon className="w-3.5 h-3.5" />
                      {typeCfg.label}
                    </span>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 font-bold">
                        SUPPRESSED
                      </span>
                      <QualityBadge score={mem.quality_score} size="sm" />
                    </div>
                  </div>

                  {/* Suppression reason callout */}
                  <div className="flex items-center gap-2 p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
                    <AlertTriangle className="w-4 h-4 shrink-0" />
                    <span className="font-medium">Suppression Reason: {mem.reason || 'Failed quality threshold'}</span>
                  </div>

                  {/* Content */}
                  <div className="text-sm text-slate-300 leading-relaxed font-normal bg-slate-950 p-3 rounded-lg border border-slate-800">
                    {mem.content}
                  </div>

                  {/* Conflict / Risk callout */}
                  <div className="space-y-2 bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 text-[11px] text-slate-400">
                    <div className="flex justify-between">
                      <span>Conflict Risk Factor:</span>
                      <span className="font-mono text-rose-400">{Math.round(bd.conflict_risk * 100)}%</span>
                    </div>
                    <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                      <div className="bg-rose-500 h-full" style={{ width: `${bd.conflict_risk * 100}%` }} />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-1">
                    <span>Potential token penalty: ~{mem.tokens} tokens</span>
                    <span>ID: {mem.id}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

      </div>

    </div>
  );
}

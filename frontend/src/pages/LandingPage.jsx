import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Brain, 
  ArrowRight, 
  BookOpen, 
  Database, 
  CheckCircle2, 
  Sparkles, 
  Zap, 
  SlidersHorizontal, 
  Search, 
  Cpu, 
  Layers, 
  Clock, 
  Flame, 
  CalendarClock, 
  ShieldCheck, 
  Workflow,
  Radio,
  FileCode2,
  Terminal,
  Server
} from 'lucide-react';
import ArchitectureDiagram from '../components/ArchitectureDiagram';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-600 selection:text-white">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
              <Brain className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white flex items-center gap-2">
                Adaptive Memory Runtime
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                  v1.2
                </span>
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
            <a href="#architecture" className="hover:text-blue-400 transition-colors">Architecture</a>
            <a href="#pillars" className="hover:text-blue-400 transition-colors">Four Pillars</a>
            <a href="#memory-types" className="hover:text-blue-400 transition-colors">Memory Topology</a>
            <a href="#integrations" className="hover:text-blue-400 transition-colors">Integrations</a>
            <Link to="/app/developer" className="hover:text-blue-400 transition-colors flex items-center gap-1">
              <FileCode2 className="w-4 h-4" />
              Docs & SDK
            </Link>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              to="/app/assistant"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-all shadow-md shadow-blue-600/20 hover:shadow-blue-600/40"
            >
              <span>Launch Demo</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-16 lg:pt-28 lg:pb-24 overflow-hidden">
        {/* Subtle radial background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-gradient-to-tr from-blue-600/15 via-indigo-600/10 to-transparent blur-3xl pointer-events-none -z-10" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          
          {/* Eyebrow badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300 text-xs sm:text-sm font-mono mb-6 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-400">Memory Runtime IS the Product</span>
            <span className="text-slate-600">|</span>
            <span className="text-blue-400 font-semibold">Zero Prompt Bloat</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white mb-6 leading-[1.1]">
            Adaptive Memory Runtime
          </h1>

          {/* Subtitle */}
          <p className="text-xl sm:text-2xl font-medium text-blue-400 mb-6">
            Plug-and-play memory intelligence for AI agents.
          </p>

          {/* Main message statement */}
          <p className="text-base sm:text-lg text-slate-300 max-w-3xl mx-auto leading-relaxed mb-10">
            Remember what matters. Retrieve what is useful. Forget what is not. Run locally or connect to any model.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/app/assistant"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-base transition-all shadow-lg shadow-blue-600/30 hover:scale-[1.02]"
            >
              <span>Try the Demo</span>
              <ArrowRight className="w-5 h-5" />
            </Link>

            <Link
              to="/app/developer"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-medium text-base transition-all hover:scale-[1.02]"
            >
              <BookOpen className="w-5 h-5 text-slate-400" />
              <span>View Documentation</span>
            </Link>
          </div>

          {/* Key Metric Highlights */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-slate-800/80 pt-10 text-left">
            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/60">
              <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono">99.4%</div>
              <div className="text-xs text-slate-400 mt-1">Context Precision Rate</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/60">
              <div className="text-2xl sm:text-3xl font-extrabold text-emerald-400 font-mono">-65%</div>
              <div className="text-xs text-slate-400 mt-1">Token Context Overhead</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/60">
              <div className="text-2xl sm:text-3xl font-extrabold text-blue-400 font-mono">&lt; 20ms</div>
              <div className="text-xs text-slate-400 mt-1">MQM Evaluation Latency</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/60">
              <div className="text-2xl sm:text-3xl font-extrabold text-purple-400 font-mono">100%</div>
              <div className="text-xs text-slate-400 mt-1">Model & Cloud Agnostic</div>
            </div>
          </div>
        </div>
      </section>

      {/* Prominent Architecture Diagram Section */}
      <section id="architecture" className="py-16 sm:py-24 bg-slate-950/60 border-t border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-xs sm:text-sm font-mono uppercase tracking-widest text-blue-400 mb-2">
              End-to-End System Topology
            </h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white">
              The Architecture Behind Adaptive Memory
            </p>
            <p className="text-slate-400 mt-3 text-sm sm:text-base">
              Decoupling memory evaluation and edge budgeting from LLM reasoning produces hallucination-free, high-speed agent pipelines.
            </p>
          </div>

          {/* Architecture Visual Component */}
          <ArchitectureDiagram />
        </div>
      </section>

      {/* Four Pillars Section */}
      <section id="pillars" className="py-20 sm:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs sm:text-sm font-mono uppercase tracking-widest text-indigo-400 mb-2">
              Operational Fundamentals
            </h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white">
              The Four Pillars of Memory Intelligence
            </p>
            <p className="text-slate-400 mt-3 text-sm sm:text-base">
              Traditional vector databases dump everything into context. The Adaptive Memory Runtime behaves like a living cognitive substrate.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Pillar 1: REMEMBER */}
            <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 flex flex-col justify-between hover:border-blue-500/50 transition-all group">
              <div>
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <Database className="w-6 h-6" />
                </div>
                <div className="text-xs font-mono font-bold text-blue-400 tracking-wider uppercase mb-1">Pillar 1</div>
                <h3 className="text-xl font-bold text-white mb-2">1. REMEMBER</h3>
                <p className="text-xs text-blue-300/80 font-mono mb-3">Store the right information</p>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Extracts structured entities, operational constraints, and conversational intent without hoarding noisy chat turns. Automatically segments into appropriate memory tiers.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] font-mono text-slate-500">
                • Intent distillation • Schema inference
              </div>
            </div>

            {/* Pillar 2: RETRIEVE */}
            <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 flex flex-col justify-between hover:border-emerald-500/50 transition-all group">
              <div>
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <Search className="w-6 h-6" />
                </div>
                <div className="text-xs font-mono font-bold text-emerald-400 tracking-wider uppercase mb-1">Pillar 2</div>
                <h3 className="text-xl font-bold text-white mb-2">2. RETRIEVE</h3>
                <p className="text-xs text-emerald-300/80 font-mono mb-3">Find possible memories</p>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Hybrid vector similarity search combined with graph traversal and time-decay curves to surface relevant candidate candidates across all 4 memory stores in milliseconds.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] font-mono text-slate-500">
                • pgvector / ANN • Temporal decay
              </div>
            </div>

            {/* Pillar 3: EVALUATE */}
            <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 flex flex-col justify-between hover:border-amber-500/50 transition-all group">
              <div>
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div className="text-xs font-mono font-bold text-amber-400 tracking-wider uppercase mb-1">Pillar 3</div>
                <h3 className="text-xl font-bold text-white mb-2">3. EVALUATE</h3>
                <p className="text-xs text-amber-300/80 font-mono mb-3">Decide which deserve trust</p>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Memory Quality Manager scores candidate utility, source reliability, and contradiction risk. Suppresses outdated or conflicting facts before they reach the model.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] font-mono text-slate-500">
                • Conflict suppression • Trust thresholding
              </div>
            </div>

            {/* Pillar 4: LEARN */}
            <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 flex flex-col justify-between hover:border-purple-500/50 transition-all group">
              <div>
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <SlidersHorizontal className="w-6 h-6" />
                </div>
                <div className="text-xs font-mono font-bold text-purple-400 tracking-wider uppercase mb-1">Pillar 4</div>
                <h3 className="text-xl font-bold text-white mb-2">4. LEARN</h3>
                <p className="text-xs text-purple-300/80 font-mono mb-3">Reinforce from outcomes</p>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Closed-loop reinforcement. Successful task completions boost memory utility scores; errors trigger downweighting and graceful forgetting curves.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] font-mono text-slate-500">
                • Utility reinforcement • Ebbinghaus forgetting
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Memory Types Section */}
      <section id="memory-types" className="py-20 bg-slate-900/40 border-t border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs sm:text-sm font-mono uppercase tracking-widest text-emerald-400 mb-2">
              Cognitive Architecture
            </h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white">
              The 4 Distinct Memory Tiers
            </p>
            <p className="text-slate-400 mt-3 text-sm sm:text-base">
              No single vector index fits all cognitive needs. The runtime segregates storage to guarantee zero cross-contamination.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Type 1: Session */}
            <div className="p-6 rounded-2xl bg-slate-950/80 border border-blue-500/30 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      <Clock className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-white">Session Memory</h4>
                      <span className="text-xs text-blue-400 font-mono">Working / Ephemeral Memory</span>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                    TTL: Current Conversation
                  </span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed mb-4">
                  Captures active variables, turn-by-turn dialogue dependencies, and temporary agent state. Automatically pruned when the session closes.
                </p>
              </div>
              <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 font-mono text-xs text-slate-400">
                <span className="text-blue-400 font-semibold block mb-1">Concrete Example:</span>
                "User currently debugging a 504 Gateway Timeout on checkout API using port 8080."
              </div>
            </div>

            {/* Type 2: Long-Term */}
            <div className="p-6 rounded-2xl bg-slate-950/80 border border-emerald-500/30 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <Layers className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-white">Long-Term Memory</h4>
                      <span className="text-xs text-emerald-400 font-mono">Declarative / Semantic Facts</span>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                    TTL: Persistent (Decay-Protected)
                  </span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed mb-4">
                  Stores user profiles, system policies, permanent entity definitions, and developer conventions across multi-week interactions.
                </p>
              </div>
              <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 font-mono text-xs text-slate-400">
                <span className="text-emerald-400 font-semibold block mb-1">Concrete Example:</span>
                "Organization enforces strict HIPAA data isolation; never write unmasked patient IDs to logs."
              </div>
            </div>

            {/* Type 3: Experience */}
            <div className="p-6 rounded-2xl bg-slate-950/80 border border-amber-500/30 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      <Flame className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-white">Experience Memory</h4>
                      <span className="text-xs text-amber-400 font-mono">Procedural / Reinforcement Outcomes</span>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                    TTL: Dynamic Reinforcement
                  </span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed mb-4">
                  Records tool executions and operational outcomes. If a specific SQL query pattern caused a lock contention, this memory suppresses repeated mistakes.
                </p>
              </div>
              <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 font-mono text-xs text-slate-400">
                <span className="text-amber-400 font-semibold block mb-1">Concrete Example:</span>
                "Previous CSV export exceeded 50MB and crashed node process; use streaming writer instead."
              </div>
            </div>

            {/* Type 4: Prospective */}
            <div className="p-6 rounded-2xl bg-slate-950/80 border border-purple-500/30 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                      <CalendarClock className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-white">Prospective Memory</h4>
                      <span className="text-xs text-purple-400 font-mono">Conditional / Actionable Intent</span>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                    TTL: Condition-Triggered
                  </span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed mb-4">
                  Autonomous intentions and deferred triggers. Wakes up the agent when specific semantic, temporal, or operational criteria are met.
                </p>
              </div>
              <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 font-mono text-xs text-slate-400">
                <span className="text-purple-400 font-semibold block mb-1">Concrete Example:</span>
                "TRIGGER: When user mentions deployment to production, mandate manual confirmation of API secrets."
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section id="integrations" className="py-20 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-3xl mx-auto mb-12">
            <h2 className="text-xs sm:text-sm font-mono uppercase tracking-widest text-blue-400 mb-2">
              Pluggable Ecosystem
            </h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white">
              Works With Any Model, Search, or Voice Provider
            </p>
            <p className="text-slate-400 mt-3 text-sm sm:text-base">
              The Adaptive Memory Runtime does not lock you into any proprietary model or vendor cloud. Swap providers with one config line.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center">
              <span className="text-xs font-mono text-slate-500 mb-2">Local SLM</span>
              <span className="font-bold text-sm text-slate-200">Ollama / Llama 3</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center">
              <span className="text-xs font-mono text-slate-500 mb-2">Cloud LLM</span>
              <span className="font-bold text-sm text-slate-200">Google Gemini</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center">
              <span className="text-xs font-mono text-slate-500 mb-2">Reasoning LLM</span>
              <span className="font-bold text-sm text-slate-200">Claude 3.5 Sonnet</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center">
              <span className="text-xs font-mono text-slate-500 mb-2">Proprietary</span>
              <span className="font-bold text-sm text-slate-200">OpenAI GPT-4o</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center">
              <span className="text-xs font-mono text-slate-500 mb-2">Vector Backend</span>
              <span className="font-bold text-sm text-slate-200">pgvector / PostgreSQL</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center">
              <span className="text-xs font-mono text-slate-500 mb-2">Live Search</span>
              <span className="font-bold text-sm text-slate-200">Brave / Tavily / Serper</span>
            </div>
          </div>

          {/* Banner */}
          <div className="mt-12 p-8 rounded-2xl bg-gradient-to-r from-blue-900/20 via-indigo-900/20 to-purple-900/20 border border-blue-500/30 max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="text-left">
              <h4 className="text-lg font-bold text-white">Ready to embed in your agent stack?</h4>
              <p className="text-xs sm:text-sm text-slate-300 mt-1">
                Install via pip, wrap your prompt loop with 3 lines of code, and eliminate hallucinations.
              </p>
            </div>
            <Link
              to="/app/assistant"
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm whitespace-nowrap shadow-md shadow-blue-600/30"
            >
              Launch Interactive Console →
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-12 bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6 text-center sm:text-left">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white">
              <Brain className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-sm text-white">Adaptive Memory Runtime</span>
              <p className="text-xs text-slate-500">Autonomous cognitive layer for AI agent swarms.</p>
            </div>
          </div>

          <p className="text-xs font-mono text-slate-400">
            The Memory Runtime is the product. Everything else is a replaceable integration.
          </p>

          <div className="flex items-center gap-4 text-xs text-slate-400">
            <Link to="/app/developer" className="hover:text-white transition-colors">Documentation</Link>
            <Link to="/app/assistant" className="hover:text-white transition-colors">Live Demo</Link>
            <Link to="/app/quality" className="hover:text-white transition-colors">Quality Inspector</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

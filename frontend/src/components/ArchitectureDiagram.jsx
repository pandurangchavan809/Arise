import React, { useState } from 'react';
import { 
  MessageSquare, 
  Mic, 
  Terminal, 
  SlidersHorizontal, 
  Brain, 
  Zap, 
  ShieldCheck, 
  Cpu, 
  ArrowRight, 
  Layers, 
  Clock, 
  Flame, 
  CalendarClock,
  Sparkles,
  Info
} from 'lucide-react';

export default function ArchitectureDiagram({ interactive = true }) {
  const [activeStep, setActiveStep] = useState(null);

  const stepsInfo = {
    inputs: {
      title: 'Interchangeable Input Interfaces',
      desc: 'Chat UIs, Voice speech-to-text, or Python SDK streams send agent events & prompts into the runtime.',
    },
    mqm: {
      title: 'Memory Quality Manager (MQM)',
      desc: 'The central intelligence engine that scores relevance, historical utility, confidence calibration, and conflict risk.',
    },
    stores: {
      title: 'Decoupled 4-Tier Memory Topology',
      desc: 'Session (ephemeral), Long-Term (semantic facts), Experience (reinforcement outcomes), and Prospective (conditional triggers).',
    },
    edge: {
      title: 'Edge Budgeting & Pruning',
      desc: 'Hard token limits enforce dynamic pruning so only the highest ROI memories make it into the prompt context.',
    },
    trusted: {
      title: 'Small Trusted Context Window',
      desc: 'A laser-focused, verified context block (300-800 tokens) that eliminates hallucination without context stuffing.',
    },
    llm: {
      title: 'Any LLM / SLM / Model Provider',
      desc: 'Deploy locally on Ollama/Llama-3, or route to Gemini, Claude, or OpenAI. The runtime is model-agnostic.',
    },
  };

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800/80 rounded-2xl p-6 sm:p-8 backdrop-blur-md shadow-2xl relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute -top-24 -left-24 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800 mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-mono uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            Core Runtime Architecture
          </div>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            The Adaptive Memory Runtime Pipeline
          </h3>
          <p className="text-sm text-slate-400 mt-1">
            Memory Runtime <span className="text-blue-400 font-semibold">IS the product</span>. Chat, voice, and models are swappable interfaces.
          </p>
        </div>

        {interactive && (
          <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800 self-start sm:self-auto">
            <Info className="w-3.5 h-3.5 text-blue-400" />
            <span>Hover blocks to inspect pipeline mechanics</span>
          </div>
        )}
      </div>

      {/* Main Flow Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-3 items-stretch relative">
        
        {/* Step 1: Input interfaces (Col 1-2) */}
        <div 
          onMouseEnter={() => setActiveStep('inputs')}
          onMouseLeave={() => setActiveStep(null)}
          className={`lg:col-span-2 rounded-xl bg-slate-950/70 border border-slate-800 p-4 flex flex-col justify-between transition-all duration-300 hover:border-blue-500/50 hover:bg-slate-950 ${
            activeStep === 'inputs' ? 'ring-2 ring-blue-500/50 bg-slate-950' : ''
          }`}
        >
          <div>
            <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-3">1. Interface Tier</div>
            <div className="space-y-2">
              <div className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-200">
                <MessageSquare className="w-4 h-4 text-blue-400" />
                <span className="font-medium">Chat Stream</span>
              </div>
              <div className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-200">
                <Mic className="w-4 h-4 text-emerald-400" />
                <span className="font-medium">Voice STT</span>
              </div>
              <div className="flex items-center gap-2.5 p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-200">
                <Terminal className="w-4 h-4 text-purple-400" />
                <span className="font-medium">Python SDK</span>
              </div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 font-mono">
            Demoware Layer
          </div>
        </div>

        {/* Transition arrow 1 */}
        <div className="hidden lg:flex items-center justify-center lg:col-span-1">
          <div className="w-full flex items-center justify-center">
            <div className="h-0.5 flex-1 bg-gradient-to-r from-blue-500/40 to-indigo-500/60" />
            <ArrowRight className="w-5 h-5 text-indigo-400 animate-pulse -ml-1" />
          </div>
        </div>

        {/* Step 2 & 3: Runtime Core Engine (Col 4-8) */}
        <div className="lg:col-span-5 rounded-xl bg-gradient-to-b from-blue-950/20 to-slate-950/80 border-2 border-blue-500/40 p-4 sm:p-5 relative shadow-[0_0_30px_rgba(59,130,246,0.15)] flex flex-col justify-between">
          <div className="absolute -top-3 left-4 bg-blue-600 text-white font-mono text-[10px] font-bold px-2.5 py-0.5 rounded-full tracking-wider uppercase shadow-md flex items-center gap-1.5">
            <Brain className="w-3 h-3" />
            Adaptive Memory Runtime (THE PRODUCT)
          </div>

          <div>
            {/* MQM Sub-block */}
            <div
              onMouseEnter={() => setActiveStep('mqm')}
              onMouseLeave={() => setActiveStep(null)}
              className={`rounded-lg bg-slate-900/90 border border-blue-500/30 p-3 mb-3.5 transition-all duration-300 hover:border-blue-400 ${
                activeStep === 'mqm' ? 'ring-2 ring-blue-400 bg-slate-800/80' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <SlidersHorizontal className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-bold text-white tracking-wide">Memory Quality Manager</span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  RL-Calibrated
                </span>
              </div>
              <div className="grid grid-cols-4 gap-1.5 text-center text-[10px] font-mono text-slate-300">
                <div className="bg-slate-950/80 p-1 rounded border border-slate-800">Relevance</div>
                <div className="bg-slate-950/80 p-1 rounded border border-slate-800">Utility</div>
                <div className="bg-slate-950/80 p-1 rounded border border-slate-800">Confidence</div>
                <div className="bg-slate-950/80 p-1 rounded border border-slate-800">Risk Check</div>
              </div>
            </div>

            {/* 4 Memory Stores Sub-block */}
            <div
              onMouseEnter={() => setActiveStep('stores')}
              onMouseLeave={() => setActiveStep(null)}
              className={`rounded-lg bg-slate-900/70 border border-slate-800 p-3 mb-3.5 transition-all duration-300 hover:border-indigo-400 ${
                activeStep === 'stores' ? 'ring-2 ring-indigo-400 bg-slate-800/80' : ''
              }`}
            >
              <div className="text-[11px] font-semibold text-slate-300 mb-2 flex items-center justify-between">
                <span>Decoupled Memory Stores</span>
                <span className="text-[10px] font-mono text-slate-500">Vector + Graph + Relational</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-1.5 p-1.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-300">
                  <Clock className="w-3.5 h-3.5" />
                  <span className="font-medium text-[11px]">1. Session</span>
                </div>
                <div className="flex items-center gap-1.5 p-1.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                  <Layers className="w-3.5 h-3.5" />
                  <span className="font-medium text-[11px]">2. Long-Term</span>
                </div>
                <div className="flex items-center gap-1.5 p-1.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300">
                  <Flame className="w-3.5 h-3.5" />
                  <span className="font-medium text-[11px]">3. Experience</span>
                </div>
                <div className="flex items-center gap-1.5 p-1.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-300">
                  <CalendarClock className="w-3.5 h-3.5" />
                  <span className="font-medium text-[11px]">4. Prospective</span>
                </div>
              </div>
            </div>

            {/* Edge Budgeting */}
            <div
              onMouseEnter={() => setActiveStep('edge')}
              onMouseLeave={() => setActiveStep(null)}
              className={`rounded-lg bg-slate-950/80 border border-slate-800 p-2.5 flex items-center justify-between transition-all duration-300 hover:border-emerald-500/50 ${
                activeStep === 'edge' ? 'ring-2 ring-emerald-500/50 bg-slate-900' : ''
              }`}
            >
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-semibold text-slate-200">Edge Token Budgeter</span>
              </div>
              <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                Max 400 - 1,024 Tokens
              </span>
            </div>
          </div>

          <div className="mt-3 pt-2 text-[10px] font-mono text-center text-blue-400/80">
            Self-Supervised Retention & Forgetting Loop
          </div>
        </div>

        {/* Transition arrow 2 */}
        <div className="hidden lg:flex items-center justify-center lg:col-span-1">
          <div className="w-full flex items-center justify-center">
            <div className="h-0.5 flex-1 bg-gradient-to-r from-indigo-500/60 to-emerald-500/60" />
            <ArrowRight className="w-5 h-5 text-emerald-400 animate-pulse -ml-1" />
          </div>
        </div>

        {/* Step 4 & 5: Context & Model Target (Col 10-12) */}
        <div className="lg:col-span-3 space-y-3 flex flex-col justify-between">
          {/* Small Trusted Context Block */}
          <div
            onMouseEnter={() => setActiveStep('trusted')}
            onMouseLeave={() => setActiveStep(null)}
            className={`rounded-xl bg-slate-950/70 border border-emerald-500/30 p-4 transition-all duration-300 hover:border-emerald-400 hover:bg-slate-950 ${
              activeStep === 'trusted' ? 'ring-2 ring-emerald-500/50 bg-slate-950' : ''
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">Small Trusted Context</span>
            </div>
            <p className="text-[11px] text-slate-400 mb-2 leading-relaxed">
              Zero noise, no hallucination prompts. High-utility facts only.
            </p>
            <div className="p-2 rounded bg-emerald-500/5 border border-emerald-500/20 font-mono text-[10px] text-emerald-300">
              ✓ 99.4% Precision<br />
              ✓ Suppressed 90% Distractions
            </div>
          </div>

          {/* Target LLM/SLM */}
          <div
            onMouseEnter={() => setActiveStep('llm')}
            onMouseLeave={() => setActiveStep(null)}
            className={`rounded-xl bg-slate-950/70 border border-slate-800 p-4 transition-all duration-300 hover:border-purple-400 hover:bg-slate-950 ${
              activeStep === 'llm' ? 'ring-2 ring-purple-500/50 bg-slate-950' : ''
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">Any LLM or SLM</span>
            </div>
            <div className="space-y-1 text-[11px] text-slate-400">
              <div className="flex items-center justify-between">
                <span>Local: Ollama / Llama 3</span>
                <span className="text-purple-400 font-mono text-[10px]">8B SLM</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Cloud: Gemini / Claude / GPT-4</span>
                <span className="text-blue-400 font-mono text-[10px]">FastAPI</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Interactive Detail Drawer */}
      {activeStep && stepsInfo[activeStep] && (
        <div className="mt-6 p-4 rounded-xl bg-slate-950 border border-blue-500/30 animate-fadeIn flex items-center justify-between">
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-400" />
              {stepsInfo[activeStep].title}
            </h4>
            <p className="text-xs text-slate-300 mt-1">{stepsInfo[activeStep].desc}</p>
          </div>
          <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider hidden sm:block">
            Runtime Engine Spec
          </span>
        </div>
      )}
    </div>
  );
}

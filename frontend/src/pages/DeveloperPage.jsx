import React, { useState } from 'react';
import { 
  FileCode2, 
  Terminal, 
  Copy, 
  Check, 
  BookOpen, 
  Code2, 
  Layers, 
  Sparkles, 
  Cpu, 
  ArrowRight,
  ExternalLink
} from 'lucide-react';
import ArchitectureDiagram from '../components/ArchitectureDiagram';

function CodeBlock({ code, language = 'python' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group my-3 rounded-xl overflow-hidden border border-slate-800 bg-slate-950">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800/80 bg-slate-900/60 text-xs text-slate-400 font-mono">
        <span>{language}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1 hover:text-white transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-4 text-xs font-mono text-slate-200 overflow-x-auto leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
}

export default function DeveloperPage() {
  const [activeTab, setActiveTab] = useState('quickstart'); // quickstart, sdk, rest, langchain

  const pipCode = `pip install adaptive-memory-runtime`;

  const quickstartCode = `from adaptive_memory import MemoryRuntime

# 1. Initialize the Adaptive Memory Runtime
# Runs locally with embedded pgvector or connects to your cloud database
runtime = MemoryRuntime(
    storage_uri="postgresql://user:pass@localhost:5432/agent_memories",
    max_budget_tokens=500,
    quality_threshold=0.65
)

# 2. Store memories across the 4 cognitive tiers
runtime.store(
    tier="long_term",
    content="Production deployment requires strict TLS 1.3 and zero hardcoded credentials.",
    confidence=0.98,
    metadata={"env": "production", "policy": "sec_01"}
)

# 3. Intercept & evaluate memory before passing to ANY model
query = "How should we deploy the microservice to prod?"
trusted_context = runtime.recall(
    query=query, 
    user_id="usr_admin"
)

# 4. Use the trusted context in your model call
print(f"Selected memories: {len(trusted_context.memories)}")
print(f"Tokens consumed: {trusted_context.budget.tokens_used}")
print(trusted_context.to_system_prompt())`;

  const sdkAgentLoopCode = `import ollama
from adaptive_memory import MemoryRuntime

runtime = MemoryRuntime.local()

def run_agent_turn(user_message: str, user_id: str = "usr_default"):
    # Step A: Evaluate memory quality and build laser-focused prompt context
    recall_result = runtime.recall(query=user_message, user_id=user_id)
    
    # Step B: Inject only verified, high-utility memory context
    system_prompt = f"""You are an autonomous operations agent.
Here is your verified, trusted memory context:
{recall_result.to_bulleted_context()}"""

    # Step C: Call local Llama-3 (8B) or any cloud model
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message},
        ]
    )
    agent_reply = response['message']['content']

    # Step D: Store the interaction and record feedback outcome
    runtime.store_turn(
        user_id=user_id,
        user_message=user_message,
        agent_reply=agent_reply
    )
    
    return agent_reply, recall_result.memories`;

  const openAiCode = `import openai
from adaptive_memory.integrations import AdaptiveMemoryOpenAI

client = openai.OpenAI()

# Wrap OpenAI with Adaptive Memory Runtime
# Zero prompt bloat: handles vector retrieval, MQM scoring, and outcome logging automatically
agent = AdaptiveMemoryOpenAI(
    client=client,
    model="gpt-4o",
    budget_tokens=600,
    reinforce_outcomes=True
)

response = agent.chat(
    user_id="usr_102",
    message="Generate the migration script for PostgreSQL pgvector."
)

print(response.content)
print(f"Active memories applied: {response.memory_metrics.count_selected}")`;

  const restEndpoints = [
    {
      method: 'POST',
      path: '/api/recall',
      desc: 'Evaluate candidate memories and generate trusted context within token budget',
      req: `{
  "query": "Postgres database configurations",
  "user_id": "usr_default",
  "max_tokens": 400
}`,
      res: `{
  "selected_memories": [
    {
      "id": "mem_long_02",
      "type": "long_term",
      "content": "Primary PostgreSQL cluster is hosted on AWS RDS with pgvector...",
      "quality_score": 0.85,
      "breakdown": { "relevance": 0.88, "utility": 0.92, "confidence": 0.96 }
    }
  ],
  "suppressed_memories": [],
  "budget": { "total_allowed_tokens": 400, "tokens_used": 142 }
}`,
    },
    {
      method: 'POST',
      path: '/api/memories',
      desc: 'Explicitly store memory into specified cognitive tier (session, long_term, experience, prospective)',
      req: `{
  "type": "experience",
  "content": "Sending uncompressed PDFs spiked hallucination rates. Distill first.",
  "confidence": 0.95,
  "utility": 0.93,
  "metadata": { "incident": "tok_overflow" }
}`,
      res: `{
  "id": "mem_exp_918",
  "status": "active",
  "quality_score": 0.94,
  "created_at": "2026-10-15T00:00:00Z"
}`,
    },
    {
      method: 'POST',
      path: '/api/outcome',
      desc: 'Reinforce memory utility score based on real-world task success or failure (RL from Outcomes)',
      req: `{
  "memory_ids": ["mem_long_02"],
  "outcome": "positive",
  "user_id": "usr_default"
}`,
      res: `{
  "success": true,
  "updated": 1,
  "delta": 0.05
}`,
    },
    {
      method: 'POST',
      path: '/api/memories/{id}/forget',
      desc: 'Active suppression of outdated facts with Ebbinghaus forgetting retention policy',
      req: `{}`,
      res: `{
  "success": true,
  "id": "mem_legacy_01",
  "status": "forgotten"
}`,
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 space-y-10">
      
      {/* Header */}
      <div className="pb-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1 rounded bg-blue-500/10 text-blue-400">
              <FileCode2 className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold text-white tracking-tight">Developer Documentation & SDK</h1>
          </div>
          <p className="text-sm text-slate-400">
            Plug the Adaptive Memory Runtime into your agent pipelines with 3 lines of code.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
            Python 3.10+ • Node.js • REST
          </span>
        </div>
      </div>

      {/* Architecture Refresher */}
      <div>
        <h2 className="text-sm font-mono uppercase tracking-wider text-blue-400 mb-3">Runtime Execution Flow</h2>
        <ArchitectureDiagram interactive={false} />
      </div>

      {/* Documentation Tabs */}
      <div className="space-y-6">
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
          {[
            { id: 'quickstart', label: 'Quick Start (Python)' },
            { id: 'agent_loop', label: 'Local SLM Agent Loop' },
            { id: 'langchain', label: 'OpenAI / Claude Wrapper' },
            { id: 'rest', label: 'REST API Reference' },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab 1: Quickstart */}
        {activeTab === 'quickstart' && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <h3 className="text-lg font-bold text-white mb-2">1. Installation</h3>
              <p className="text-sm text-slate-400 mb-3">
                Install the lightweight runtime package. Zero heavyweight ML dependencies required for runtime inference.
              </p>
              <CodeBlock code={pipCode} language="bash" />
            </div>

            <div>
              <h3 className="text-lg font-bold text-white mb-2">2. Basic Integration</h3>
              <p className="text-sm text-slate-400 mb-3">
                Initialize the runtime, store facts, and perform quality-scored recall.
              </p>
              <CodeBlock code={quickstartCode} language="python" />
            </div>
          </div>
        )}

        {/* Tab 2: Agent Loop */}
        {activeTab === 'agent_loop' && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <h3 className="text-lg font-bold text-white mb-2">Zero-Bloat Local SLM Loop</h3>
              <p className="text-sm text-slate-400 mb-3">
                Small Language Models (e.g. Llama 3 8B, Phi-3, Mistral) struggle with context stuffing. The Adaptive Memory Runtime restricts context to 300-500 verified tokens, elevating SLM accuracy to match 70B models.
              </p>
              <CodeBlock code={sdkAgentLoopCode} language="python" />
            </div>
          </div>
        )}

        {/* Tab 3: OpenAI */}
        {activeTab === 'langchain' && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <h3 className="text-lg font-bold text-white mb-2">OpenAI & Proprietary Model Wrapper</h3>
              <p className="text-sm text-slate-400 mb-3">
                Wrap your standard OpenAI or Anthropic client to automatically manage conversation sessions and persist long-term memories.
              </p>
              <CodeBlock code={openAiCode} language="python" />
            </div>
          </div>
        )}

        {/* Tab 4: REST API */}
        {activeTab === 'rest' && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <h3 className="text-lg font-bold text-white mb-2">REST API Reference</h3>
              <p className="text-sm text-slate-400 mb-4">
                The Adaptive Memory Runtime exposes standard HTTP endpoints under <code className="text-blue-400 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">/api</code>.
              </p>
            </div>

            <div className="space-y-6">
              {restEndpoints.map((ep, idx) => (
                <div key={idx} className="rounded-xl bg-slate-900 border border-slate-800 p-5 space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 font-mono text-xs font-bold border border-blue-500/20">
                      {ep.method}
                    </span>
                    <span className="font-mono text-sm text-white font-semibold">{ep.path}</span>
                  </div>
                  <p className="text-xs text-slate-300">{ep.desc}</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                    <div>
                      <span className="text-[11px] font-mono text-slate-500 block mb-1">Request Payload:</span>
                      <CodeBlock code={ep.req} language="json" />
                    </div>
                    <div>
                      <span className="text-[11px] font-mono text-slate-500 block mb-1">Response JSON:</span>
                      <CodeBlock code={ep.res} language="json" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>

    </div>
  );
}

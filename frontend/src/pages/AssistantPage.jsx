import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  RotateCcw, 
  Sparkles, 
  Brain, 
  User, 
  Bot, 
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  Globe,
  Sliders,
  Volume2
} from 'lucide-react';
import { api } from '../api/client';
import ChatMessage from '../components/ChatMessage';
import MemoryInspector from '../components/MemoryInspector';

export default function AssistantPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I am connected to the **Adaptive Memory Runtime**. 

Every prompt you send is intercepted by the **Memory Quality Manager (MQM)**. It evaluates four memory tiers (Session, Long-Term, Experience, and Prospective), enforces your edge token budget, and injects only high-utility, conflict-free context into my prompt.

Try asking about:
- *"What are my architectural preferences for Python?"*
- *"What happened last time we sent uncompressed PDFs?"*
- *"Check if our pgvector database is configured."*`,
      memories_used: [
        {
          id: 'mem_init_01',
          type: 'session',
          content: 'Session initialized with default user context and active MQM evaluation pipeline.',
          quality_score: 0.95,
          confidence: 0.98,
          utility: 0.92,
          relevance: 0.96,
          recency: 1.0,
          conflict_risk: 0.02,
          tokens: 28,
        }
      ],
      search_used: false,
      timestamp: new Date().toISOString(),
    }
  ]);

  const [input, setInput] = useState('');
  const [userId, setUserId] = useState('usr_default');
  const [sessionId, setSessionId] = useState(() => `sess_${Date.now().toString(36)}`);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [inspectorData, setInspectorData] = useState({ open: false, memories: [], query: '' });
  const [feedbackGiven, setFeedbackGiven] = useState({});

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (textToSend) => {
    const text = (textToSend || input).trim();
    if (!text || isLoading) return;

    setInput('');
    const userMsg = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const data = await api.chat(text, userId, sessionId);
      const assistantMsg = {
        role: 'assistant',
        content: data.response || 'Memory runtime executed successfully.',
        memories_used: data.memories_used || [],
        search_used: data.search_used || false,
        search_results: data.search_results || [],
        timestamp: data.timestamp || new Date().toISOString(),
        interactionId: `turn_${Date.now()}`,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Error communicating with Memory Runtime. Please check backend status.',
          memories_used: [],
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceToggle = async () => {
    if (isRecording) {
      setIsRecording(false);
      return;
    }

    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      // Mock voice input
      setIsRecording(true);
      setTimeout(async () => {
        setIsRecording(false);
        const transcript = await api.transcribe(new Blob());
        handleSend(transcript.text);
      }, 1800);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    setIsRecording(true);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setIsRecording(false);
      handleSend(transcript);
    };

    recognition.onerror = () => {
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.start();
  };

  const handleOutcomeFeedback = async (msgIndex, memories, outcome) => {
    if (!memories || memories.length === 0) return;
    const memoryIds = memories.map((m) => m.id);
    await api.recordOutcome(memoryIds, outcome, userId);
    setFeedbackGiven((prev) => ({ ...prev, [msgIndex]: outcome }));
  };

  const handleNewSession = () => {
    setSessionId(`sess_${Date.now().toString(36)}`);
    setMessages([
      {
        role: 'assistant',
        content: 'New session started. Session-specific working memory has been reset while Long-Term and Experience memories remain intact.',
        memories_used: [],
        timestamp: new Date().toISOString(),
      }
    ]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto px-4 py-4 sm:px-6">
      
      {/* Top Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80 mb-3 text-xs">
        
        {/* User & Session Selector */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1.5 rounded-lg">
            <User className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-slate-400 font-mono">User:</span>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="bg-transparent text-slate-200 font-mono text-xs w-24 focus:outline-none focus:text-blue-400"
            />
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1.5 rounded-lg">
            <span className="text-slate-400 font-mono">Session:</span>
            <span className="text-slate-300 font-mono text-xs truncate max-w-[120px]">{sessionId}</span>
          </div>

          <button
            type="button"
            onClick={handleNewSession}
            className="flex items-center gap-1 text-slate-400 hover:text-white bg-slate-900 hover:bg-slate-800 px-2.5 py-1.5 rounded-lg border border-slate-800 transition-colors"
            title="Reset Working Session Memory"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">New Session</span>
          </button>
        </div>

        {/* Runtime Demoware Notice */}
        <div className="hidden md:flex items-center gap-2 text-slate-400 bg-blue-950/20 border border-blue-500/20 px-3 py-1 rounded-full text-[11px]">
          <Brain className="w-3 h-3 text-blue-400" />
          <span>Memory Runtime active: Chat & Voice are demonstration interfaces</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className="flex flex-col">
            <ChatMessage
              message={msg}
              onOpenInspector={(mems) =>
                setInspectorData({
                  open: true,
                  memories: mems,
                  query: messages[index - 1]?.content || 'Prompt Context',
                })
              }
            />

            {/* Reinforcement Learning Feedback Bar for Assistant Responses */}
            {msg.role === 'assistant' && msg.memories_used && msg.memories_used.length > 0 && (
              <div className="flex items-center gap-3 ml-12 text-[11px] text-slate-500 mt-1">
                <span>Memory Outcome RL:</span>
                <button
                  type="button"
                  onClick={() => handleOutcomeFeedback(index, msg.memories_used, 'positive')}
                  className={`flex items-center gap-1 hover:text-emerald-400 transition-colors ${
                    feedbackGiven[index] === 'positive' ? 'text-emerald-400 font-bold' : ''
                  }`}
                  title="Reinforce memory utility score (+0.05)"
                >
                  <ThumbsUp className="w-3 h-3" />
                  <span>Helpful</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleOutcomeFeedback(index, msg.memories_used, 'negative')}
                  className={`flex items-center gap-1 hover:text-rose-400 transition-colors ${
                    feedbackGiven[index] === 'negative' ? 'text-rose-400 font-bold' : ''
                  }`}
                  title="Penalize memory utility score (-0.08)"
                >
                  <ThumbsDown className="w-3 h-3" />
                  <span>Unhelpful</span>
                </button>
                {feedbackGiven[index] && (
                  <span className="text-[10px] text-emerald-400 font-mono">
                    ✓ Calibrated
                  </span>
                )}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 items-center text-slate-400 my-4 pl-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="flex items-center gap-2 text-xs font-mono bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
              <span>Querying Memory Quality Manager (MQM)...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Bar */}
      <div className="pt-3 border-t border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-center gap-2"
        >
          {/* Microphone button */}
          <button
            type="button"
            onClick={handleVoiceToggle}
            className={`p-3 rounded-xl border transition-all ${
              isRecording
                ? 'bg-rose-600 text-white border-rose-500 animate-pulse'
                : 'bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border-slate-800'
            }`}
            title={isRecording ? 'Listening... click to stop' : 'Voice Input (Speech-to-Text)'}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          {/* Text Input */}
          <div className="relative flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything or teach the runtime new operational constraints..."
              disabled={isLoading}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 pr-12 transition-colors disabled:opacity-50"
            />

            {/* Send button inside input */}
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white disabled:text-slate-600 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>

        <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 px-1">
          <span>Press Enter to send. Edge Token Budgeting actively suppresses context bloat.</span>
          <span className="font-mono">MQM Threshold: &gt;0.65</span>
        </div>
      </div>

      {/* Memory Inspector Drawer */}
      <MemoryInspector
        isOpen={inspectorData.open}
        onClose={() => setInspectorData({ open: false, memories: [], query: '' })}
        memories={inspectorData.memories}
        query={inspectorData.query}
      />
    </div>
  );
}

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  History,
  Brain,
  Sparkles,
  ChevronDown,
  ChevronUp,
  X,
  Settings,
  Wifi,
  WifiOff,
  Clock,
  Database,
  Shield,
  Zap,
  MessageSquare,
  Search,
  Star,
  AlertTriangle,
} from 'lucide-react';
import VoiceOrb from '../components/VoiceOrb';
import { api } from '../api/client';

// ── Voice Assistant States ──
const STATES = {
  IDLE: 'idle',
  LISTENING: 'listening',
  PROCESSING: 'processing',
  SPEAKING: 'speaking',
};

// ── Greeting messages ──
const GREETINGS = [
  "Hello! I'm your Adaptive Memory assistant.",
  "Welcome back. Your memories are ready.",
  "Hi there! What can I help you remember?",
  "Ready when you are. Tap to speak.",
];

export default function VoiceAssistantPage() {
  // ── Core state ──
  const [voiceState, setVoiceState] = useState(STATES.IDLE);
  const [audioLevel, setAudioLevel] = useState(0);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [displayedResponse, setDisplayedResponse] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [memoriesUsed, setMemoriesUsed] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showMemoryPanel, setShowMemoryPanel] = useState(false);
  const [memoryPanelData, setMemoryPanelData] = useState(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [statusMessage, setStatusMessage] = useState('');
  const [greeting] = useState(() => GREETINGS[Math.floor(Math.random() * GREETINGS.length)]);

  // ── Refs ──
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const streamRef = useRef(null);
  const animFrameRef = useRef(null);
  const typingIntervalRef = useRef(null);
  const historyEndRef = useRef(null);
  const responseEndRef = useRef(null);
  const scrollContainerRef = useRef(null);

  // ── Scroll conversation history ──
  useEffect(() => {
    if (historyEndRef.current) {
      historyEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversationHistory]);

  // ── Auto-scroll as response streams ──
  useEffect(() => {
    if (responseEndRef.current) {
      responseEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [displayedResponse]);

  // ── Streaming text effect ──
  const streamText = useCallback((text, onComplete) => {
    if (typingIntervalRef.current) clearInterval(typingIntervalRef.current);
    let idx = 0;
    setDisplayedResponse('');
    typingIntervalRef.current = setInterval(() => {
      idx++;
      setDisplayedResponse(text.slice(0, idx));
      if (idx >= text.length) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
        if (onComplete) onComplete();
      }
    }, 22);
  }, []);

  // ── Audio level monitoring ──
  const startAudioMonitor = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);

      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      const updateLevel = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
        const avg = sum / dataArray.length / 255;
        setAudioLevel(avg);
        animFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();
    } catch (err) {
      console.warn('Microphone access denied:', err);
    }
  }, []);

  const stopAudioMonitor = useCallback(() => {
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    analyserRef.current = null;
    setAudioLevel(0);
  }, []);

  // ── Check if query is a memory inspection command ──
  const isMemoryQuery = (text) => {
    const lower = text.toLowerCase();
    return (
      lower.includes('show my') ||
      lower.includes('my memories') ||
      lower.includes('long term memory') ||
      lower.includes('long-term memory') ||
      lower.includes('session memory') ||
      lower.includes('experience memory') ||
      lower.includes('prospective memory') ||
      lower.includes('what do you remember') ||
      lower.includes('what do you know about me') ||
      lower.includes('my preferences') ||
      lower.includes('my history') ||
      lower.includes('memory status') ||
      lower.includes('all memories')
    );
  };

  const getMemoryTypeFromQuery = (text) => {
    const lower = text.toLowerCase();
    if (lower.includes('long term') || lower.includes('long-term') || lower.includes('preference') || lower.includes('permanent')) return 'long_term';
    if (lower.includes('session') || lower.includes('current')) return 'session';
    if (lower.includes('experience') || lower.includes('past') || lower.includes('history')) return 'experience';
    if (lower.includes('prospective') || lower.includes('reminder') || lower.includes('future') || lower.includes('upcoming')) return 'prospective';
    return null; // all types
  };

  // ── Fetch and display memories ──
  const handleMemoryQuery = useCallback(async (text) => {
    const memType = getMemoryTypeFromQuery(text);
    let memories = [];
    let label = 'All';

    try {
      if (memType === 'long_term') {
        memories = await api.getLongTermMemories();
        label = 'Long-Term';
      } else if (memType === 'session') {
        memories = await api.getSessionMemories();
        label = 'Session';
      } else if (memType === 'experience') {
        memories = await api.getExperienceMemories();
        label = 'Experience';
      } else if (memType === 'prospective') {
        memories = await api.getProspectiveMemories();
        label = 'Prospective';
      } else {
        memories = await api.getMemories();
        label = 'All';
      }
    } catch {
      memories = [];
    }

    if (!Array.isArray(memories)) memories = [];
    const activeMemories = memories.filter((m) => m.status !== 'forgotten');

    setMemoryPanelData({
      label,
      type: memType,
      memories: activeMemories,
    });
    setShowMemoryPanel(true);

    const summaryLines = activeMemories.slice(0, 5).map(
      (m, i) => `${i + 1}. "${m.content?.slice(0, 80)}..." (${m.type || 'unknown'}, confidence: ${(m.confidence || 0).toFixed(2)})`
    );

    const responseText = activeMemories.length > 0
      ? `I found ${activeMemories.length} ${label.toLowerCase()} ${activeMemories.length === 1 ? 'memory' : 'memories'} stored locally:\n\n${summaryLines.join('\n')}\n\n${activeMemories.length > 5 ? `...and ${activeMemories.length - 5} more. All data stays on your device.` : 'All data is stored locally on your device.'}`
      : `No ${label.toLowerCase()} memories found yet. As we interact, I'll learn and remember what matters to you.`;

    return responseText;
  }, []);

  // ── Process voice input ──
  const processInput = useCallback(
    async (text) => {
      if (!text.trim()) return;

      setVoiceState(STATES.PROCESSING);
      setStatusMessage('Processing with Memory Quality Manager...');

      // Add user message to history
      setConversationHistory((prev) => [
        ...prev,
        { role: 'user', text, timestamp: new Date() },
      ]);

      try {
        let responseText;
        let memories = [];

        // Check if this is a memory inspection query
        if (isMemoryQuery(text)) {
          responseText = await handleMemoryQuery(text);
        } else {
          // Regular chat with memory-augmented response
          const chatResult = await api.chat(text, 'usr_default', `voice_${Date.now()}`);
          responseText = chatResult.response || "I've processed your request through the memory runtime.";
          memories = chatResult.memories_used || [];
          setMemoriesUsed(memories);
        }

        setResponse(responseText);

        // Stream the response text
        setVoiceState(STATES.SPEAKING);
        setStatusMessage('');
        streamText(responseText, () => {
          // Speak response if not muted
          if (!isMuted && 'speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(responseText.replace(/\n/g, '. ').slice(0, 500));
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.onend = () => setVoiceState(STATES.IDLE);
            window.speechSynthesis.speak(utterance);
          } else {
            setTimeout(() => setVoiceState(STATES.IDLE), 1000);
          }
        });

        // Add assistant response to history
        setConversationHistory((prev) => [
          ...prev,
          {
            role: 'assistant',
            text: responseText,
            timestamp: new Date(),
            memoriesCount: memories.length,
          },
        ]);
      } catch (err) {
        setVoiceState(STATES.IDLE);
        setStatusMessage('');
        const errMsg = 'I encountered an issue processing that. The memory runtime is still operational — try again.';
        setResponse(errMsg);
        streamText(errMsg);
        setConversationHistory((prev) => [
          ...prev,
          { role: 'assistant', text: errMsg, timestamp: new Date(), memoriesCount: 0 },
        ]);
      }
    },
    [isMuted, streamText, handleMemoryQuery]
  );

  // ── Start listening ──
  const startListening = useCallback(() => {
    if (voiceState === STATES.LISTENING) {
      // Stop listening
      if (recognitionRef.current) recognitionRef.current.stop();
      stopAudioMonitor();
      setVoiceState(STATES.IDLE);
      return;
    }

    // Cancel any ongoing speech
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    if (typingIntervalRef.current) clearInterval(typingIntervalRef.current);

    setTranscript('');
    setDisplayedResponse('');
    setResponse('');
    setShowMemoryPanel(false);
    setMemoryPanelData(null);
    setVoiceState(STATES.LISTENING);
    setStatusMessage('Listening...');

    startAudioMonitor();

    // Use Web Speech API for STT
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        let interimText = '';
        let finalText = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const t = event.results[i][0].transcript;
          if (event.results[i].isFinal) finalText += t;
          else interimText += t;
        }
        setTranscript(finalText || interimText);
      };

      recognition.onend = () => {
        stopAudioMonitor();
        const currentTranscript = document.getElementById('voice-transcript')?.textContent || '';
        if (currentTranscript.trim()) {
          processInput(currentTranscript);
        } else {
          setVoiceState(STATES.IDLE);
          setStatusMessage('');
        }
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        stopAudioMonitor();
        setVoiceState(STATES.IDLE);
        setStatusMessage(event.error === 'not-allowed' ? 'Microphone access denied' : '');
      };

      recognition.start();
      recognitionRef.current = recognition;
    } else {
      // Fallback: simulate listening for demo
      setTimeout(() => {
        stopAudioMonitor();
        setTranscript("Show my long-term memories");
        processInput("Show my long-term memories");
      }, 3000);
    }
  }, [voiceState, startAudioMonitor, stopAudioMonitor, processInput]);

  // ── Cleanup on unmount ──
  useEffect(() => {
    return () => {
      stopAudioMonitor();
      if (recognitionRef.current) recognitionRef.current.abort();
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
      if (typingIntervalRef.current) clearInterval(typingIntervalRef.current);
    };
  }, [stopAudioMonitor]);

  // ── Keyboard shortcut: Space to toggle ──
  useEffect(() => {
    const handleKey = (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        startListening();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [startListening]);

  // ── Text input fallback ──
  const [textInput, setTextInput] = useState('');
  const [showTextInput, setShowTextInput] = useState(false);

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (textInput.trim()) {
      setTranscript(textInput);
      processInput(textInput);
      setTextInput('');
      setShowTextInput(false);
    }
  };

  // ── Memory type configs ──
  const memoryTypeConfig = {
    session: { color: 'blue', icon: Clock, label: 'Session' },
    long_term: { color: 'emerald', icon: Database, label: 'Long-Term' },
    experience: { color: 'amber', icon: Star, label: 'Experience' },
    prospective: { color: 'purple', icon: Zap, label: 'Prospective' },
  };

  // ── Render ──
  return (
    <div className="relative h-full w-full overflow-hidden bg-slate-950 flex flex-col items-center">
      {/* ── Background Grid Pattern ── */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(0,210,210,0.4) 1px, transparent 0)`,
          backgroundSize: '40px 40px',
        }}
      />

      {/* ── Ambient Gradient Blobs ── */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-teal-500/5 rounded-full blur-3xl" />

      {/* ── Top Status Bar ── */}
      <div className="relative z-10 w-full px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs font-mono">
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-slate-400">{isOnline ? 'Edge Runtime Active' : 'Offline'}</span>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 bg-slate-900/50 px-2.5 py-1 rounded-full border border-slate-800/50">
            <Shield className="w-3 h-3" />
            <span>Local Storage</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowTextInput(!showTextInput)}
            className="p-2 rounded-xl bg-slate-900/60 border border-slate-800/50 text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30 transition-all"
            title="Type instead"
          >
            <MessageSquare className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsMuted(!isMuted)}
            className="p-2 rounded-xl bg-slate-900/60 border border-slate-800/50 text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30 transition-all"
            title={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className={`p-2 rounded-xl border transition-all ${
              showHistory
                ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
                : 'bg-slate-900/60 border-slate-800/50 text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30'
            }`}
            title="Conversation History"
          >
            <History className="w-4 h-4" />
            {conversationHistory.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 text-[9px] font-bold bg-cyan-500 text-white rounded-full flex items-center justify-center">
                {Math.ceil(conversationHistory.length / 2)}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* ── Main Voice Interface ── */}
      <div className="relative z-10 flex-1 flex flex-col items-center w-full max-w-2xl px-6 overflow-y-auto pb-4 scrollbar-thin" style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(0,210,210,0.2) transparent' }}>
        {/* Status message above orb */}
        {statusMessage && (
          <div className="mb-4 text-xs font-mono text-cyan-400/80 animate-pulse">
            {statusMessage}
          </div>
        )}

        {/* ── The Voice Orb ── */}
        <div className="relative cursor-pointer group" onClick={startListening}>
          <VoiceOrb state={voiceState} audioLevel={audioLevel} size={280} />

          {/* Center text overlay */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            {voiceState === STATES.IDLE && (
              <>
                <p className="text-lg font-light text-white/90 mb-1 tracking-wide">
                  Tap to Speak
                </p>
                <p className="text-[11px] text-cyan-400/60 font-mono">
                  or press Space
                </p>
              </>
            )}
            {voiceState === STATES.LISTENING && (
              <>
                <Mic className="w-8 h-8 text-cyan-400 animate-pulse mb-2" />
                <p className="text-sm text-cyan-300/90 font-light">Listening...</p>
              </>
            )}
            {voiceState === STATES.PROCESSING && (
              <>
                <Brain className="w-7 h-7 text-amber-400 animate-spin mb-2" />
                <p className="text-sm text-amber-300/80 font-light">Thinking...</p>
              </>
            )}
            {voiceState === STATES.SPEAKING && (
              <>
                <Volume2 className="w-7 h-7 text-cyan-400 animate-pulse mb-2" />
                <p className="text-sm text-cyan-300/80 font-light">Speaking</p>
              </>
            )}
          </div>

          {/* Outer pulse ring on listening */}
          {voiceState === STATES.LISTENING && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-[320px] h-[320px] rounded-full border border-cyan-400/20 animate-ping" style={{ animationDuration: '2s' }} />
            </div>
          )}
        </div>

        {/* ── Live Transcript ── */}
        {transcript && (
          <div className="mt-6 w-full">
            <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/30 rounded-2xl px-5 py-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <Mic className="w-3 h-3 text-blue-400" />
                </div>
                <span className="text-[11px] font-mono text-blue-400/70 uppercase tracking-wider">You said</span>
              </div>
              <p id="voice-transcript" className="text-white/90 text-sm leading-relaxed">
                {transcript}
              </p>
            </div>
          </div>
        )}

        {/* ── Streaming Response ── */}
        {displayedResponse && (
          <div className="mt-4 w-full">
            <div className="bg-slate-900/30 backdrop-blur-xl border border-cyan-500/10 rounded-2xl px-5 py-4 shadow-lg shadow-cyan-500/5">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-5 h-5 rounded-full bg-cyan-500/20 flex items-center justify-center">
                  <Sparkles className="w-3 h-3 text-cyan-400" />
                </div>
                <span className="text-[11px] font-mono text-cyan-400/70 uppercase tracking-wider">
                  Adaptive Memory Response
                </span>
                {memoriesUsed.length > 0 && (
                  <span className="ml-auto text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    {memoriesUsed.length} {memoriesUsed.length === 1 ? 'memory' : 'memories'} used
                  </span>
                )}
              </div>
              <p className="text-white/85 text-sm leading-relaxed whitespace-pre-line">
                {displayedResponse}
                {typingIntervalRef.current && (
                  <span className="inline-block w-2 h-4 bg-cyan-400 ml-0.5 animate-pulse rounded-sm" />
                )}
              </p>
            </div>
          </div>
        )}

        {/* ── Idle Greeting ── */}
        {voiceState === STATES.IDLE && !transcript && !displayedResponse && (
          <div className="mt-8 text-center">
            <p className="text-slate-400 text-sm font-light leading-relaxed max-w-md">
              {greeting}
            </p>
            <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
              {[
                "What's my preferred route?",
                "Show my long-term memory",
                "Set AC to 22°C",
                "Any reminders today?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setTranscript(suggestion);
                    processInput(suggestion);
                  }}
                  className="text-[11px] text-cyan-400/70 bg-cyan-500/5 border border-cyan-500/10 rounded-full px-3 py-1.5 hover:bg-cyan-500/10 hover:border-cyan-500/20 hover:text-cyan-300 transition-all"
                >
                  "{suggestion}"
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ── Text Input Fallback ── */}
        {showTextInput && (
          <form onSubmit={handleTextSubmit} className="mt-4 w-full">
            <div className="flex gap-2">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Type a command or question..."
                className="flex-1 bg-slate-900/60 border border-slate-700/40 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/40 focus:ring-1 focus:ring-cyan-500/20"
                autoFocus
              />
              <button
                type="submit"
                className="px-5 py-3 bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/30 transition-all"
              >
                Send
              </button>
            </div>
          </form>
        )}
      </div>

      {/* ── Bottom Quick Actions ── */}
      <div className="relative z-10 w-full px-6 py-5">
        <div className="max-w-2xl mx-auto">
          <div className="grid grid-cols-4 gap-3">
            {[
              { icon: Mic, label: 'Voice', desc: 'Tap the orb', active: voiceState === STATES.LISTENING },
              { icon: Database, label: 'Memory', desc: 'Browse stored', action: () => { setTranscript('Show all my memories'); processInput('Show all my memories'); } },
              { icon: Search, label: 'Search', desc: 'Web lookup', action: () => { setTranscript('Search for the latest news'); processInput('Search for the latest news'); } },
              { icon: Brain, label: 'Recall', desc: 'Quality test', action: () => { setTranscript('What do you know about me?'); processInput('What do you know about me?'); } },
            ].map((item) => (
              <button
                key={item.label}
                onClick={item.action || startListening}
                className={`flex flex-col items-center gap-1.5 p-3 rounded-2xl border transition-all ${
                  item.active
                    ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
                    : 'bg-slate-900/40 border-slate-800/40 text-slate-400 hover:text-white hover:border-slate-700/60 hover:bg-slate-900/60'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="text-xs font-medium">{item.label}</span>
                <span className="text-[10px] text-slate-500 hidden sm:block">{item.desc}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Conversation History Slide-Out ── */}
      {showHistory && (
        <div className="absolute inset-0 z-40 flex">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowHistory(false)} />
          <div className="relative ml-auto w-full max-w-md h-full bg-slate-950/95 backdrop-blur-xl border-l border-slate-800/50 flex flex-col animate-slide-in-right">
            <div className="flex items-center justify-between p-4 border-b border-slate-800/50">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-cyan-400" />
                <span className="text-sm font-semibold text-white">Conversation History</span>
              </div>
              <button onClick={() => setShowHistory(false)} className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {conversationHistory.length === 0 ? (
                <div className="text-center text-slate-500 text-sm mt-12">
                  <History className="w-8 h-8 mx-auto mb-3 opacity-30" />
                  <p>No conversations yet.</p>
                  <p className="text-xs mt-1">Start by tapping the orb.</p>
                </div>
              ) : (
                conversationHistory.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                        msg.role === 'user'
                          ? 'bg-blue-500/15 border border-blue-500/20 text-blue-100'
                          : 'bg-slate-900/80 border border-slate-800/50 text-slate-200'
                      }`}
                    >
                      <p className="leading-relaxed whitespace-pre-line text-xs">{msg.text.slice(0, 300)}{msg.text.length > 300 ? '...' : ''}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-[10px] text-slate-500">
                          {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {msg.memoriesCount > 0 && (
                          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                            {msg.memoriesCount} memories
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
              <div ref={historyEndRef} />
            </div>
          </div>
        </div>
      )}

      {/* ── Memory Panel Slide-Out ── */}
      {showMemoryPanel && memoryPanelData && (
        <div className="absolute inset-0 z-40 flex">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowMemoryPanel(false)} />
          <div className="relative ml-auto w-full max-w-lg h-full bg-slate-950/95 backdrop-blur-xl border-l border-slate-800/50 flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-slate-800/50">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <span className="text-sm font-semibold text-white">
                  {memoryPanelData.label} Memories
                </span>
                <span className="text-[10px] font-mono text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
                  {memoryPanelData.memories.length} records
                </span>
              </div>
              <button onClick={() => setShowMemoryPanel(false)} className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {memoryPanelData.memories.map((mem, i) => {
                const typeConf = memoryTypeConfig[mem.type] || memoryTypeConfig.session;
                const TypeIcon = typeConf.icon;
                const colorMap = {
                  blue: { bg: 'bg-blue-500/10', border: 'border-blue-500/20', text: 'text-blue-400', bar: 'bg-blue-500' },
                  emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', text: 'text-emerald-400', bar: 'bg-emerald-500' },
                  amber: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400', bar: 'bg-amber-500' },
                  purple: { bg: 'bg-purple-500/10', border: 'border-purple-500/20', text: 'text-purple-400', bar: 'bg-purple-500' },
                };
                const c = colorMap[typeConf.color] || colorMap.blue;

                return (
                  <div key={mem.id || i} className={`${c.bg} border ${c.border} rounded-xl p-4`}>
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-lg ${c.bg} flex items-center justify-center shrink-0 mt-0.5`}>
                        <TypeIcon className={`w-4 h-4 ${c.text}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className={`text-[10px] font-mono uppercase ${c.text}`}>{typeConf.label}</span>
                          <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                            mem.status === 'active' ? 'text-emerald-400 bg-emerald-500/10' : 'text-slate-500 bg-slate-800'
                          }`}>
                            {mem.status}
                          </span>
                        </div>
                        <p className="text-sm text-white/85 leading-relaxed mb-3">{mem.content}</p>
                        <div className="grid grid-cols-2 gap-2 text-[11px]">
                          <div>
                            <span className="text-slate-500">Confidence</span>
                            <div className="flex items-center gap-2 mt-0.5">
                              <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                <div className={`h-full ${c.bar} rounded-full`} style={{ width: `${(mem.confidence || 0) * 100}%` }} />
                              </div>
                              <span className={c.text}>{((mem.confidence || 0) * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                          <div>
                            <span className="text-slate-500">Utility</span>
                            <div className="flex items-center gap-2 mt-0.5">
                              <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                <div className={`h-full ${c.bar} rounded-full`} style={{ width: `${(mem.utility || 0) * 100}%` }} />
                              </div>
                              <span className={c.text}>{((mem.utility || 0) * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ── Slide-in animation style ── */}
      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        .animate-slide-in-right {
          animation: slideInRight 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

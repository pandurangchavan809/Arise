import React from 'react';
import { Brain, Globe, ExternalLink, Bot, User, CheckCircle2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function ChatMessage({ message, onOpenInspector }) {
  const isUser = message.role === 'user';
  const memoryCount = message.memories_used ? message.memories_used.length : 0;
  const hasSearch = message.search_used || (message.search_results && message.search_results.length > 0);

  const formattedTime = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Bot Icon */}
      {!isUser && (
        <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center shrink-0 text-blue-400 mt-1 shadow-sm">
          <Bot className="w-4 h-4" />
        </div>
      )}

      <div className={`max-w-[85%] md:max-w-[75%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        
        {/* Message Bubble */}
        <div
          className={`rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-md backdrop-blur-sm ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-none'
              : 'bg-slate-900 border border-slate-800 text-slate-100 rounded-tl-none'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Indicators below assistant bubble */}
        {!isUser && (
          <div className="flex flex-wrap items-center gap-2 mt-2 ml-1">
            {/* Memory Used Badge */}
            {memoryCount > 0 ? (
              <button
                type="button"
                onClick={() => onOpenInspector && onOpenInspector(message.memories_used)}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-medium bg-blue-500/10 text-blue-300 border border-blue-500/30 hover:bg-blue-500/20 hover:border-blue-400 transition-all cursor-pointer shadow-sm group"
                title="Click to view recalled memories & quality breakdown"
              >
                <Brain className="w-3.5 h-3.5 text-blue-400 group-hover:scale-110 transition-transform" />
                <span>Memory used: {memoryCount}</span>
                <span className="text-[10px] bg-blue-500/20 px-1 py-0.2 rounded text-blue-200">Inspect</span>
              </button>
            ) : (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono text-slate-500 bg-slate-950 border border-slate-800">
                Direct Context (0 memories)
              </span>
            )}

            {/* Web Search Used Badge */}
            {hasSearch && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                <span>Web Search Verified</span>
              </span>
            )}

            {/* Timestamp */}
            {formattedTime && (
              <span className="text-[11px] text-slate-500 font-mono ml-1">
                {formattedTime}
              </span>
            )}
          </div>
        )}

        {/* Citations block if any search results */}
        {!isUser && message.search_results && message.search_results.length > 0 && (
          <div className="mt-2.5 ml-1 w-full bg-slate-950/70 border border-slate-800 rounded-lg p-3 text-xs">
            <div className="text-slate-400 font-semibold mb-1.5 flex items-center gap-1">
              <Globe className="w-3 h-3 text-emerald-400" />
              <span>External Citations:</span>
            </div>
            <div className="space-y-1.5">
              {message.search_results.map((cite, idx) => (
                <a
                  key={idx}
                  href={cite.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between text-blue-400 hover:text-blue-300 hover:underline p-1 rounded hover:bg-slate-900"
                >
                  <span className="truncate pr-2">{cite.title}</span>
                  <ExternalLink className="w-3 h-3 shrink-0" />
                </a>
              ))}
            </div>
          </div>
        )}

        {/* User timestamp */}
        {isUser && formattedTime && (
          <span className="text-[11px] text-slate-500 font-mono mt-1 mr-1">
            {formattedTime}
          </span>
        )}
      </div>

      {/* User Icon */}
      {isUser && (
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0 text-white mt-1 shadow-sm">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}

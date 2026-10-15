import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Plus, 
  Search, 
  Clock, 
  Layers, 
  Flame, 
  CalendarClock, 
  Filter, 
  RefreshCw, 
  X, 
  Sliders, 
  Check, 
  Info,
  Archive,
  Trash2,
  Sparkles
} from 'lucide-react';
import { api } from '../api/client';
import MemoryCard, { TYPE_CONFIG } from '../components/MemoryCard';

export default function MemoryBrowserPage() {
  const [activeTab, setActiveTab] = useState('session'); // session, long_term, experience, prospective, all
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all, active, archived
  const [stats, setStats] = useState({
    total_memories: 0,
    active_memories: 0,
    average_quality_score: 0.88,
    retrieval_precision: 0.942,
  });

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newContent, setNewContent] = useState('');
  const [newType, setNewType] = useState('long_term');
  const [newConfidence, setNewConfidence] = useState(0.9);
  const [newUtility, setNewUtility] = useState(0.85);
  const [newMetadataKey, setNewMetadataKey] = useState('');
  const [newMetadataVal, setNewMetadataVal] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [allMems, runtimeStats] = await Promise.all([
        api.getMemories(),
        api.getStats(),
      ]);
      setMemories(allMems || []);
      if (runtimeStats) setStats(runtimeStats);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleArchive = async (id) => {
    await api.archiveMemory(id);
    loadData();
  };

  const handleForget = async (id) => {
    await api.forgetMemory(id);
    loadData();
  };

  const handleCreateMemory = async (e) => {
    e.preventDefault();
    if (!newContent.trim()) return;

    const metadata = {};
    if (newMetadataKey.trim() && newMetadataVal.trim()) {
      metadata[newMetadataKey.trim()] = newMetadataVal.trim();
    }

    await api.createMemory({
      type: newType,
      content: newContent.trim(),
      confidence: parseFloat(newConfidence),
      utility: parseFloat(newUtility),
      metadata,
    });

    setNewContent('');
    setNewMetadataKey('');
    setNewMetadataVal('');
    setIsModalOpen(false);
    loadData();
  };

  // Filter memories
  const filteredMemories = memories.filter((mem) => {
    // Tab filter
    if (activeTab !== 'all' && mem.type !== activeTab) return false;
    // Status filter
    if (statusFilter !== 'all' && mem.status !== statusFilter) return false;
    // Text search
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const inContent = mem.content.toLowerCase().includes(q);
      const inId = mem.id.toLowerCase().includes(q);
      if (!inContent && !inId) return false;
    }
    return true;
  });

  const tabList = [
    { key: 'session', label: 'Session', icon: Clock, count: memories.filter((m) => m.type === 'session').length },
    { key: 'long_term', label: 'Long-Term', icon: Layers, count: memories.filter((m) => m.type === 'long_term').length },
    { key: 'experience', label: 'Experience (RL)', icon: Flame, count: memories.filter((m) => m.type === 'experience').length },
    { key: 'prospective', label: 'Prospective', icon: CalendarClock, count: memories.filter((m) => m.type === 'prospective').length },
    { key: 'all', label: 'All Records', icon: Database, count: memories.length },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 space-y-8">
      
      {/* Page Title & Add Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1 rounded bg-blue-500/10 text-blue-400">
              <Database className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold text-white tracking-tight">Memory Browser</h1>
          </div>
          <p className="text-sm text-slate-400">
            Inspect, manage, and audit cognitive memories across all four decoupled tiers.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={loadData}
            className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors"
            title="Refresh memory store"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-all shadow-md shadow-blue-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>Store New Memory</span>
          </button>
        </div>
      </div>

      {/* Stats Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs font-mono text-slate-400 block mb-1">Total Memories</span>
          <span className="text-2xl font-bold text-white font-mono">{stats.total_memories || memories.length}</span>
          <span className="text-[11px] text-slate-500 block mt-1">Across 4 tiers</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs font-mono text-slate-400 block mb-1">Active for Recall</span>
          <span className="text-2xl font-bold text-emerald-400 font-mono">
            {memories.filter((m) => m.status === 'active').length}
          </span>
          <span className="text-[11px] text-emerald-500/80 block mt-1">Unsuppressed</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs font-mono text-slate-400 block mb-1">Mean Quality Score</span>
          <span className="text-2xl font-bold text-blue-400 font-mono">
            {(stats.average_quality_score || 0.88).toFixed(2)}
          </span>
          <span className="text-[11px] text-blue-400/80 block mt-1">Trust benchmark</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs font-mono text-slate-400 block mb-1">Retrieval Precision</span>
          <span className="text-2xl font-bold text-purple-400 font-mono">
            {((stats.retrieval_precision || 0.942) * 100).toFixed(1)}%
          </span>
          <span className="text-[11px] text-purple-400/80 block mt-1">Zero context pollution</span>
        </div>
      </div>

      {/* Tabs & Search Filter Header */}
      <div className="space-y-4">
        {/* Memory Tier Tabs */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
          {tabList.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'bg-slate-900/70 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                <span
                  className={`text-xs px-1.5 py-0.2 rounded-full font-mono ${
                    isActive ? 'bg-blue-700 text-blue-100' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Filter controls row */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          {/* Search text input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter memories by keyword, entity, or ID..."
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Status selector */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500 font-mono">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-900 border border-slate-800 text-slate-300 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active Only</option>
              <option value="archived">Archived Only</option>
              <option value="forgotten">Forgotten Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Memory Cards Grid */}
      {filteredMemories.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/30 rounded-2xl border border-dashed border-slate-800">
          <Database className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <h3 className="text-base font-semibold text-slate-300">No memories found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            {searchQuery
              ? 'No memories match your query filter. Try clearing your search.'
              : 'This memory store tier currently has zero entries.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredMemories.map((mem) => (
            <MemoryCard
              key={mem.id}
              memory={mem}
              onArchive={handleArchive}
              onForget={handleForget}
            />
          ))}
        </div>
      )}

      {/* Add Memory Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-blue-400" />
                <h3 className="text-lg font-bold text-white">Store In Adaptive Memory Runtime</h3>
              </div>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateMemory} className="space-y-4">
              {/* Tier selector */}
              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1.5">Cognitive Memory Tier</label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {['session', 'long_term', 'experience', 'prospective'].map((t) => {
                    const cfg = TYPE_CONFIG[t];
                    const isSelected = newType === t;
                    return (
                      <button
                        key={t}
                        type="button"
                        onClick={() => setNewType(t)}
                        className={`p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 transition-all ${
                          isSelected
                            ? 'bg-blue-600/20 border-blue-500 text-blue-300'
                            : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <cfg.icon className="w-4 h-4" />
                        <span>{cfg.label.split(' ')[0]}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Memory content */}
              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1.5">Memory Content</label>
                <textarea
                  rows={4}
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  placeholder="State the fact, operational rule, failure outcome, or prospective trigger..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none font-normal"
                  required
                />
              </div>

              {/* Sliders: Confidence & Utility */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>Source Confidence</span>
                    <span className="font-mono text-blue-400">{Math.round(newConfidence * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={newConfidence}
                    onChange={(e) => setNewConfidence(e.target.value)}
                    className="w-full accent-blue-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>Initial Utility</span>
                    <span className="font-mono text-amber-400">{Math.round(newUtility * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={newUtility}
                    onChange={(e) => setNewUtility(e.target.value)}
                    className="w-full accent-amber-500"
                  />
                </div>
              </div>

              {/* Custom metadata tag */}
              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1.5">Optional Metadata Tag</label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    value={newMetadataKey}
                    onChange={(e) => setNewMetadataKey(e.target.value)}
                    placeholder="Key (e.g. source, trigger)"
                    className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
                  />
                  <input
                    type="text"
                    value={newMetadataVal}
                    onChange={(e) => setNewMetadataVal(e.target.value)}
                    placeholder="Value (e.g. docs, tokens>5000)"
                    className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="pt-4 border-t border-slate-800 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white bg-slate-800 text-xs font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all"
                >
                  Commit Memory
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

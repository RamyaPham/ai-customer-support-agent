import { useState, useEffect } from "react";
import { RefreshCw, Activity, Clock, Zap, Layers, AlertTriangle } from "lucide-react";
import { getRuns, getTrace, type RunSummary, type TraceStep } from "../api";
import TraceStepCard from "./TraceStepCard";

export default function AdminDashboard() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [trace, setTrace] = useState<TraceStep[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchRuns = async () => {
    const data = await getRuns();
    setRuns(data);
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const selectRun = async (runId: string) => {
    setSelectedRun(runId);
    setLoading(true);
    const data = await getTrace(runId);
    setTrace(data);
    setLoading(false);
  };

  const totalTokens = trace.reduce((s, t) => s + t.tokens_in + t.tokens_out, 0);
  const totalLatency = trace.reduce((s, t) => s + t.latency_ms, 0);
  const failedSteps = trace.filter((t) => t.error || t.retries > 0);

  return (
    <div className="flex h-full">
      <div className="w-80 border-r border-slate-200 bg-white overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-indigo-500" />
            <h2 className="text-base font-semibold text-slate-800">Runs</h2>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{runs.length}</span>
          </div>
          <button
            onClick={fetchRuns}
            className="p-1.5 rounded-md text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
          >
            <RefreshCw size={14} />
          </button>
        </div>
        {runs.length === 0 && (
          <div className="text-center mt-16 px-4">
            <Activity size={32} className="mx-auto text-slate-300 mb-3" />
            <p className="text-sm text-slate-400">No runs yet</p>
            <p className="text-xs text-slate-300 mt-1">Send a message in Chat to create one</p>
          </div>
        )}
        {runs.map((r) => (
          <div
            key={r.run_id}
            onClick={() => selectRun(r.run_id)}
            className={`px-5 py-3.5 border-b border-slate-100 cursor-pointer transition-colors ${
              selectedRun === r.run_id
                ? "bg-indigo-50 border-l-3 border-l-indigo-500"
                : "hover:bg-slate-50"
            }`}
          >
            <div className="text-xs font-mono text-slate-500 truncate">{r.run_id.slice(0, 12)}...</div>
            <div className="flex gap-4 mt-1.5 text-[11px] text-slate-400">
              <span className="flex items-center gap-1">
                <Layers size={10} />
                {r.steps}
              </span>
              <span className="flex items-center gap-1">
                <Clock size={10} />
                {r.total_latency_ms.toFixed(0)}ms
              </span>
              <span className="flex items-center gap-1">
                <Zap size={10} />
                {r.total_tokens}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto bg-slate-50 p-6">
        {!selectedRun && (
          <div className="text-center mt-24">
            <div className="bg-slate-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Activity size={28} className="text-slate-400" />
            </div>
            <p className="text-slate-500 font-medium">Select a run to view its trace</p>
            <p className="text-xs text-slate-400 mt-1">Click a run in the sidebar to inspect tool I/O, latency, and tokens</p>
          </div>
        )}
        {selectedRun && (
          <>
            <div className="flex flex-wrap items-center gap-3 mb-5">
              <span className="font-mono text-sm text-slate-600 bg-white border border-slate-200 px-3 py-1 rounded-lg">
                {selectedRun.slice(0, 12)}...
              </span>
              <div className="flex gap-2">
                <span className="flex items-center gap-1.5 text-xs text-slate-500 bg-white border border-slate-200 px-2.5 py-1 rounded-lg">
                  <Layers size={12} className="text-indigo-400" />
                  {trace.length} steps
                </span>
                <span className="flex items-center gap-1.5 text-xs text-slate-500 bg-white border border-slate-200 px-2.5 py-1 rounded-lg">
                  <Clock size={12} className="text-indigo-400" />
                  {totalLatency.toFixed(0)}ms
                </span>
                <span className="flex items-center gap-1.5 text-xs text-slate-500 bg-white border border-slate-200 px-2.5 py-1 rounded-lg">
                  <Zap size={12} className="text-indigo-400" />
                  {totalTokens} tokens
                </span>
                {failedSteps.length > 0 && (
                  <span className="flex items-center gap-1.5 text-xs font-medium text-red-600 bg-red-50 border border-red-200 px-2.5 py-1 rounded-lg">
                    <AlertTriangle size={12} />
                    {failedSteps.length} failed
                  </span>
                )}
              </div>
            </div>
            {loading ? (
              <p className="text-slate-400 text-sm">Loading trace...</p>
            ) : (
              <div className="space-y-0">
                {trace.map((s, i) => (
                  <TraceStepCard key={i} step={s} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

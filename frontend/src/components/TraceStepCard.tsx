import { useState } from "react";
import { ChevronDown, ChevronRight, Bot, Wrench, AlertCircle, CheckCircle, Clock, Zap } from "lucide-react";
import type { TraceStep } from "../api";

interface Props {
  step: TraceStep;
}

const TYPE_CONFIG: Record<string, { Icon: typeof Bot; label: string; accent: string }> = {
  llm: { Icon: Bot, label: "LLM", accent: "text-violet-500 bg-violet-50" },
  tool: { Icon: Wrench, label: "Tool", accent: "text-blue-500 bg-blue-50" },
  error: { Icon: AlertCircle, label: "Error", accent: "text-red-500 bg-red-50" },
  decision: { Icon: CheckCircle, label: "Decision", accent: "text-emerald-500 bg-emerald-50" },
};

export default function TraceStepCard({ step }: Props) {
  const [open, setOpen] = useState(false);
  const config = TYPE_CONFIG[step.type] || TYPE_CONFIG.tool;
  const { Icon } = config;
  const hasError = !!step.error || step.retries > 0;

  return (
    <div
      className={`border rounded-xl mb-2 overflow-hidden transition-shadow ${
        hasError
          ? "border-red-300 bg-red-50/50 shadow-sm shadow-red-100"
          : "border-slate-200 bg-white hover:shadow-sm"
      }`}
    >
      <div
        className="flex items-center gap-3 px-4 py-3 cursor-pointer select-none"
        onClick={() => setOpen(!open)}
      >
        {open ? (
          <ChevronDown size={14} className="text-slate-400 shrink-0" />
        ) : (
          <ChevronRight size={14} className="text-slate-400 shrink-0" />
        )}
        <div className={`p-1.5 rounded-md ${hasError ? "bg-red-100" : config.accent.split(" ").slice(1).join(" ")}`}>
          <Icon size={14} className={hasError ? "text-red-500" : config.accent.split(" ")[0]} />
        </div>
        <span className="font-mono text-sm font-medium text-slate-700">{step.name}</span>
        <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${hasError ? "bg-red-100 text-red-600" : config.accent}`}>
          {config.label}
        </span>

        <div className="ml-auto flex items-center gap-3 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Clock size={11} />
            {step.latency_ms.toFixed(0)}ms
          </span>
          {(step.tokens_in > 0 || step.tokens_out > 0) && (
            <span className="flex items-center gap-1">
              <Zap size={11} />
              {step.tokens_in + step.tokens_out} tok
            </span>
          )}
          {step.retries > 0 && (
            <span className="text-red-500 font-semibold">{step.retries} retries</span>
          )}
        </div>
      </div>

      {open && (
        <div className="border-t border-slate-100 px-4 py-3 space-y-3 text-xs bg-slate-50/50">
          {step.input != null && (
            <div>
              <div className="font-semibold text-slate-500 mb-1 uppercase tracking-wider text-[10px]">Input</div>
              <pre className="bg-white border border-slate-200 p-3 rounded-lg overflow-x-auto max-h-48 text-slate-700">
                {typeof step.input === "string"
                  ? step.input
                  : JSON.stringify(step.input, null, 2)}
              </pre>
            </div>
          )}
          {step.output != null && (
            <div>
              <div className="font-semibold text-slate-500 mb-1 uppercase tracking-wider text-[10px]">Output</div>
              <pre className="bg-white border border-slate-200 p-3 rounded-lg overflow-x-auto max-h-48 text-slate-700">
                {typeof step.output === "string"
                  ? step.output
                  : JSON.stringify(step.output, null, 2)}
              </pre>
            </div>
          )}
          {step.error && (
            <div>
              <div className="font-semibold text-red-500 mb-1 uppercase tracking-wider text-[10px]">Error</div>
              <pre className="bg-red-50 border border-red-200 p-3 rounded-lg text-red-700">{step.error}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

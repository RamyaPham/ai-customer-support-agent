const API_BASE = "/api";

export interface TraceStep {
  step: number;
  type: string;
  name: string;
  input: unknown;
  output: unknown;
  latency_ms: number;
  tokens_in: number;
  tokens_out: number;
  retries: number;
  error: string | null;
}

export interface ChatResponse {
  reply: string;
  decision: "APPROVED" | "DENIED" | "ESCALATED" | "NEEDS_INFO" | null;
  trace: TraceStep[];
  run_id: string;
}

export interface RunSummary {
  run_id: string;
  steps: number;
  total_latency_ms: number;
  total_tokens: number;
}

export async function sendMessage(
  message: string,
  runId?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, run_id: runId }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function getRuns(): Promise<RunSummary[]> {
  const res = await fetch(`${API_BASE}/runs`);
  const data = await res.json();
  return data.runs;
}

export async function getTrace(runId: string): Promise<TraceStep[]> {
  const res = await fetch(`${API_BASE}/runs/${runId}/trace`);
  const data = await res.json();
  return data.trace;
}

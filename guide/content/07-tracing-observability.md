# Chapter 7: Tracing and Observability -- Seeing Inside the Black Box

## The Problem: AI Is Opaque

When a traditional application fails, you read the logs and see exactly what happened. When an AI agent fails, the LLM's reasoning is hidden inside a neural network. Did it misunderstand the customer? Did it call the wrong tool? Did the tool return unexpected data? Without tracing, you are debugging in the dark.

**Analogy:** Observability is the flight recorder (black box) on an airplane. You hope you never need it, but when something goes wrong, it is the difference between "we have no idea what happened" and "here is exactly where things went wrong, step by step."

## What We Trace

Every step of the agent loop is recorded as a `TraceStep`:

```python
# backend/app/models.py
class TraceStep(BaseModel):
    step: int              # Sequential step number
    type: str              # "llm" or "tool"
    name: str              # e.g., "agent_call" or "check_eligibility"
    input: Any = None      # What went in
    output: Any = None     # What came out
    latency_ms: float = 0  # How long it took
    tokens_in: int = 0     # Tokens sent (LLM calls only)
    tokens_out: int = 0    # Tokens received (LLM calls only)
    retries: int = 0       # How many retries were needed
    error: Optional[str]   # Error message if something failed
```

This captures everything you need to reconstruct what the agent did: what it thought, what tools it called, what data it received, how long each step took, and how many tokens it consumed.

## How Tracing Works

Here is the actual tracing context manager from our project:

```python
# backend/app/trace/tracer.py
TRACE_STORE: dict[str, list[TraceStep]] = defaultdict(list)
_current_run_id: ContextVar[str | None] = ContextVar(
    "_current_run_id", default=None
)

@contextmanager
def trace_step(step_no, type_, name, input_=None):
    start = time.perf_counter()
    box = {"output": None, "error": None, "retries": 0,
           "tokens_in": 0, "tokens_out": 0, "_step": None}
    try:
        yield box
    except Exception as e:
        box["error"] = str(e)
        raise
    finally:
        box["latency_ms"] = (time.perf_counter() - start) * 1000
        step = TraceStep(
            step=step_no, type=type_, name=name,
            input=input_, output=box["output"],
            error=box["error"], retries=box["retries"],
            latency_ms=round(box["latency_ms"], 2),
            tokens_in=box["tokens_in"], tokens_out=box["tokens_out"],
        )
        box["_step"] = step
        run_id = _current_run_id.get()
        if run_id:
            TRACE_STORE[run_id].append(step)
```

Key design decisions:

- **Context manager** (`with trace_step(...) as box`): Automatically captures timing even if an exception occurs. The `finally` block always runs.
- **TRACE_STORE**: A dictionary keyed by `run_id` (each conversation gets a unique ID). All trace steps for a conversation are stored together.
- **ContextVar**: A thread-safe way to track which conversation is active, so traces land in the right bucket even in a concurrent server.

## What You Can Answer With Traces

- "Why was this refund denied?" -- Look at the `check_eligibility` tool output in the trace.
- "Why did this request take 8 seconds?" -- Check `latency_ms` on each step to find the bottleneck.
- "How much did this conversation cost?" -- Sum `tokens_in` and `tokens_out` across all LLM steps.
- "Did the agent hallucinate?" -- Compare the LLM output in the trace with the tool results it received.

## Why This Matters

In production, you cannot watch every conversation. Traces are your eyes. They enable debugging, auditing, cost monitoring, and performance optimization. Without observability, you are operating an AI system blind.

## Key Takeaways

- AI agents are opaque by nature -- tracing makes their behavior visible and auditable.
- Every agent step (LLM call, tool execution) should be recorded with timing, I/O, and error data.
- Context managers ensure tracing captures data even when errors occur.
- Traces answer critical questions: why was this denied, what took so long, how much did it cost.
- Observability is not optional in production AI systems -- it is how you debug, audit, and optimize.

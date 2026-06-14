# Chapter 8: Project Architecture -- Full Walkthrough

## Why We Chose This Architecture

Most AI chatbots let the language model make decisions. That is dangerous for a refund system -- an LLM can be persuaded, confused, or tricked into approving refunds that violate policy. Our architecture separates **language** from **decisions**: the LLM talks to the customer and orchestrates tool calls, but a deterministic Python engine computes the actual APPROVE / DENY / ESCALATE verdict. No amount of clever prompting can override a Python `if` statement.

## How It Works In Our Project

The system has five layers, each with a single responsibility:

```
 User (Browser)
   |
   v
 React 19 + Tailwind v4 (frontend/src/)
   |  POST /api/chat  { message, run_id }
   v
 FastAPI (backend/app/main.py)
   |  Invokes LangGraph compiled graph
   v
 LangGraph Agent Loop (backend/app/agent/graph.py)
   |  agent -> tools_condition -> tools -> extract -> agent
   v
 LangChain Tools (backend/app/tools/tools.py)
   |  lookup_customer, list_orders, get_order,
   |  get_refund_policy, check_eligibility,
   |  issue_refund, escalate_to_human
   v
 Deterministic Eligibility Engine (backend/app/engine/)
   |  Pure Python rules -- no LLM involved
   v
 Response: { reply, decision, trace[], run_id }
```

### Walking Through a Refund Request Step by Step

**1. User sends a message.** The React `ChatWindow` component calls `sendMessage()` from `api.ts`, which POSTs to `/api/chat`.

**2. FastAPI receives the request.** `main.py` creates or retrieves a session, prepends the system prompt, and invokes the LangGraph agent:

```python
state = agent_graph.invoke({
    "messages": history,
    "trace": [],
    "decision": None,
    "run_id": run_id,
})
```

**3. The agent node runs.** The LLM reads the conversation, decides it needs customer data, and emits a tool call for `lookup_customer`.

**4. LangGraph routes to tools.** The `tools_condition` edge detects the tool call and routes to the `tools` node, which executes `lookup_customer` against our seed database.

**5. The extract node scans for a verdict.** After each tool execution, the `extract_decision` node checks whether the conversation contains APPROVED, DENIED, ESCALATED, or NEEDS_INFO.

**6. The loop continues.** Control returns to the agent node. The LLM now has customer data and calls `list_orders`, then `check_eligibility`. The eligibility engine runs deterministic Python rules and returns a structured `EligibilityResult`.

**7. The agent acts on the verdict.** If the engine returned APPROVED, the LLM calls `issue_refund`. Critically, `issue_refund` **re-validates eligibility internally** before executing -- this is defense in depth. If the engine returned DENIED, the LLM explains why, citing the policy.

**8. The response returns.** FastAPI packages the LLM's final reply, the decision enum, and the full trace array into a `ChatResponse` and sends it back to the frontend.

**9. The frontend renders.** `ChatWindow` displays the reply and a `DecisionBadge` (APPROVED in green, DENIED in red). The `AdminDashboard` lets operators inspect every trace step -- tool inputs, outputs, latency, and token counts.

### The Golden Rule

Facts come from tools, verdicts come from code, the LLM only communicates. This rule is enforced at every layer: the hardened system prompt tells the LLM not to decide on its own, the tools refuse to act without engine approval, and the engine ignores anything the LLM says -- it only reads structured data.

## Key Takeaways

- **Separation of concerns**: language handling (LLM) vs. business logic (engine) vs. transport (API) vs. presentation (React).
- **Defense in depth**: three independent layers prevent unauthorized refunds.
- **Observability built in**: every node emits a `TraceStep`, so the admin dashboard shows exactly what happened and why.
- **The architecture is the security model**: the LLM physically cannot bypass the eligibility engine, no matter what a user types.

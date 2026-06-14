# Full Session Log — AI Customer Support Challenge
**Date:** June 10, 2026
**Author:** Harsha
**Project:** AI Customer Support Agent — E-commerce Refund Automation

---

## Timeline of Everything We Did

### Session 1 — Workspace Setup & Challenge Planning

#### 1.1 Workspace Initialization
- Created project structure, virtual environment, `.gitignore`, session logger
- Created `logs/session_logger.py` — shared CLI tool for structured session logging
- Created `docs/` folder for planning documents

#### 1.2 Challenge Received & Analyzed
- Build a fully functional web app: AI Customer Support Agent that processes/denies e-commerce refunds
- 3 components: (1) Synthetic CRM data + refund policy, (2) Backend with agent loop, (3) Frontend with chat + admin dashboard
- Must handle edge cases, prompt injection, policy violations
- Deliverable: working repo + 5-min Loom video

#### 1.3 Stack Decision
- **Backend:** FastAPI + LangGraph + Groq/OpenAI function-calling LLM
- **Frontend:** React + Tailwind
- **Data:** JSON synthetic CRM + markdown refund policy
- **Why local-first:** No cloud required; simpler to demo and run

---

### Session 2 — Research & Planning

#### 2.1 Technology Choices
| Layer | Choice | Why |
|---|---|---|
| Python packages | PyPI versions for all deps | FastAPI 0.136.3, Pydantic 2.13.4, LangGraph 1.2.4 |
| LLM model | `llama-3.1-8b-instant` (Groq, free) | Fast, free, strong tool-calling |
| Fallback LLM | `gpt-4o-mini` (OpenAI) | Reliable paid alternative |

---

### Session 3 — Implementation

#### 3.1 Backend Built
- `app/main.py` — FastAPI app with `/api/chat`, `/api/health`, `/api/runs` endpoints
- `app/agent/graph.py` — LangGraph agent loop (agent → tools → extract → agent)
- `app/agent/llm.py` — Swappable LLM client (Groq/OpenAI via env var)
- `app/engine/eligibility.py` — Deterministic verdict engine (APPROVE/DENY/ESCALATE)
- `app/tools/tools.py` — 7 LangChain tools
- `app/trace/tracer.py` — Per-step trace capture
- `data/seed/customers.json` — 15 customers with edge-case orders

#### 3.2 Frontend Built
- `src/App.tsx` — Tab navigation (Chat / Admin)
- `src/components/ChatWindow.tsx` — Customer chat interface
- `src/components/AdminDashboard.tsx` — Trace timeline with tool I/O, latency, tokens

#### 3.3 Tests Written
- 71 tests covering eligibility engine, adversarial prompts, end-to-end flows

---

### Session 4 — Verification

#### 4.1 All Systems Working
- Backend starts clean on port 8000
- Frontend proxies to backend automatically
- All 6 policy rules (R1–R6) verified working
- Prompt injection attempts correctly blocked
- Trace captures tool I/O, latency, token counts per step

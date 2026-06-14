# AI Customer Support Agent — E-commerce Refund Automation

An AI-powered customer support agent that autonomously processes refund requests using a deterministic eligibility engine, LangGraph agent loop, and hardened system prompt.

## Architecture

```
User → React UI → FastAPI → LangGraph Agent → Tools → Eligibility Engine → Response
                                                          ↑
                                               Deterministic Python code
                                               (verdict cannot be overridden)
```

**Key principle:** The LLM handles language and orchestration. The **verdict (APPROVE/DENY/ESCALATE) is computed by deterministic Python code** that cannot be overridden by prompt injection.

---

## Prerequisites

- **Python 3.12+**
- **Node.js 20.19+ or 22+** (v24 LTS recommended)
- **uv** (Python package manager)
- **An LLM API key** — Groq (free) or OpenAI

---

## Setup (after cloning)

### 1. Install uv

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Then restart your terminal so `uv` is on PATH.

### 2. Backend setup

```bash
cd backend

# Install Python dependencies (creates .venv automatically)
uv sync

# Copy environment config
cp .env.example .env   # Mac/Linux
copy .env.example .env  # Windows
```

Edit `.env` and set your LLM provider. **Groq is free** (sign up at https://console.groq.com):

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Or use OpenAI (paid):
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

```bash
# Verify seed data loads correctly
uv run python scripts/seed_db.py

# Start the backend server
uv run uvicorn app.main:app --reload --port 8000
```

The backend runs at **http://localhost:8000**.

### 3. Frontend setup

Open a **new terminal**:

```bash
cd frontend
npm install
npm run dev
```

**Windows only** — if you get a script execution error:
```cmd
# Use Command Prompt (cmd.exe) instead of PowerShell, or run:
node node_modules\.bin\vite
```

The frontend runs at **http://localhost:5173**. It proxies `/api` requests to the backend automatically.

### 4. Open the app

Go to **http://localhost:5173** in your browser.

- **Chat tab** — customer-facing chat for refund requests
- **Admin tab** — trace dashboard showing tool I/O, latency, tokens

### 5. Run tests

```bash
cd backend
uv run pytest tests/ -v
```

All 71 tests should pass.

---

## Learning Guide

An interactive learning portal is included for anyone new to AI/LLM concepts.

### React app (recommended)

```bash
cd guide/app
npm install
npm run dev
```

Open **http://localhost:3000**

### Static HTML (no setup needed)

```bash
open guide/index.html
```

### Topics covered

| # | Chapter | Category |
|---|---|---|
| 1 | What is AI? | Core Concept |
| 2 | How LLMs Work | Core Concept |
| 3 | Tool Calling | Core Concept |
| 4 | Agent Loops | Core Concept |
| 5 | Prompt Engineering | Core Concept |
| 6 | Deterministic Engines | Core Concept |
| 7 | Tracing & Observability | Core Concept |
| 8 | Project Architecture | Walkthrough |
| 9 | FastAPI | Tech Reference |
| 10 | LangGraph | Tech Reference |
| 11 | LangChain Tools | Tech Reference |
| 12 | Pydantic | Tech Reference |
| 13 | React & Tailwind | Tech Reference |
| 14 | Defense in Depth | Tech Reference |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | `groq` or `openai` |
| `GROQ_API_KEY` | — | Required if using Groq (free) |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Groq model ID |
| `OPENAI_API_KEY` | — | Required if using OpenAI |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model ID |
| `REFUND_WINDOW_DAYS` | `30` | Refund eligibility window |
| `ESCALATION_THRESHOLD` | `500` | Amount requiring human approval |

---

## Policy Rules

| Rule | Description | Verdict |
|---|---|---|
| R1 | Final-sale items | DENIED |
| R2 | Amount > $500 | ESCALATED |
| R3 | Past 30-day window | DENIED |
| R4 | Wrong customer | DENIED |
| R5 | Already refunded | DENIED |
| R6 | Damaged overrides R1 | APPROVED (if other rules pass) |

---

## Seed Data Edge Cases

| Customer | Order | Edge Case |
|---|---|---|
| CUST-001 / Alice | ORD-1002 | Final sale item (R1) |
| CUST-002 / Bob | ORD-2001 | $529.98 order (R2 escalation) |
| CUST-003 / Carol | ORD-3001 | Delivered >30 days ago (R3) |
| CUST-004 / David | ORD-4001 | Already refunded (R5) |
| CUST-006 / Frank | ORD-6001 | Damaged + final sale (R6 override) |
| CUST-011 / Karen | ORD-11001 | $650 order (R2 escalation) |

---

## Project Structure

```
AI Customer Support/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app + routes
│   │   ├── models.py              # Pydantic models
│   │   ├── db.py                  # In-memory JSON data store
│   │   ├── config.py              # Env-driven settings
│   │   ├── agent/
│   │   │   ├── graph.py           # LangGraph agent loop
│   │   │   ├── llm.py             # Swappable LLM client
│   │   │   └── prompts.py         # Hardened system prompt
│   │   ├── engine/
│   │   │   └── eligibility.py     # Deterministic verdict engine
│   │   ├── policy/
│   │   │   └── refund_policy.md   # Rules R1-R6
│   │   ├── tools/
│   │   │   └── tools.py           # 7 LangChain tools
│   │   └── trace/
│   │       └── tracer.py          # TraceStep capture
│   ├── data/seed/
│   │   └── customers.json         # 15 customers + orders
│   ├── tests/                     # 71 tests
│   ├── pyproject.toml             # uv-managed dependencies
│   └── uv.lock                    # Locked dependency versions
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Tab nav (Chat / Admin)
│   │   ├── api.ts                 # Typed API client
│   │   └── components/            # ChatWindow, AdminDashboard, etc.
│   ├── vite.config.ts
│   └── package.json
├── guide/                         # Learning portal
│   ├── content/                   # 14 markdown chapters
│   ├── app/                       # React learning app (port 3000)
│   └── index.html                 # Static HTML fallback
├── docs/                          # Requirements + design docs
└── README.md                      # This file
```

---

## Loom Recording Script (≤ 5 min)

1. **(0:00–0:45)** Architecture: Data → Engine → Tools → Agent → API → UI
2. **(0:45–2:00)** Happy path: valid refund → APPROVED → trace timeline
3. **(2:00–3:00)** Resilience: prompt injection + >$500 → DENIED/ESCALATED
4. **(3:00–4:00)** Trace deep-dive: tool I/O, latency, tokens
5. **(4:00–5:00)** What I'd add before prod

# Chapter 9: FastAPI -- The Backend Framework

## Why We Chose This

FastAPI is a modern Python web framework built for APIs. It is fast (async-capable), auto-generates API documentation, and uses Python type hints for request validation. For an AI agent backend that needs to accept chat messages, invoke an LLM, and return structured JSON, FastAPI is the natural fit. It is also the de facto standard in the Python AI/ML ecosystem.

## How It Works In Our Project

Our entire backend API lives in one file: `backend/app/main.py`. It exposes three endpoints.

### App Setup and CORS

```python
app = FastAPI(title="AI Refund Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

CORS (Cross-Origin Resource Sharing) is a browser security feature. Our React frontend runs on port 5173 and our backend on port 8000 -- different origins. Without the CORS middleware, the browser would block the frontend from calling our API.

### Endpoint 1: Health Check

```python
@app.get("/api/health")
def health():
    return {"status": "ok"}
```

A simple endpoint that returns `{"status": "ok"}`. Used by monitoring, load balancers, and deployment pipelines to verify the server is alive.

### Endpoint 2: Chat (the main one)

```python
class ChatRequest(BaseModel):
    message: str
    run_id: str | None = None

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    run_id = payload.run_id or str(uuid.uuid4())
    # ... invoke agent_graph, return ChatResponse
```

The `ChatRequest` model uses Pydantic (covered in Chapter 12) to validate that every request has a `message` string. The optional `run_id` lets the frontend maintain a conversation session. FastAPI automatically returns a 422 error if the request body is malformed -- no manual validation code needed.

### Endpoint 3: Observability

```python
@app.get("/api/runs/{run_id}/trace")
def get_trace(run_id: str):
    return {"run_id": run_id, "trace": [s.model_dump() for s in TRACE_STORE.get(run_id, [])]}

@app.get("/api/runs")
def list_runs():
    return {"runs": [{"run_id": rid, "steps": len(steps), ...} for rid, steps in TRACE_STORE.items()]}
```

These endpoints power the Admin Dashboard. `/api/runs` lists all conversation sessions with summary stats (step count, total latency, token usage). `/api/runs/{run_id}/trace` returns the full trace for a specific session so operators can inspect exactly what the agent did.

### Error Handling

The chat endpoint wraps the agent invocation in a try/except and maps common LLM errors (missing API key, quota exceeded, invalid key) to appropriate HTTP status codes with human-readable messages. This saves frontend developers from debugging cryptic 500 errors.

## Key Takeaways

- **FastAPI uses decorators** (`@app.get`, `@app.post`) to map Python functions to HTTP endpoints.
- **Pydantic models** validate request/response shapes automatically.
- **CORS middleware** is required when frontend and backend run on different ports.
- **Three endpoints** handle everything: health checks, chat conversations, and observability data.

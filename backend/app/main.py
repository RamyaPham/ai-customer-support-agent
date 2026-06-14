import os
import uuid
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.models import ChatResponse, TraceStep
from app.agent.graph import agent_graph, AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.trace.tracer import TRACE_STORE, set_current_run

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Refund Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: dict[str, list] = {}


class ChatRequest(BaseModel):
    message: str
    run_id: str | None = None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    run_id = payload.run_id or str(uuid.uuid4())
    set_current_run(run_id)

    from langchain_core.messages import HumanMessage, SystemMessage

    history = SESSIONS.get(run_id, [])
    if not history:
        history = [SystemMessage(content=SYSTEM_PROMPT)]
    history.append(HumanMessage(content=payload.message))

    TRACE_STORE.pop(run_id, None)

    try:
        state = agent_graph.invoke({
            "messages": history,
            "trace": [],
            "decision": None,
            "run_id": run_id,
        })
    except Exception as e:
        error_msg = str(e)
        logger.error("Agent invocation failed: %s", error_msg)
        if "Missing credentials" in error_msg or "api_key" in error_msg.lower():
            raise HTTPException(status_code=503, detail="LLM API key not configured. Set GROQ_API_KEY or OPENAI_API_KEY in backend/.env")
        if "insufficient_quota" in error_msg or "exceeded" in error_msg.lower():
            raise HTTPException(status_code=503, detail="LLM API quota exceeded. Check your plan and billing.")
        if "401" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
            raise HTTPException(status_code=503, detail="LLM API key is invalid. Check your key in backend/.env")
        raise HTTPException(status_code=500, detail=f"Agent error: {error_msg}")

    SESSIONS[run_id] = state["messages"]

    last_content = state["messages"][-1].content
    if isinstance(last_content, list):
        last_content = " ".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in last_content
        )

    return ChatResponse(
        reply=last_content,
        decision=state.get("decision"),
        trace=TRACE_STORE.get(run_id, []),
        run_id=run_id,
    )


@app.get("/api/runs/{run_id}/trace")
def get_trace(run_id: str):
    return {
        "run_id": run_id,
        "trace": [s.model_dump() for s in TRACE_STORE.get(run_id, [])],
    }


@app.get("/api/runs")
def list_runs():
    return {
        "runs": [
            {
                "run_id": rid,
                "steps": len(steps),
                "total_latency_ms": round(sum(s.latency_ms for s in steps), 2),
                "total_tokens": sum(s.tokens_in + s.tokens_out for s in steps),
            }
            for rid, steps in TRACE_STORE.items()
        ]
    }

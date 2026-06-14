# Development Notes — AI Customer Support Challenge

## Session Logging

Every conversation in this workspace is logged to `logs/sessions/`.
The logger script is at `logs/session_logger.py`.

```bash
python3 logs/session_logger.py start
python3 logs/session_logger.py decision "what was decided and why"
python3 logs/session_logger.py code "what changed and why"
python3 logs/session_logger.py summary "what was accomplished"
```

---

## Project Context

- **Project**: AI Customer Support Agent — E-commerce Refund Automation
- **Stack**: Python + FastAPI + LangGraph + React
- **LLM**: Groq (free) or OpenAI via LangChain

---

## General Rules

- Always explain reasoning before implementing.
- Log every non-trivial decision with its rationale.
- Keep session logs human-readable and well-structured.
- Activate the virtual environment before running Python: `source venv/bin/activate`

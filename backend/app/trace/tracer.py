import time
from collections import defaultdict
from contextvars import ContextVar
from contextlib import contextmanager
from app.models import TraceStep

TRACE_STORE: dict[str, list[TraceStep]] = defaultdict(list)

_current_run_id: ContextVar[str | None] = ContextVar("_current_run_id", default=None)


def set_current_run(run_id: str):
    _current_run_id.set(run_id)


@contextmanager
def trace_step(step_no: int, type_: str, name: str, input_=None):
    start = time.perf_counter()
    box = {
        "output": None,
        "error": None,
        "retries": 0,
        "tokens_in": 0,
        "tokens_out": 0,
        "_step": None,
    }
    try:
        yield box
    except Exception as e:
        box["error"] = str(e)
        raise
    finally:
        box["latency_ms"] = (time.perf_counter() - start) * 1000
        step = TraceStep(
            step=step_no,
            type=type_,
            name=name,
            input=input_,
            output=box["output"],
            error=box["error"],
            retries=box["retries"],
            latency_ms=round(box["latency_ms"], 2),
            tokens_in=box["tokens_in"],
            tokens_out=box["tokens_out"],
        )
        box["_step"] = step
        run_id = _current_run_id.get()
        if run_id:
            TRACE_STORE[run_id].append(step)

#!/usr/bin/env python3
"""
Session Logger — Auto-creates and appends structured session logs under logs/sessions/.
Used by workspace hooks and can be called directly.

Usage:
    python3 logs/session_logger.py start              # Start a new session log
    python3 logs/session_logger.py thought "message"  # Append a thought
    python3 logs/session_logger.py decision "message" # Append a decision
    python3 logs/session_logger.py summary "message"  # Append session summary
    python3 logs/session_logger.py latest             # Print path of latest log
"""

import sys
import os
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path(__file__).parent / "sessions"


def get_latest_session() -> Path | None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    logs = sorted(SESSIONS_DIR.glob("session_*.md"), reverse=True)
    return logs[0] if logs else None


def start_session() -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_file = SESSIONS_DIR / f"session_{ts}.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""# Session Log — {now}

**Workspace:** AI Customer Support Challenge  
**Goal:** _Fill in task goal for this session_

---

## Ideas & Reasoning

## Decisions Made

## Code Changes

## Open Questions

---
"""
    session_file.write_text(content)
    print(f"[session-logger] Started: {session_file}")
    return session_file


def append_entry(entry_type: str, message: str) -> None:
    session = get_latest_session()
    if not session:
        session = start_session()
    ts = datetime.now().strftime("%H:%M:%S")
    tag = entry_type.upper()
    entry = f"\n### {ts} — [{tag}]\n{message}\n"
    with session.open("a") as f:
        f.write(entry)
    print(f"[session-logger] Appended [{tag}] to {session.name}")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] == "start":
        start_session()
    elif args[0] == "latest":
        log = get_latest_session()
        print(log or "No session log found.")
    elif args[0] in ("thought", "decision", "summary", "code", "idea"):
        message = " ".join(args[1:]) if len(args) > 1 else "(no message)"
        append_entry(args[0], message)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

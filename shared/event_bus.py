"""
Shared Event Bus for StudySync Ecosystem.
Allows all 6 agents to log structured events and listen or query past events.
Provides data continuity between QuizGen, CodeMentor, PerformanceAnalyst,
StudyPlanner, TutorGPT, and RevisionGPT.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_EVENT_LOG = Path(__file__).parent.parent / "data" / "events.jsonl"


class EventBus:
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or DEFAULT_EVENT_LOG
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()

    def log_event(
        self,
        event_type: str,
        student_id: str,
        payload: Dict[str, Any],
        source_agent: str
    ) -> Dict[str, Any]:
        """Record an event to the shared event ledger."""
        record = {
            "timestamp": time.time(),
            "iso_time": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "student_id": student_id,
            "source_agent": source_agent,
            "payload": payload
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return record

    def get_events(
        self,
        student_id: Optional[str] = None,
        event_type: Optional[str] = None,
        source_agent: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve and filter past events."""
        if not self.log_path.exists():
            return []

        results = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                    if student_id and ev.get("student_id") != student_id:
                        continue
                    if event_type and ev.get("event_type") != event_type:
                        continue
                    if source_agent and ev.get("source_agent") != source_agent:
                        continue
                    results.append(ev)
                except Exception:
                    continue

        return results[-limit:]

    def clear(self):
        """Reset the event log."""
        if self.log_path.exists():
            self.log_path.write_text("", encoding="utf-8")


_default_bus = None

def get_event_bus() -> EventBus:
    global _default_bus
    if _default_bus is None:
        _default_bus = EventBus()
    return _default_bus

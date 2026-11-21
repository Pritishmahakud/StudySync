"""
Shared Event Bus for StudySync Ecosystem.
Allows all 6 agents to log structured events and listen/react to real-time events.
Implements a pub/sub event-driven architecture connecting:
1. TutorGPT (AI Teaching Agent)
2. QuizGen AI (Assessment Agent)
3. CodeMentor AI (Programming Agent)
4. StudyPlanner AI (Planning Agent)
5. PerformanceAnalyst AI (Analytics Agent)
6. RevisionGPT (Revision Agent)
"""

from __future__ import annotations

import fnmatch
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("StudySync.EventBus")

DEFAULT_EVENT_LOG = Path(__file__).parent.parent / "data" / "events.jsonl"

EventListener = Callable[[Dict[str, Any]], None]


class EventBus:
    """
    Event-driven multi-agent pub/sub event broker.
    Supports persistent append-only JSONL event logging, wildcard topic subscriptions,
    and automatic real-time event dispatching across agents.
    """

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or DEFAULT_EVENT_LOG
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()

        # Subscription map: pattern -> {sub_id: callback}
        self._subscribers: Dict[str, Dict[str, EventListener]] = {}

    def subscribe(
        self,
        event_pattern: str,
        callback: EventListener
    ) -> str:
        """
        Register an event listener for a specific event type or wildcard pattern.
        Examples: 'quiz.completed', 'weak_concept.*', '*'
        Returns a unique subscription ID for subsequent unsubscription.
        """
        sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        if event_pattern not in self._subscribers:
            self._subscribers[event_pattern] = {}
        self._subscribers[event_pattern][sub_id] = callback
        logger.info(f"Registered subscriber {sub_id} for pattern '{event_pattern}'")
        return sub_id

    def unsubscribe(self, sub_id: str) -> bool:
        """Remove a subscription by its ID."""
        for pattern, subs in self._subscribers.items():
            if sub_id in subs:
                del subs[sub_id]
                logger.info(f"Unsubscribed {sub_id} from '{pattern}'")
                return True
        return False

    def publish(
        self,
        event_type: str,
        student_id: str,
        payload: Dict[str, Any],
        source_agent: str
    ) -> Dict[str, Any]:
        """
        Publish an event to the shared event ledger AND immediately dispatch
        to all matching registered listener callbacks.
        """
        record = {
            "timestamp": time.time(),
            "iso_time": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "student_id": student_id,
            "source_agent": source_agent,
            "payload": payload or {}
        }

        # 1. Append to persistent JSONL log
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist event to {self.log_path}: {e}")

        # 2. Reactive Dispatch to all matching subscribers
        self._dispatch(record)

        return record

    def log_event(
        self,
        event_type: str,
        student_id: str,
        payload: Dict[str, Any],
        source_agent: str
    ) -> Dict[str, Any]:
        """
        Alias for publish to preserve backward compatibility with existing agent code,
        ensuring all logged events trigger registered subscribers.
        """
        return self.publish(
            event_type=event_type,
            student_id=student_id,
            payload=payload,
            source_agent=source_agent
        )

    def _dispatch(self, event_record: Dict[str, Any]) -> None:
        """Deliver event to all matching subscriber callbacks with error isolation."""
        event_type = event_record.get("event_type", "")
        listeners_to_call: List[EventListener] = []

        for pattern, subs in self._subscribers.items():
            if pattern == "*" or fnmatch.fnmatch(event_type, pattern) or pattern == event_type:
                listeners_to_call.extend(subs.values())

        for callback in listeners_to_call:
            try:
                callback(event_record)
            except Exception as e:
                logger.error(
                    f"Listener error in {callback.__name__ if hasattr(callback, '__name__') else callback} "
                    f"handling {event_type}: {e}",
                    exc_info=True
                )

    def get_events(
        self,
        student_id: Optional[str] = None,
        event_type: Optional[str] = None,
        source_agent: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve and filter past events from the append-only ledger."""
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
                    if event_type and not (ev.get("event_type") == event_type or fnmatch.fnmatch(ev.get("event_type", ""), event_type)):
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


_default_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    global _default_bus
    if _default_bus is None:
        _default_bus = EventBus()
    return _default_bus

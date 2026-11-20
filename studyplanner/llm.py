"""LLM layer for StudyPlanner AI, routed via StudySync shared provider."""

from __future__ import annotations

import json
from datetime import date

from shared.llm_provider import ask


def parse_request(text: str, today: date) -> dict | None:
    system = (f"Today is {today}. Extract a study-planning request. Reply with ONLY JSON: "
              '{"subjects":[{"name":str,"exam_date":"YYYY-MM-DD","difficulty":1-5}],'
              '"weekday_hours":number,"weekend_hours":number}. No prose, no markdown.')
    out = ask(system=system, user=text)
    if not out:
        return None
    try:
        return json.loads(out.replace("```json", "").replace("```", "").strip())
    except json.JSONDecodeError:
        return None


def explain_plan(plan: dict, profile_note: str = "") -> str:
    hours = plan.get("hours_by_subject", {})
    system = ("You are a friendly study coach. In under 120 words, explain why this plan is "
              "ordered the way it is (deadlines, weak subjects, revision before exams). "
              "Be concrete and encouraging.")
    prompt = json.dumps({"hours_by_subject": hours, "warnings": plan.get("warnings", []),
                         "note": profile_note, "first_sessions": plan.get("sessions", [])[:8]}, default=str)
    out = ask(system=system, user=prompt)
    if out and len(out.strip()) > 20:
        return out
    top = sorted(hours.items(), key=lambda x: -x[1])
    msg = "Your plan gives the most time to " + ", ".join(f"{k} ({v} h)" for k, v in top[:3]) + \
          ". Subjects with nearer exams and weaker scores get priority, and the last few days " \
          "before each exam are reserved for revision."
    if plan.get("warnings"):
        msg += " Warning: " + " ".join(plan["warnings"])
    return msg

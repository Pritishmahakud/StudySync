"""Core scheduling algorithm: deadline-aware, weakness-aware greedy allocation."""

from collections import defaultdict
from datetime import timedelta
from .models import PlanRequest, Plan, Session, Subject, AnalyticsFeedback

STUDY_SHARE = 0.75       # 75% of a subject's hours are first-pass study
REVISE_SHARE = 0.25      # 25% are revision (scheduled mostly in the revision window)


def total_need(s: Subject) -> float:
    base = s.est_hours if s.est_hours else s.difficulty * 5
    return base * (1 + 0.5 * s.weakness)          # weak subjects need more time


def build_plan(req: PlanRequest) -> Plan:
    blk = req.block_minutes / 60
    study_left = {s.name: max(total_need(s) * STUDY_SHARE - s.done_hours, 0) for s in req.subjects}
    revise_left = {s.name: total_need(s) * REVISE_SHARE for s in req.subjects}
    subj = {s.name: s for s in req.subjects}
    concept_idx = defaultdict(int)

    last_exam = max(s.exam_date for s in req.subjects)
    raw = []                                       # (date, subject, kind, focus) per block
    day = req.start_date
    while day < last_exam:
        cap = 0 if day in req.availability.days_off else (
            req.availability.weekend_hours if day.weekday() >= 5 else req.availability.weekday_hours)
        prev = None
        for _ in range(int(cap / blk)):
            best, best_score, best_kind = None, 0, None
            for s in req.subjects:
                days_left = (s.exam_date - day).days
                if days_left < 1:
                    continue
                in_window = days_left <= req.revision_window
                if in_window and revise_left[s.name] > 0:
                    kind, left = "revise", revise_left[s.name]
                elif study_left[s.name] > 0:
                    kind, left = "study", study_left[s.name]
                else:
                    continue
                score = left / days_left * (1 + 0.5 * s.weakness)
                if s.name == prev:
                    score *= 1.1                   # small bonus -> longer focused sessions, less switching
                if score > best_score:
                    best, best_score, best_kind = s, score, kind
            if best is None:
                break
            pool = revise_left if best_kind == "revise" else study_left
            pool[best.name] -= blk
            focus = None
            if best.weak_concepts and (best_kind == "revise" or best.weakness > 0.3):
                focus = best.weak_concepts[concept_idx[best.name] % len(best.weak_concepts)]
                concept_idx[best.name] += 1
            raw.append((day, best.name, best_kind, focus))
            prev = best.name
        day += timedelta(days=1)

    # merge consecutive identical blocks into sessions
    sessions: list[Session] = []
    for d, name, kind, focus in raw:
        if sessions and (sessions[-1].date, sessions[-1].subject, sessions[-1].kind, sessions[-1].focus) == (d, name, kind, focus):
            sessions[-1].minutes += req.block_minutes
        else:
            sessions.append(Session(date=d, subject=name, minutes=req.block_minutes, kind=kind, focus=focus))

    warnings = []
    for s in req.subjects:
        short = study_left[s.name] + revise_left[s.name]
        if short > 0.01:
            warnings.append(f"{s.name}: short by {short:.1f} h before {s.exam_date}. "
                            f"Add more daily hours or reduce scope.")
    hours = defaultdict(float)
    for x in sessions:
        hours[x.subject] += x.minutes / 60
    return Plan(student_id=req.student_id, sessions=sessions, warnings=warnings,
                hours_by_subject={k: round(v, 1) for k, v in hours.items()})


def apply_analytics(req: PlanRequest, fb: AnalyticsFeedback) -> PlanRequest:
    """Adaptive step: convert quiz scores into weakness, then the plan is rebuilt."""
    for s in req.subjects:
        if s.name in fb.subject_scores:
            s.weakness = round(1 - fb.subject_scores[s.name] / 100, 2)
        if s.name in fb.weak_concepts:
            s.weak_concepts = fb.weak_concepts[s.name]
    return req


def replan(req: PlanRequest, fb: AnalyticsFeedback | None = None, new_start=None,
           done: dict[str, float] | None = None) -> Plan:
    """Rebuild from a new start date, crediting completed hours and analytics feedback."""
    if fb:
        req = apply_analytics(req, fb)
    for s in req.subjects:
        s.done_hours += (done or {}).get(s.name, 0)
    if new_start:
        req.start_date = new_start
    return build_plan(req)

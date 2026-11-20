"""CodeMentorAgent - Member 3 Programming Agent for StudySync."""

from __future__ import annotations

import uuid
from typing import Any

from shared.event_bus import get_event_bus
from . import prompts
from .config import get_settings
from .executor import check_syntax, run_code, run_tests, SUPPORTED_LANGUAGES
from .llm import LLMClient, build_llm, extract_json

LEVELS = ("beginner", "intermediate", "advanced")


class CodeMentorAgent:
    """Programming agent: explain code, detect errors, generate exercises, review solutions."""

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or build_llm()
        self.settings = get_settings()
        self._exercises: dict[str, dict] = {}
        self.event_bus = get_event_bus()

    def _ask_json(self, user_prompt: str) -> dict:
        raw = self.llm.complete(prompts.BASE_SYSTEM, user_prompt, max_tokens=self.settings.max_tokens)
        try:
            return extract_json(raw)
        except Exception:
            retry = user_prompt + "\n\nYour previous reply was not valid JSON. Reply again with ONLY the JSON object."
            try:
                return extract_json(self.llm.complete(prompts.BASE_SYSTEM, retry, max_tokens=self.settings.max_tokens))
            except Exception:
                # Fallback to template
                return {
                    "summary": "Core algorithmic execution pattern.",
                    "step_by_step": [{"lines": "1-5", "explanation": "Initializes and processes inputs sequentially."}],
                    "key_concepts": ["control flow", "data structures"],
                    "time_complexity": "O(n)",
                    "space_complexity": "O(1)",
                    "example_walkthrough": "Processes input elements one by one.",
                    "common_mistakes": ["Index out of range", "Off-by-one boundary checks"]
                }

    @staticmethod
    def _lang(language: str) -> str:
        return (language or "python").strip().lower()

    def explain_code(self, code: str, language: str = "python", level: str = "beginner") -> dict:
        level = level if level in LEVELS else "beginner"
        language = self._lang(language)
        result = self._ask_json(prompts.EXPLAIN.format(code=code, language=language, level=level))
        result.update({"language": language, "level": level})
        return result

    def detect_errors(self, code: str, language: str = "python", run: bool = True, stdin: str = "") -> dict:
        language = self._lang(language)
        context, execution = [], None

        syntax = check_syntax(code, language)
        if syntax:
            context.append(f"Syntax error at line {syntax['line']}: {syntax['message']}")
        elif run and language in SUPPORTED_LANGUAGES:
            execution = run_code(code, language, stdin=stdin)
            if execution.timed_out:
                context.append("Execution timed out - likely an infinite loop or very slow algorithm.")
            elif not execution.ok:
                context.append(f"Runtime error (exit {execution.exit_code}):\n{execution.stderr[-1500:]}")
            else:
                context.append("Code ran without crashing. Output:\n" + (execution.stdout[:800] or "(no output)"))
        else:
            context.append("No automated checks were run.")

        result = self._ask_json(prompts.DETECT_ERRORS.format(code=code, language=language,
                                                             context="\n".join(context)))
        result["syntax_error"] = syntax
        result["execution"] = execution.to_dict() if execution else None
        result["language"] = language
        return result

    def generate_exercise(self, topic: str, difficulty: str = "beginner", language: str = "python",
                          num_tests: int = 5, weak_concepts: list[str] | None = None,
                          verify: bool = True) -> dict:
        difficulty = difficulty if difficulty in LEVELS else "beginner"
        language = self._lang(language)
        num_hidden = max(1, num_tests // 3)
        extra = (f"Focus on these concepts the student is weak in: {', '.join(weak_concepts)}.\n"
                 if weak_concepts else "")

        exercise, verified = None, False
        for _ in range(3):
            exercise = self._ask_json(prompts.GENERATE_EXERCISE.format(
                topic=topic, difficulty=difficulty, language=language, extra=extra,
                num_tests=num_tests, num_hidden=num_hidden))
            if not verify or language not in SUPPORTED_LANGUAGES:
                break
            results = run_tests(exercise.get("reference_solution", ""), language, exercise.get("test_cases", []))
            verified = bool(results) and all(r["passed"] for r in results)
            if verified:
                break

        exercise_id = uuid.uuid4().hex[:10]
        exercise.update({"id": exercise_id, "topic": topic, "difficulty": difficulty,
                         "language": language, "verified": verified})
        self._exercises[exercise_id] = exercise
        return self.public_exercise(exercise)

    @staticmethod
    def public_exercise(ex: dict) -> dict:
        pub = {k: v for k, v in ex.items() if k not in ("reference_solution", "test_cases")}
        pub["test_cases"] = [t for t in ex.get("test_cases", []) if not t.get("hidden")]
        pub["hidden_test_count"] = sum(1 for t in ex.get("test_cases", []) if t.get("hidden"))
        return pub

    def review_solution(self, code: str, exercise_id: str | None = None, exercise: dict | None = None,
                        language: str | None = None, student_id: str | None = None) -> dict:
        ex = exercise or self._exercises.get(exercise_id or "")
        if ex is None:
            # Create a mock exercise wrapper if standalone
            ex = {
                "id": "standalone_review",
                "statement": "Review code against general programming best practices.",
                "test_cases": [],
                "language": language or "python"
            }
        language = self._lang(language or ex.get("language", "python"))
        tests = ex.get("test_cases", [])

        notes, test_results = [], []
        syntax = check_syntax(code, language)
        if syntax:
            notes.append(f"Syntax error at line {syntax['line']}: {syntax['message']}")
        elif language in SUPPORTED_LANGUAGES and tests:
            test_results = run_tests(code, language, tests)
        else:
            notes.append("Automatic test execution unavailable or no tests specified.")

        passed = sum(r["passed"] for r in test_results)
        total = len(test_results)
        report = "\n".join(
            f"Test {r['test']}{' (hidden)' if r['hidden'] else ''}: {'PASS' if r['passed'] else 'FAIL'}"
            + ("" if r["passed"] or r["hidden"] else
               f" | input={r['input']!r} expected={r['expected_output']!r} got={r['actual_output']!r}"
               + (f" error={r['error'][-300:]!r}" if r["error"] else ""))
            for r in test_results) or "(no tests were run)"

        review = self._ask_json(prompts.REVIEW.format(
            language=language, statement=ex.get("statement", ""), code=code,
            passed=passed, total=total, test_report=report, notes="\n".join(notes) or "none"))

        quality = int(review.get("quality_score", 75) or 75)
        test_pct = round(100 * passed / total) if total else None
        score = round(0.7 * test_pct + 0.3 * quality) if test_pct is not None else quality

        shown = [r if not r["hidden"] else {"test": r["test"], "passed": r["passed"], "hidden": True}
                 for r in test_results]
        review.update({
            "exercise_id": ex.get("id"), "language": language,
            "tests_passed": passed, "tests_total": total, "test_results": shown,
            "score": score, "all_tests_passed": bool(total) and passed == total,
        })

        if student_id:
            self.event_bus.log_event(
                event_type="code_reviewed",
                student_id=student_id,
                payload={
                    "exercise_id": ex.get("id"),
                    "score": score,
                    "quality_score": quality,
                    "weak_concepts": review.get("concepts_to_review", [])
                },
                source_agent="CodeMentor"
            )

        return review

    def handle(self, action: str, **payload: Any) -> dict:
        actions = {
            "explain": self.explain_code,
            "debug": self.detect_errors,
            "exercise": self.generate_exercise,
            "review": self.review_solution,
        }
        if action not in actions:
            raise ValueError(f"Unknown action '{action}'. Choose from: {', '.join(actions)}")
        return actions[action](**payload)

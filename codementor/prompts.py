"""Prompt templates. Every prompt asks for strict JSON so other StudySync agents can consume the output."""

BASE_SYSTEM = (
    "You are CodeMentor AI, a patient, accurate programming tutor inside the StudySync learning platform. "
    "You teach students; you do not just hand over answers. Be concrete, reference line numbers, "
    "and never invent facts about the code. Respond with ONLY a single valid JSON object - no markdown fences, no prose."
)

EXPLAIN = """Explain this {language} code to a student at the **{level}** level.

```{language}
{code}
```

Return JSON with exactly these keys:
{{
  "summary": "1-2 sentence plain-English summary of what the code does",
  "step_by_step": [{{"lines": "e.g. 1-3", "explanation": "what these lines do and why"}}],
  "key_concepts": ["concepts a student should know, e.g. recursion, hash map"],
  "time_complexity": "Big-O or 'n/a'",
  "space_complexity": "Big-O or 'n/a'",
  "example_walkthrough": "a short trace of the code on a small example input",
  "common_mistakes": ["pitfalls related to this kind of code"]
}}"""

DETECT_ERRORS = """Review this {language} code for bugs.

```{language}
{code}
```

Context from automated checks (treat as ground truth):
{context}

Find syntax errors, runtime errors AND logical errors (off-by-one, wrong condition, bad edge-case handling,
unhandled input, wrong algorithm, mutation bugs, etc.). Only report real problems.

Return JSON with exactly these keys:
{{
  "has_errors": true/false,
  "errors": [{{
     "type": "syntax | runtime | logic | edge_case | style",
     "severity": "high | medium | low",
     "line": null,
     "description": "what is wrong",
     "why_it_happens": "teach the underlying concept",
     "fix": "how to fix it (short snippet allowed)"
  }}],
  "corrected_code": "full corrected code, or empty string if there were no errors",
  "concepts_to_review": ["topics the student should study"]
}}"""

GENERATE_EXERCISE = """Create a {difficulty} {language} programming exercise on the topic: "{topic}".
{extra}
Rules:
- The program must read from standard input and write to standard output so it can be auto-graded.
- Provide {num_tests} test cases ({num_hidden} of them hidden edge cases). "input" is the exact stdin text,
  "expected_output" the exact stdout text.
- Include a correct reference solution that produces exactly the expected outputs.
- Difficulty guide: beginner = single concept, short; intermediate = combines 2 concepts; advanced = needs algorithmic thinking.

Return JSON with exactly these keys:
{{
  "title": "...",
  "statement": "full problem statement with input/output format and constraints",
  "starter_code": "starter template with TODO comments",
  "test_cases": [{{"input": "...", "expected_output": "...", "hidden": false}}],
  "hints": ["progressive hints, from gentle to specific"],
  "concepts": ["concepts practiced"],
  "reference_solution": "complete working solution"
}}"""

REVIEW = """Review a student's {language} solution.

Problem statement:
{statement}

Student code:
```{language}
{code}
```

Automated test results (ground truth, {passed}/{total} passed):
{test_report}

Execution/syntax notes:
{notes}

Give constructive, educational feedback. Do not simply paste a full solution unless the code is already
correct and you are showing an improvement.

Return JSON with exactly these keys:
{{
  "verdict": "correct | partially_correct | incorrect",
  "quality_score": 85,
  "strengths": ["..."],
  "issues": [{{"line": null, "description": "...", "suggestion": "..."}}],
  "time_complexity": "...",
  "space_complexity": "...",
  "suggestions": ["concrete improvements"],
  "concepts_mastered": ["..."],
  "concepts_to_review": ["..."]
}}"""

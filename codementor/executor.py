"""Runs user code in a subprocess with a timeout and resource limits."""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict

from .config import get_settings

SUPPORTED_LANGUAGES = ("python", "javascript")


@dataclass
class ExecResult:
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    timed_out: bool = False
    duration_s: float = 0.0

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def to_dict(self) -> dict:
        d = asdict(self)
        d["ok"] = self.ok
        return d


def _limit_resources(mem_mb: int, cpu_s: int):
    def apply():  # runs in the child process (POSIX only)
        try:
            import resource
            mem = mem_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
        except Exception:
            pass
    return apply


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + f"\n...[truncated {len(text) - limit} chars]"


def run_code(code: str, language: str = "python", stdin: str = "", timeout: float | None = None,
             mem_mb: int = 256) -> ExecResult:
    settings = get_settings()
    timeout = timeout or settings.exec_timeout
    language = language.lower()
    if language in ("py", "python3"):
        language = "python"
    if language in ("js", "node", "nodejs"):
        language = "javascript"

    if language == "python":
        filename, cmd = "main.py", [sys.executable, "-I", "main.py"]
    elif language == "javascript":
        node = shutil.which("node")
        if not node:
            return ExecResult(stderr="Node.js is not installed on the server.", exit_code=127)
        filename, cmd = "main.js", [node, "main.js"]
    else:
        return ExecResult(stderr=f"Execution is not supported for '{language}'. "
                                 f"Supported: {', '.join(SUPPORTED_LANGUAGES)}.", exit_code=127)

    with tempfile.TemporaryDirectory(prefix="codementor_") as tmp:
        with open(os.path.join(tmp, filename), "w", encoding="utf-8") as f:
            f.write(code)
        preexec = None
        if os.name == "posix" and language == "python":
            preexec = _limit_resources(mem_mb, int(timeout) + 1)
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
        start = time.perf_counter()
        try:
            proc = subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=timeout,
                                  cwd=tmp, env=env, preexec_fn=preexec)
            return ExecResult(
                stdout=_truncate(proc.stdout, settings.max_output_chars),
                stderr=_truncate(proc.stderr, settings.max_output_chars),
                exit_code=proc.returncode,
                duration_s=round(time.perf_counter() - start, 3),
            )
        except subprocess.TimeoutExpired as e:
            out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            return ExecResult(stdout=_truncate(out, settings.max_output_chars),
                              stderr=f"Time limit exceeded ({timeout}s). Possible infinite loop.",
                              exit_code=124, timed_out=True, duration_s=round(time.perf_counter() - start, 3))


def check_syntax(code: str, language: str = "python") -> dict | None:
    """Cheap static syntax check. Returns error info, or None if fine / unsupported."""
    if language.lower() not in ("python", "py", "python3"):
        return None
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {"type": "SyntaxError", "message": e.msg, "line": e.lineno, "column": e.offset}
    return None


def run_tests(code: str, language: str, tests: list[dict], timeout: float | None = None) -> list[dict]:
    """Run `code` against stdin/stdout test cases: [{"input": str, "expected_output": str, ...}]."""
    results = []
    for i, t in enumerate(tests, 1):
        res = run_code(code, language, stdin=t.get("input", ""), timeout=timeout)
        actual = res.stdout.strip()
        expected = str(t.get("expected_output", "")).strip()
        passed = bool(res.ok and _normalize(actual) == _normalize(expected))
        results.append({
            "test": i,
            "passed": passed,
            "hidden": bool(t.get("hidden", False)),
            "input": t.get("input", ""),
            "expected_output": expected,
            "actual_output": actual,
            "error": res.stderr.strip() if not res.ok else "",
            "timed_out": res.timed_out,
        })
    return results


def _normalize(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.strip().splitlines())

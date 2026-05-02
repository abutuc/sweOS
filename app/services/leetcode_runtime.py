from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


@dataclass(slots=True)
class LeetCodeRunCaseResult:
    index: int
    passed: bool
    input: list[Any]
    expected: Any
    actual: Any | None
    error: str | None = None


@dataclass(slots=True)
class LeetCodeRunResult:
    passed: bool
    total_cases: int
    passed_cases: int
    stdout: str
    stderr: str
    runtime_ms: float | None
    case_results: list[LeetCodeRunCaseResult]
    message: str


_RUNNER_SCRIPT = r"""
import contextlib
import io
import json
import sys
import time
import traceback


SAFE_BUILTINS = {
    "__import__": __import__,
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "object": object,
    "ord": ord,
    "pow": pow,
    "print": print,
    "range": range,
    "reversed": reversed,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}


def main() -> int:
    user_code_path = sys.argv[1]
    tests_path = sys.argv[2]

    with open(user_code_path, "r", encoding="utf-8") as handle:
        source = handle.read()
    with open(tests_path, "r", encoding="utf-8") as handle:
        tests = json.load(handle)

    namespace = {"__builtins__": SAFE_BUILTINS}
    stdout_buffer = io.StringIO()
    case_results = []
    started_at = time.perf_counter()

    try:
        exec(compile(source, user_code_path, "exec"), namespace)
        solve = namespace.get("solve")
        if not callable(solve):
            raise RuntimeError("The solution must define a callable `solve` function.")

        for index, case in enumerate(tests, start=1):
            args = case["args"]
            expected = case["expected"]
            try:
                with contextlib.redirect_stdout(stdout_buffer):
                    actual = solve(*args)
                passed = actual == expected
                case_results.append(
                    {
                        "index": index,
                        "passed": passed,
                        "input": args,
                        "expected": expected,
                        "actual": actual,
                        "error": None,
                    }
                )
            except Exception:
                case_results.append(
                    {
                        "index": index,
                        "passed": False,
                        "input": args,
                        "expected": expected,
                        "actual": None,
                        "error": traceback.format_exc(),
                    }
                )
    except Exception:
        payload = {
            "passed": False,
            "total_cases": len(tests),
            "passed_cases": 0,
            "stdout": stdout_buffer.getvalue(),
            "stderr": traceback.format_exc(),
            "runtime_ms": round((time.perf_counter() - started_at) * 1000, 2),
            "case_results": case_results,
            "message": "Execution failed before all tests could run.",
        }
        print(json.dumps(payload))
        return 0

    passed_cases = sum(1 for case in case_results if case["passed"])
    payload = {
        "passed": passed_cases == len(tests),
        "total_cases": len(tests),
        "passed_cases": passed_cases,
        "stdout": stdout_buffer.getvalue(),
        "stderr": "",
        "runtime_ms": round((time.perf_counter() - started_at) * 1000, 2),
        "case_results": case_results,
        "message": (
            "All test cases passed." if passed_cases == len(tests)
            else f"{passed_cases} of {len(tests)} test cases passed."
        ),
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _load_runner_payload(output: str) -> dict[str, Any]:
    return json.loads(output.strip() or "{}")


def run_python_solution(source: str, tests: list[dict[str, Any]], timeout_seconds: int = 3) -> LeetCodeRunResult:
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        user_code_path = temp_path / "solution.py"
        tests_path = temp_path / "tests.json"
        runner_path = temp_path / "runner.py"

        user_code_path.write_text(source, encoding="utf-8")
        tests_path.write_text(json.dumps(tests), encoding="utf-8")
        runner_path.write_text(_RUNNER_SCRIPT, encoding="utf-8")

        try:
            completed = subprocess.run(
                [sys.executable, "-I", str(runner_path), str(user_code_path), str(tests_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            return LeetCodeRunResult(
                passed=False,
                total_cases=len(tests),
                passed_cases=0,
                stdout=exc.stdout or "",
                stderr="Execution timed out.",
                runtime_ms=None,
                case_results=[],
                message="Execution timed out.",
            )

        payload = _load_runner_payload(completed.stdout)
        case_results = [
            LeetCodeRunCaseResult(
                index=item["index"],
                passed=item["passed"],
                input=item["input"],
                expected=item["expected"],
                actual=item["actual"],
                error=item["error"],
            )
            for item in payload.get("case_results", [])
        ]
        return LeetCodeRunResult(
            passed=bool(payload.get("passed", False)),
            total_cases=int(payload.get("total_cases", len(tests))),
            passed_cases=int(payload.get("passed_cases", 0)),
            stdout=str(payload.get("stdout", "")),
            stderr=str(payload.get("stderr", completed.stderr or "")),
            runtime_ms=payload.get("runtime_ms"),
            case_results=case_results,
            message=str(payload.get("message", "Execution completed.")),
        )

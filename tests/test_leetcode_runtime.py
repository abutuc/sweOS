from app.services.leetcode_runtime import run_python_solution


def test_run_python_solution_passes_all_cases():
    result = run_python_solution(
        """
def solve(nums, target):
    seen = {}
    for index, value in enumerate(nums):
        needed = target - value
        if needed in seen:
            return [seen[needed], index]
        seen[value] = index
""",
        [
            {"args": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"args": [[3, 2, 4], 6], "expected": [1, 2]},
        ],
    )

    assert result.passed is True
    assert result.passed_cases == 2
    assert result.total_cases == 2
    assert result.case_results[0].passed is True


def test_run_python_solution_reports_failures():
    result = run_python_solution(
        """
def solve(nums, target):
    return []
""",
        [{"args": [[1, 2, 3], 3], "expected": [0, 1]}],
    )

    assert result.passed is False
    assert result.passed_cases == 0
    assert result.case_results[0].passed is False

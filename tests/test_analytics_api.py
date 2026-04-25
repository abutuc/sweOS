from datetime import date

from app.api.analytics import _calculate_streak_days


def test_calculate_streak_days_counts_consecutive_evaluation_dates():
    assert (
        _calculate_streak_days(
            [
                date(2026, 4, 25),
                date(2026, 4, 24),
                date(2026, 4, 24),
                date(2026, 4, 23),
                date(2026, 4, 20),
            ]
        )
        == 3
    )


def test_calculate_streak_days_returns_zero_without_activity():
    assert _calculate_streak_days([]) == 0

from heatmap.api.gui import *


def test_get_weeks_and_months_from_start_end_date():
    cases = [
        # Single Sunday, with leading zeros.
        (
            {"Year": 2026, "Month": 10, "Day": 18},
            {"Year": 2026, "Month": 10, "Day": 18},
            [[0, 0, 0, 0, 0, 0, 18]],
            [None],
            [None]
        ),
        # One complete Monday-to-Sunday week.
        (
            {"Year": 2026, "Month": 10, "Day": 12},
            {"Year": 2026, "Month": 10, "Day": 18},
            [[12, 13, 14, 15, 16, 17, 18]],
            [None],
            [None]
        ),
        # Leap day, month boundary, and partial weeks.
        (
            {"Year": 2024, "Month": 2, "Day": 28},
            {"Year": 2024, "Month": 3, "Day": 4},
            [[0, 0, 28, 29, 1, 2, 3], [4, 0, 0, 0, 0, 0, 0]],
            ["Mar", None],
            [None, None]
        ),
        # Year boundary.
        (
            {"Year": 2025, "Month": 12, "Day": 31},
            {"Year": 2026, "Month": 1, "Day": 1},
            [[0, 0, 31, 1, 0, 0, 0]],
            ["Jan"],
            [2026]
        ),
        # Month begins on Monday, creating a new week.
        (
            {"Year": 2026, "Month": 5, "Day": 31},
            {"Year": 2026, "Month": 6, "Day": 1},
            [[0, 0, 0, 0, 0, 0, 31], [1, 0, 0, 0, 0, 0, 0]],
            [None, "Jun"],
            [None, None]
        ),
    ]

    for start, end, expected_weeks, expected_months, expected_years in cases:
        assert get_weeks_and_months_from_start_end_date(start, end) == (
            expected_weeks,
            expected_months,
            expected_years,
        ), f"Failed for {start} through {end}"
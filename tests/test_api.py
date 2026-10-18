import pytest
from heatmap.api.gui import get_weeks_and_months_from_start_end_date, get_number_of_columns_in_grid

@pytest.mark.parametrize(
        ("start", "end", "expected_weeks", "expected_months", "expected_years"),
        [
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
            )  
        ]
)
def test_get_weeks_and_months_from_start_end_date(start, end, expected_weeks, expected_months, expected_years):
    assert get_weeks_and_months_from_start_end_date(start, end) == (
        expected_weeks,
        expected_months,
        expected_years,
    ), f"Failed for {start} through {end}"


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ((2026, 10, 19), (2026, 10, 19), 1),  # Same Monday
        ((2026, 10, 18), (2026, 10, 18), 1),  # Same Sunday
        ((2026, 10, 19), (2026, 10, 25), 1),  # Monday through Sunday
        ((2026, 10, 18), (2026, 10, 19), 2),  # Sunday through Monday
        ((2026, 10, 20), (2026, 10, 26), 2),  # Seven days spanning two weeks
        ((2026, 10, 19), (2026, 10, 26), 2),  # End Monday is included
        ((2026, 9, 30), (2026, 10, 1), 1),    # Month boundary, same week
        ((2026, 12, 31), (2027, 1, 1), 1),    # Year boundary, same week
        ((2023, 12, 31), (2024, 1, 1), 2),    # Year and week boundary
        ((2024, 2, 28), (2024, 3, 1), 1),     # Includes leap day
        ((2024, 2, 29), (2024, 3, 4), 2),     # Starts on leap day
        ((2026, 1, 1), (2026, 12, 31), 53),   # Full year
        ((2012, 1, 1), (2012, 12, 31), 54),   # Leap year touching 54 weeks
    ],
)
def test_get_number_of_columns_in_grid(start, end, expected):
    start_date = dict(zip(("Year", "Month", "Day"), start))
    end_date = dict(zip(("Year", "Month", "Day"), end))

    assert get_number_of_columns_in_grid(start_date, end_date) == expected


def test_get_number_of_columns_in_grid_rejects_reversed_dates():
    start_date = {"Year": 2026, "Month": 10, "Day": 19}
    end_date = {"Year": 2026, "Month": 10, "Day": 18}

    with pytest.raises(ValueError, match="Start date must not be after end date"):
        get_number_of_columns_in_grid(start_date, end_date)
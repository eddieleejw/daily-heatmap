from typing import Any

from nicegui import ui


def process_weeks(weeks: list[int]) -> list[list[int]]:
    '''
    Takes a list of days and processes it to remove any non-leading 0s, and return it partitioned by weeks

    e.g. [0, 0, 0, 1, 2, 3, 4, 5, ..., 30, 31, 0, 0, 0, 1, 2, ...] -> [[0, 0, 0, 1, 2, 3, 4], [5, 6, ...], ..., [..., 30, 31, 1, ...], ...]

    '''
    first_week = True

    removed_zeros = []

    for day in weeks:
        if day == 0 and first_week:
            removed_zeros.append(day)
        elif day == 0 and not first_week:
            continue
        else:
            first_week = False
            removed_zeros.append(day)

    removed_zeros += [0 for _ in range((7 - (len(removed_zeros) % 7))%7)]

    return [[removed_zeros[i + 7*weeks] for i in range(7)] for weeks in range(len(removed_zeros)//7)]


def find_months(weeks: list[list[int]]) -> list[Any]:
    '''
    Takes a processed weeks list (remove non-trailing zeros and in chunks of weeks) and returns a list denoting the column month labels

    e.g. [Jan, None, None, None, Feb, None, ...]
    '''

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    i = 0

    months_labels = []

    for week in weeks:
        new_month = False
        for day in week:
            if day == 1:
                new_month = True

        if new_month:
            months_labels.append(months[i])
            i += 1
        else:
            months_labels.append(None)
    
    return months_labels


def toggled_habit_cell(day):

    selected = False

    def toggle():
        nonlocal selected

        selected = not selected

        cell.classes(
            remove='bg-gray-200 bg-green-200',
            add='bg-green-200' if selected else 'bg-gray-200',
        )

    cell = ui.card().classes(
        'w-full h-full p-0 items-center justify-center '
        'rounded bg-gray-200 text-green-950 '
        'cursor-pointer'
    ).props('flat')
    
    with cell:
        ui.label(str(day)).classes('text-xs')

    cell.on('click', toggle)



from datetime import datetime
from pathlib import Path

from nicegui import ui

from heatmap.config import load_config
from heatmap.data.database import EMPTY_HABIT_ID, add_to_db, create_habit, get_db_all_as_dict, get_habits

DEFAULT_CONFIG_PATH = Path("configs/config.yaml")

def remove_intermediate_zeros(weeks: list[int]) -> list[int]:
    '''
    Takes a list of numbers and removed non-leading 0s

    e.g. [0, 0, 1, 2, 0, 3, 4, 0] -> [0, 0, 1, 2, 3, 4]
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

    return removed_zeros


def pad_zeros_to_multiple_of_seven(removed_zeros: list[int]):
    '''
    Pads '0's to an end of list of numbers to ensure it can be broken up into sub lists of size 7
    '''
    return removed_zeros + [0 for _ in range((7 - (len(removed_zeros) % 7))%7)]


def split_into_seven(to_split: list[int]) -> list[list[int]]:
    '''
    Takes a list of size n (divisible by 7) and divides it into 7 sublists in sequential order

    e.g. [1,2,3,4,5,6,7,8,9,10,11,12,13,14] -> [[1,2,3,4,5,6,7], [8,9,10,11,12,13,14]]
    '''
    assert len(to_split) % 7 == 0, "split_into_seven: input has incorrect size (not divisible by 7)"
    
    return [[to_split[i + 7*weeks] for i in range(7)] for weeks in range(len(to_split)//7)]


def process_weeks(weeks: list[int]) -> list[list[int]]:
    '''
    Takes a list of days and processes it to remove any non-leading 0s, and return it partitioned by weeks

    e.g. [0, 0, 0, 1, 2, 3, 4, 5, ..., 30, 31, 0, 0, 0, 1, 2, ...] -> [[0, 0, 0, 1, 2, 3, 4], [5, 6, ...], ..., [..., 30, 31, 1, ...], ...]

    '''
    removed_zeros = remove_intermediate_zeros(weeks)

    padded_removed_zeros = pad_zeros_to_multiple_of_seven(removed_zeros)

    return split_into_seven(padded_removed_zeros)


def find_months( weeks: list[list[int]], months: list[str] | None = None) -> list[str | None]:
    '''
    Takes a processed weeks list (remove non-trailing zeros and in chunks of weeks) and returns a list denoting the column month labels

    e.g. [Jan, None, None, None, Feb, None, ...]
    '''

    if months is None:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    month_names = iter(months)
    return [next(month_names) if 1 in week else None for week in weeks]


def create_habit_cell(day):
    cell = ui.card().classes(
        'w-full h-full p-0 items-center justify-center '
        'rounded bg-gray-200 text-green-950 '
        'cursor-pointer'
    ).props('flat')
    
    with cell:
        ui.label(str(day)).classes('text-xs')

    return cell


def toggled_habit_cell(day):

    def toggle():
        nonlocal selected

        selected = not selected

        cell.classes(
            remove='bg-gray-200 bg-green-200',
            add='bg-green-200' if selected else 'bg-gray-200',
        )

    cell = create_habit_cell(day)
    selected = False

    cell.on('click', toggle)


def parse_cell_date(year: int, month_str: str, day: int):
    try:
        month = datetime.strptime(month_str, "%b").month
    except ValueError as e:
        raise ValueError(f"{month_str} is not an accepted month format") from e

    return datetime(year, month, day)


def create_colored_cell(value):
    return ui.card().classes(
        'w-full h-full p-0 items-center justify-center cursor-pointer'
        ).style(
            f'background-color: hsl(120, 60%, {95 - value * 60}%);'
            ).props('flat')


def add_cell_editor(cell, cell_date: datetime, habit: str = EMPTY_HABIT_ID):
    with cell:
        editor = ui.input(label='Input value:', placeholder='0.0')
        label = ui.label(str(cell_date.day)).classes('text-xs')
        editor.set_visibility(False)

    def save_value():
        change_cell_value(cell, label, editor, cell_date, editor.value, habit)

    def show_editor():
        label.set_visibility(False)
        editor.set_visibility(True)

    editor.on('keydown.enter', save_value)
    label.on('click', show_editor)


def db_colored_cell(year: int, month_str: str, day: int, data: dict[str, float], habit: str = EMPTY_HABIT_ID) -> None:
    cell_date = parse_cell_date(year, month_str, day)
    value = data.get(cell_date.strftime('%Y-%m-%d'), 0)
    cell = create_colored_cell(value)
    add_cell_editor(cell, cell_date, habit)


def load_habit_data(habit_id: str = EMPTY_HABIT_ID) -> dict[str, float]:
    config = load_config(DEFAULT_CONFIG_PATH)
    database = config['database']
    return get_db_all_as_dict(database['db_path'], database['db_name'], habit_id)


def parse_cell_value(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if 0.0 <= number <= 1.0 else None


def save_cell_value(date: datetime, value: float, habit: str = EMPTY_HABIT_ID) -> None:
    config = load_config(DEFAULT_CONFIG_PATH)
    add_to_db(config['database']['db_path'], config['database']['db_name'], [(date.strftime("%Y-%m-%d"), value)], habit_id = habit)


def set_cell_green_color(cell, value: float) -> None:
    cell.style(f'background-color: hsl(120, 60%, {95 - value * 60}%);')


def change_cell_value(cell, label, editor, date: datetime, value, habit: str = EMPTY_HABIT_ID) -> None:
    parsed_value = parse_cell_value(value)
    if parsed_value is None:
        return

    save_cell_value(date, parsed_value, habit)
    set_cell_green_color(cell, parsed_value)
    label.set_visibility(True)
    editor.set_visibility(False)

def load_habits() -> list[str]:
    database = load_config(DEFAULT_CONFIG_PATH)['database']
    return get_habits(database['db_path'], database['db_name'])


def add_habit(name: str) -> bool:
    database = load_config(DEFAULT_CONFIG_PATH)['database']
    return create_habit(database['db_path'], database['db_name'], name)

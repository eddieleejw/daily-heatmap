import calendar

from nicegui import ui

from heatmap.api.gui_helper import (
    db_colored_cell,
    find_months,
    load_habit_data,
    process_weeks,
)


def get_weeks_and_months_from_year(year:int) -> tuple[list[list[int]], list[str | None]]:
    '''
    Given a year, returns the weeks and months representation

        weeks (list[list[int]]): each sublist has length 7, and an integer denoting the day (1~31). 0s may appear leading the first sublist or trailing the last sublist only
    
        months (list[str | None]): e.g. ["Jan", None, None, None, "Feb", None, None...]
    '''
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    weeks = [item for month in range(1,13) for week in cal.monthdayscalendar(year, month) for item in week]
    partitioned_weeks = process_weeks(weeks)
    return partitioned_weeks, find_months(partitioned_weeks)


def make_weekday_column_labels():
    '''
    Draw a column of weekday labels on a length 8 column
    '''
    ui.element('div')
    for weekday in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        ui.label(weekday).classes('flex items-center text-sm')  


def add_week_column(year: int, month: str | None, cur_month: str | None, week: list[int], data: dict[str, float]) -> str | None:
    '''
    Creates a length 8 column

    Top entry is the month if the column contains the first day of the month
    Otherwise, it is empty

    Populate each of the remaining cells with color coded habit cells
    '''
    if month == None:
        ui.element('div')
    else:
        ui.label(month)
    for day in week:
        if day == 0:
            ui.element('div')
        else:
            if day == 1:
                cur_month = month

            if cur_month is None:
                raise ValueError('A month must be known before rendering a day.')
            
            db_colored_cell(year, cur_month, day, data)

    return cur_month


def draw_year_grid(year: int, months: list[str | None], weeks: list[list[int]], data: dict[str, float]):
    if len(months) != len(weeks):
        raise ValueError(f"Length of months ({len(months)}) and weeks ({len(weeks)}) must match")
    
    ui.label(f'{year}')
    with ui.grid(rows="repeat(8, 32px)", columns="60px repeat(53, 32px)").style('grid-auto-flow: column; gap: 6px'):
        make_weekday_column_labels()

        cur_month = None
        for week, month in zip(weeks, months):       
            cur_month = add_week_column(year, month, cur_month, week, data)


def make_year_grid(year: int):
    weeks, months = get_weeks_and_months_from_year(year)
    data = load_habit_data()
    draw_year_grid(year, months, weeks, data)

def make_scroll_grid():
    pass
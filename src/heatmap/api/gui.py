import calendar
from datetime import date, timedelta

from nicegui import ui

from heatmap.api.gui_helper import (
    add_habit,
    load_habits,
    db_colored_cell,
    find_months,
    load_habit_data,
    process_weeks,
)
from heatmap.data.database import EMPTY_HABIT_ID


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


def add_week_column(year: int, month: str | None, cur_month: str | None, week: list[int], data: dict[str, float], new_year: int | None, habit: str = EMPTY_HABIT_ID) -> tuple[str | None, int]:
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
                if cur_month == "Jan" and new_year is not None:
                    year = new_year
            if cur_month is None:
                raise ValueError(f'A month must be known before rendering a day. cur_month = {cur_month}')
            
            db_colored_cell(year, cur_month, day, data, habit)

    return cur_month, year


def draw_year_grid(year: int, months: list[str | None], weeks: list[list[int]], data: dict[str, float]):
    if len(months) != len(weeks):
        raise ValueError(f"Length of months ({len(months)}) and weeks ({len(weeks)}) must match")
    
    ui.label(f'{year}')
    with ui.grid(rows="repeat(8, 32px)", columns="60px repeat(53, 32px)").style('grid-auto-flow: column; gap: 6px'):
        make_weekday_column_labels()

        cur_month = None
        for week, month in zip(weeks, months):       
            cur_month, _ = add_week_column(year, month, cur_month, week, data, new_year = None)


def make_year_grid(year: int):
    weeks, months = get_weeks_and_months_from_year(year)
    data = load_habit_data()
    draw_year_grid(year, months, weeks, data)



    

def date_dropdown_generic(title: str, options: list[int], selected_dates: dict[str, int]):

    def select_dates(option: int, selected_dates: dict[str, int], title: str):
        selected_dates[title] = option
        ui.notify(f"{title} updated to {option}")

    with ui.dropdown_button(title, auto_close=True):
        for option in options:
            ui.item(str(option), on_click=lambda option=option: select_dates(option, selected_dates, title))

def get_date_from_dropdown(title: str):
    selected_dates: dict[str, int] = {}
    ui.label(title)
    with ui.row():
        date_dropdown_generic(title="Year", options=[2024 + i for i in range(3)], selected_dates=selected_dates)
        date_dropdown_generic(title="Month", options=[i for i in range(1,13)], selected_dates=selected_dates)
        date_dropdown_generic(title="Day", options=[i for i in range(1,32)], selected_dates=selected_dates) # TODO: available options should change depending on month chosen

    return selected_dates


def get_number_of_columns_in_grid(start_date: dict[str, int], end_date: dict[str, int]) -> int:
    '''
    Given start and end date dictionary, find the number of columns needed (i.e number of weeks)
    '''
    start = date(start_date["Year"], start_date["Month"], start_date["Day"])
    end = date(end_date["Year"], end_date["Month"], end_date["Day"])

    if start > end:
        raise ValueError("Start date must not be after end date.")

    return (start.weekday() + (end - start).days) // 7 + 1

def get_weeks_and_months_from_start_end_date(start_date: dict[str, int], end_date: dict[str, int]) -> tuple[list[list[int]], list[str | None], list[int | None]]:
    '''
    Find the partitioned weeks and months given the start and end date

    Args
        start_date/end_date (dict[str, int]): a dictionary like {"Year": 2025, "Month": 10, "Day": 2}
    
    Returns
        list[list[int]]: the partitioned weeks. each sublist must have length 7. allow 0s only if leading first sublist or trailing last sublist
        list[str | None]: the months. value is the month if the corresponding week contains the first of a new month, else None
        list[int | None]: the years. same as month but for years
    '''

    start = date(start_date["Year"], start_date["Month"], start_date["Day"])
    end = date(end_date["Year"], end_date["Month"], end_date["Day"])

    if start > end:
        raise ValueError("Start date must not be after end date.")

    weeks: list[list[int]] = []
    months: list[str | None] = []
    years: list[int | None] = []

    for offset in range((end - start).days + 1):
        current = start + timedelta(days=offset)
        weekday = current.weekday()

        if not weeks or weekday == 0:
            weeks.append([0] * 7)
            months.append(None)
            years.append(None)

        weeks[-1][weekday] = current.day

        if current.day == 1:
            months[-1] = calendar.month_abbr[current.month]
            if current.month == 1:
                years[-1] = current.year

    return weeks, months, years



def draw_date_confined_grid(start_date: dict[str, int], end_date: dict[str, int], data: dict[str, float], habit: str = EMPTY_HABIT_ID):
    columns_count = get_number_of_columns_in_grid(start_date, end_date)

    with ui.grid(rows="repeat(9, 32px)", columns=f"60px repeat({columns_count}, 32px)").style('grid-auto-flow: column; gap: 6px'):
        ui.element('div')
        make_weekday_column_labels()
        weeks, months, years = get_weeks_and_months_from_start_end_date(start_date, end_date)
        cur_month: str | None = calendar.month_abbr[start_date["Month"]]
        cur_year = start_date["Year"]

        for week, month, year in zip(weeks, months, years):
            if year is not None:
                ui.label(str(year))
            else:
                ui.element('div')

            cur_month, cur_year = add_week_column(cur_year, month, cur_month, week, data, year, habit)

    
def get_start_end_dates_dropdown() -> tuple[dict[str, int], dict[str, int]]:
    start_dates = get_date_from_dropdown("Start date")
    end_dates = get_date_from_dropdown("End date")

    return start_dates, end_dates


def date_input_to_dict(date_in: ui.date_input) -> dict[str, int]:
    selected = date.fromisoformat(date_in.value)
    dates = {
        "Year": selected.year,
        "Month": selected.month,
        "Day": selected.day,
    }
    return dates

def get_start_end_dates_calendar() -> tuple[ui.date_input, ui.date_input]:
    with ui.row():
        start_dates = ui.date_input("Start date", value=(date.today() - timedelta(days=180)).isoformat())
        end_dates = ui.date_input("End date", value=date.today().isoformat())

    return start_dates, end_dates

def make_scroll_grid(habits: list[str] | None = None):
    if habits is None:
        habits = load_habits() or [EMPTY_HABIT_ID]
    if not habits:
        raise ValueError("At least one habit is required.")

    start_dates, end_dates = get_start_end_dates_calendar()

    selected_habit = habits[0]

    def select_habit(e):
        nonlocal selected_habit
        selected_habit = e.value
        click_draw_grid(start_dates, end_dates, selected_habit)

    def submit_habit():
        name = (name_input.value or '').strip()
        if not name:
            ui.notify('Enter a habit name.')
            return
        if name in habit_selector.options or not add_habit(name):
            ui.notify('That habit already exists.')
            return
        habit_selector.set_options([*habit_selector.options, name])
        habit_selector.set_value(name)
        dialog.close()
        name_input.set_value('')

    def open_habit_dialog():
        name_input.set_value('')
        dialog.open()

    with ui.dialog() as dialog, ui.card():
        name_input = ui.input('Habit name').mark('new-habit-name')
        name_input.on('keydown.enter', submit_habit)

    with ui.row().classes('items-center'):
        habit_selector = ui.select(
            list(habits), value=selected_habit, with_input=True, on_change=select_habit,
        ).mark('habit-selector')
        ui.button('Add new habit', on_click=open_habit_dialog)
    grid_container = ui.column() 

    def click_draw_grid(start_dates: ui.date_input, end_dates: ui.date_input, habit: str = EMPTY_HABIT_ID):

        grid_container.clear()

        with grid_container:
            try:
                draw_date_confined_grid(date_input_to_dict(start_dates), date_input_to_dict(end_dates), load_habit_data(habit_id = habit), habit)
            except ValueError as e:
                print(f"Error: {e}")

    click_draw_grid(start_dates, end_dates, selected_habit)

    start_dates.on_value_change(lambda: click_draw_grid(start_dates, end_dates, selected_habit))
    end_dates.on_value_change(lambda: click_draw_grid(start_dates, end_dates, selected_habit))
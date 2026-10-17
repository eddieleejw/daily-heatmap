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



    

def date_dropdown_generic(title: str, options: list[int], selected_dates: list[int]):

    def select_dates(option: int, selected_dates: list[int], title: str):
        selected_dates[title] = option
        ui.notify(f"{title} updated to {option}")

    with ui.dropdown_button(title, auto_close=True):
        for option in options:
            ui.item(option, on_click=lambda option=option: select_dates(option, selected_dates, title))

def get_date_from_dropdown(title: str):
    selected_dates = {}
    ui.label(title)
    date_dropdown_generic(title="Year", options=[2024 + i for i in range(3)], selected_dates=selected_dates)
    date_dropdown_generic(title="Month", options=[i for i in range(1,13)], selected_dates=selected_dates)
    date_dropdown_generic(title="Day", options=[i for i in range(1,32)], selected_dates=selected_dates) # TODO: available options should change depending on month chosen

    return selected_dates


def get_number_of_columns_in_grid():
    return 53 # TODO: delete default values

def get_weeks_and_months_from_start_end_date():
    # TODO: delete default values
    return [[1,2,3,4,5,6,7], [8,9,10,11,12,13,14], [15,16,17,1,2,3,4]], ["Jan", None, "Feb"]

def draw_date_confined_grid(start_date, end_date, data):
    # TODO: delete default values
    start_date = {"Year": 2024, "Month": 2, "Day": 4}
    end_date = {"Year": 2026, "Month": 5, "Day": 28}

    columns_count = get_number_of_columns_in_grid()


    with ui.grid(rows="repeat(9, 32px)", columns=f"60px repeat({columns_count}, 32px)").style('grid-auto-flow: column; gap: 6px'):
        ui.element('div')
        make_weekday_column_labels()
        for year in range(start_date["Year"], end_date["Year"]+1):
            weeks, months = get_weeks_and_months_from_start_end_date()
            cur_month = None
            new_year = True
            for week, month in zip(weeks, months):
                if new_year:
                    ui.label(f"{start_date["Year"]}")  
                    new_year = False
                else:
                    ui.element('div')
                cur_month = add_week_column(year, month, cur_month, week, data)


    

def get_start_end_dates_dropdown():
    start_dates = get_date_from_dropdown("Start date")
    end_dates = get_date_from_dropdown("End date")

    return start_dates, end_dates

def make_scroll_grid():
    start_dates, end_dates = get_start_end_dates_dropdown()
    data = load_habit_data()
    draw_date_confined_grid(start_dates, end_dates, data)

    ui.button('Click me!', on_click=lambda: ui.label(f"{start_dates}, {end_dates}"))
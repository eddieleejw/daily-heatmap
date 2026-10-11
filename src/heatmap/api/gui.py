import calendar

from nicegui import ui
from sqlite3 import Row

from heatmap.api.gui_helper import find_months, process_weeks, toggled_habit_cell, db_colored_cell


def make_year_grid(year, cell_behavior = None, args = None):
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    weeks = [item for month in range(1,13) for week in cal.monthdayscalendar(year, month) for item in week]

    weeks = process_weeks(weeks)
    months = find_months(weeks)


    ui.label(f'{year}')
    with ui.grid(rows="repeat(8, 32px)", columns="60px repeat(53, 32px)").style('grid-auto-flow: column; gap: 6px'):

        ui.element('div')
        for weekday in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            ui.label(weekday).classes('flex items-center text-sm')

        cur_month = None
        for week, month in zip(weeks, months):
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
                    # toggled_habit_cell(day)


                    db_colored_cell(year, cur_month, day)
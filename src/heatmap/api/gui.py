import calendar

from nicegui import ui
from heatmap.api.gui_helper import process_weeks

@ui.page("/prototype")
def gui_heatmap():

    year = 2026
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    weeks = [item for month in range(1,13) for week in cal.monthdayscalendar(year, month) for item in week]

    weeks = process_weeks(weeks)


    ui.label(f'{year}')
    with ui.grid(rows="repeat(8, 32px)", columns="60px repeat(53, 32px)").style('grid-auto-flow: column; gap: 6px'):

        ui.element('div')
        for weekday in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            ui.label(weekday).classes('flex items-center text-sm')

        for week in weeks:
            for day in weeks:
                if day == 0:
                    ui.element('div')
                else:
                    ui.label(str(day)).classes(
                        'flex items-center justify-center '
                        'rounded bg-green-200 text-green-950 text-xs'
                        )

        # first_week = True
        # weekday_counter = 0
        # for day in weeks:

        #     if weekday_counter == 0:
        #         ui.element('div')
        #         weekday_counter = 7

        #     if day == 0 and first_week:
        #         ui.element('div')
        #     elif day == 0 and not first_week:
        #         continue
        #     else:
        #         first_week = False
        #         ui.label(str(day)).classes(
        #             'flex items-center justify-center '
        #             'rounded bg-green-200 text-green-950 text-xs'
        #             )
        #     weekday_counter -= 1
                
        


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host = "0.0.0.0",
        port = 8800,
        show = False
    )
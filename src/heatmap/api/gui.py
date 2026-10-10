import calendar

from nicegui import ui

@ui.page("/prototype")
def gui_heatmap():

    year = 2026
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)

    with ui.row():
        for month in [4,5,6]:

            weeks = cal.monthdayscalendar(year, month)

            ui.label(f'{calendar.month_name[month]} {year}')

            with ui.grid(rows="repeat(7, 32px)", columns="60px repeat(10, 32px)").style('grid-auto-flow: column; gap: 6px'):
                for weekday in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
                    ui.label(weekday).classes('flex items-center text-sm')

                for week in weeks:
                    for day in week:
                        if day == 0:
                            ui.element('div')
                        else:
                            ui.label(str(day)).classes(
                                'flex items-center justify-center '
                                'rounded bg-green-200 text-green-950 text-xs'
                            )


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host = "0.0.0.0",
        port = 8800,
        show = False
    )
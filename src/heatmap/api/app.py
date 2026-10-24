from nicegui import ui

from heatmap.api.gui import make_scroll_grid, make_year_grid


@ui.page("/")
def main_page():
    make_scroll_grid()




if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host = "0.0.0.0",
        port = 8800,
        show = False,
        reload = False
    )
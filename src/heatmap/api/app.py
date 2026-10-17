from nicegui import ui

from heatmap.api.gui import make_year_grid, make_scroll_grid


@ui.page("/")
def main_page():
    ui.label('This is the main page')
    ui.link("Go to secret page", "/test")
    ui.link("Go to prototype", "/prototype")
    ui.link("Go to prototype scroll", "/prototype-scroll")

@ui.page("/test")
def test_page():
    ui.label('This is a test page')

@ui.page("/prototype")
def gui_heatmap():
    make_year_grid(2026)

@ui.page("/prototype-scroll")
def gui_scroll_heatmap():
    make_scroll_grid()




if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host = "0.0.0.0",
        port = 8800,
        show = False
    )
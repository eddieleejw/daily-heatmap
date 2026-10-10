from nicegui import ui


@ui.page("/")
def main_page():
    ui.label('This is the main page')
    ui.link("Go to secret page", "/test")

@ui.page("/test")
def test_page():
    ui.label('This is a test page')



if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host = "0.0.0.0",
        port = 8800,
        show = False
    )
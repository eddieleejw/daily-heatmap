from datetime import date, timedelta
from unittest.mock import Mock

import pytest
import yaml
from nicegui import ui
from nicegui.testing import User

from heatmap.api import gui, gui_helper


@pytest.mark.asyncio
async def test_render_and_edit_across_new_year(user: User, tmp_path, monkeypatch):
    '''
    Verify grid dates across New Year and that editing a January cell saves to the correct date.
    '''
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump({
            "database": {
                "db_path": str(tmp_path / "habits.db"),
                "db_name": "completed_days",
            },
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(gui_helper, "DEFAULT_CONFIG_PATH", config_path)

    start = date(2025, 12, 29)
    end = date(2026, 1, 11)
    rendered_dates = []
    original_add_cell_editor = gui_helper.add_cell_editor

    def track_cell_editor(cell, cell_date, habit=gui_helper.EMPTY_HABIT_ID):
        rendered_dates.append(cell_date.date())
        original_add_cell_editor(cell, cell_date, habit)

        editor, label = cell.default_slot.children
        key = cell_date.strftime("%Y-%m-%d")
        editor.mark(f"editor-{key}")
        label.mark(f"day-{key}")

    monkeypatch.setattr(
        gui_helper, "add_cell_editor", track_cell_editor
    )

    @ui.page("/new-year-test")
    def test_page():
        gui.draw_date_confined_grid(
            {"Year": start.year, "Month": start.month, "Day": start.day},
            {"Year": end.year, "Month": end.month, "Day": end.day},
            gui_helper.load_habit_data(),
        )

    await user.open("/new-year-test")

    expected_dates = [
        start + timedelta(days=offset)
        for offset in range((end - start).days + 1)
    ]
    assert rendered_dates == expected_dates

    # January 8 is in a column after the New Year transition.
    user.find(marker="day-2026-01-08").click()
    user.find(marker="editor-2026-01-08").type("0.75").trigger(
        "keydown.enter"
    )

    await user.should_see(marker="day-2026-01-08")
    assert gui_helper.load_habit_data() == {
        "2026-01-08": 0.75,
    }


@pytest.mark.asyncio
async def test_default_date_range_on_load(user: User, monkeypatch):
    '''
    Verify the initial grid includes today minus 180 days through today.
    '''
    today = date.today()

    class FixedDate(date):
        @classmethod
        def today(cls):
            return today

    monkeypatch.setattr(gui, "date", FixedDate)
    monkeypatch.setattr(gui, "load_habit_data", dict)

    rendered_dates = []
    original_db_colored_cell = gui.db_colored_cell

    def track_cell(year, month, day, data, habit=gui_helper.EMPTY_HABIT_ID):
        rendered_dates.append(
            gui_helper.parse_cell_date(year, month, day).date()
        )
        original_db_colored_cell(year, month, day, data, habit)

    monkeypatch.setattr(gui, "db_colored_cell", track_cell)

    @ui.page("/default-dates-test")
    def test_page():
        gui.make_scroll_grid()

    await user.open("/default-dates-test")

    start = today - timedelta(days=180)
    expected_dates = [
        start + timedelta(days=offset)
        for offset in range(181)
    ]
    assert rendered_dates == expected_dates

    
@pytest.mark.asyncio
async def test_selecting_habit_loads_its_data(user: User, monkeypatch):
    '''
    Selecting a habit requests that habit data
    '''

    load_data = Mock()
    load_data.return_value = {} # load_data() returns {}
    monkeypatch.setattr(gui, "load_habit_data", load_data)

    @ui.page("/habit-selection-test")
    def test_page():
        gui.make_scroll_grid(habits=["reading", "exercise"])

    await user.open("/habit-selection-test")

    load_data.reset_mock()

    user.find(marker="habit-selector").click()
    user.find("exercise").click()

    load_data.assert_called_once_with(habit_id="exercise")

@pytest.mark.asyncio
async def test_selected_habit_data_and_edits(user: User, tmp_path, monkeypatch):
    '''
    Test the following:

    1. Switching habits displays correct values
    2. Inputting new value changes only that habit
    3. Changing start date doesnt change values
    '''
    from heatmap.data.database import add_to_db, get_db_all_as_dict

    # Set up temp config and database with data for two habits
    db_path = tmp_path / "habits.db"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump({
        "database": {"db_path": str(db_path), "db_name": "completed_days"},
    }))
    monkeypatch.setattr(gui_helper, "DEFAULT_CONFIG_PATH", config_path)
    today = date.today().isoformat()
    add_to_db(db_path, "completed_days", [(today, 0.25)], habit_id="reading")
    add_to_db(db_path, "completed_days", [(today, 0.75)], habit_id="exercise")

    original_editor = gui_helper.add_cell_editor
    cells = {}

    def track_editor(cell, cell_date, habit):
        # Marks the cell corresponding to today's date for testing
        original_editor(cell, cell_date, habit)
        if cell_date.date().isoformat() == today:
            cells[habit] = cell
            editor, label = cell.default_slot.children
            editor.mark("today-editor")
            label.mark("today-label")

    monkeypatch.setattr(gui_helper, "add_cell_editor", track_editor)

    @ui.page("/habit-data-test")
    def test_page():
        gui.make_scroll_grid(habits=["reading", "exercise"])

    # Test switching habits loads and displays habits correctly
    await user.open("/habit-data-test")
    assert cells["reading"]._style["background-color"] == "hsl(120, 60%, 80.0%)"
    user.find(marker="habit-selector").click()
    user.find("exercise").click()
    assert cells["exercise"]._style["background-color"] == "hsl(120, 60%, 50.0%)"

    # Test that inputting new value changes only that habit's value in the database
    user.find(marker="today-label").click()
    user.find(marker="today-editor").type("0.5").trigger("keydown.enter")
    assert get_db_all_as_dict(db_path, "completed_days", "exercise") == {today: 0.5}
    assert get_db_all_as_dict(db_path, "completed_days", "reading") == {today: 0.25}

    # Check changing start date displays correct saved values
    start_input = next(element for element in user.find(ui.date_input).elements if element.label == "Start date")
    start_input.set_value((date.today() - timedelta(days=7)).isoformat())
    assert cells["exercise"]._style["background-color"] == "hsl(120, 60%, 65.0%)"
    user.find(marker="habit-selector").click()
    user.find("reading").click()
    assert cells["reading"]._style["background-color"] == "hsl(120, 60%, 80.0%)"
    user.find(marker="habit-selector").click()
    user.find("exercise").click()
    assert cells["exercise"]._style["background-color"] == "hsl(120, 60%, 65.0%)"

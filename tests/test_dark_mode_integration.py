from datetime import date, timedelta

import pytest
import yaml
from nicegui import ui
from nicegui.testing import User

from heatmap.api import gui, gui_helper
from heatmap.data.database import add_to_db, get_db_all_as_dict


@pytest.mark.asyncio
@pytest.mark.parametrize('initial_dark', [False, True])
async def test_theme_colors_survive_edits_habit_and_date_changes(
    user: User, tmp_path, monkeypatch, initial_dark,
):
    db_path = tmp_path / 'habits.db'
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(yaml.safe_dump({
        'database': {'db_path': str(db_path), 'db_name': 'completed_days'},
    }), encoding='utf-8')
    monkeypatch.setattr(gui_helper, 'DEFAULT_CONFIG_PATH', config_path)
    today = date.today().isoformat()
    add_to_db(db_path, 'completed_days', [(today, 0.25)], habit_id='reading')
    cells = {}
    original_editor = gui_helper.add_cell_editor

    def track_editor(cell, cell_date, habit, *, dark=False):
        original_editor(cell, cell_date, habit, dark=dark)
        if cell_date.date().isoformat() == today:
            cells['today'] = cell
            editor, label = cell.default_slot.children
            editor.mark('theme-editor')
            label.mark('theme-label')

    monkeypatch.setattr(gui_helper, 'add_cell_editor', track_editor)

    @ui.page('/theme-test')
    def page():
        gui.make_scroll_grid(habits=['reading', 'exercise'], dark=initial_dark)

    colors = {
        False: {0: 'hsl(120, 60%, 95%)', 0.25: 'hsl(120, 60%, 80.0%)',
                0.5: 'hsl(120, 60%, 65.0%)'},
        True: {0: 'hsl(120, 0%, 15%)', 0.25: 'hsl(120, 15.0%, 20.0%)',
               0.5: 'hsl(120, 30.0%, 25.0%)'},
    }

    def assert_color(dark, value):
        assert cells['today']._style['background-color'] == colors[dark][value]

    def select_habit(name):
        user.find(marker='habit-selector').click()
        user.find(name).click()

    await user.open('/theme-test')
    assert_color(initial_dark, 0.25)
    user.find('Dark mode').click()
    assert_color(not initial_dark, 0.25)

    user.find(marker='theme-label').click()
    user.find(marker='theme-editor').type('0.5').trigger('keydown.enter')
    assert_color(not initial_dark, 0.5)
    assert get_db_all_as_dict(db_path, 'completed_days', 'reading') == {today: 0.5}

    select_habit('exercise')
    assert_color(not initial_dark, 0)
    start_input = next(e for e in user.find(ui.date_input).elements if e.label == 'Start date')
    start_input.set_value((date.today() - timedelta(days=7)).isoformat())
    assert_color(not initial_dark, 0)

    select_habit('reading')
    assert_color(not initial_dark, 0.5)
    user.find('Dark mode').click()
    assert_color(initial_dark, 0.5)

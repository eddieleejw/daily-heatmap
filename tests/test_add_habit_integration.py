from datetime import date

import pytest
import yaml
from nicegui import ui
from nicegui.testing import User

from heatmap.api import gui, gui_helper
from heatmap.data.database import add_to_db, get_db_all_as_dict


@pytest.fixture
def habit_db(tmp_path, monkeypatch):
    '''
    Set up test database and config.yaml

    Add one data point: (date.today, 0.75, "reading")
    '''
    db_path = tmp_path / 'habits.db'
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(yaml.safe_dump({
        'database': {'db_path': str(db_path), 'db_name': 'completed_days'},
    }), encoding='utf-8')
    monkeypatch.setattr(gui_helper, 'DEFAULT_CONFIG_PATH', config_path)
    add_to_db(db_path, 'completed_days', [(date.today().isoformat(), 0.75)],
              habit_id='reading')
    return db_path


@pytest.fixture
def habit_page(habit_db):
    '''
    Generate two test pages

    One that makes scroll grid with habit reading

    One that reloads scroll grid
    '''
    @ui.page('/add-habit-test')
    def initial_page():
        gui.make_scroll_grid(habits=['reading'], dark=False)

    @ui.page('/reload-added-habit-test')
    def fresh_page():
        gui.make_scroll_grid(dark=False)

    return '/add-habit-test'


@pytest.fixture
def rendered_cells(monkeypatch):
    '''
    Render each cell normally, but keep track of the one that corresponds to today.date
    '''
    cells = {}
    original_editor = gui_helper.add_cell_editor

    def track_editor(cell, cell_date, habit=gui_helper.EMPTY_HABIT_ID, *, dark=False):
        original_editor(cell, cell_date, habit, dark=dark)
        cells[cell_date.date().isoformat()] = cell
        if cell_date.date() == date.today():
            editor, label = cell.default_slot.children
            editor.mark('today-editor')
            label.mark('today-label')

    monkeypatch.setattr(gui_helper, 'add_cell_editor', track_editor)
    return cells


def habit_selector(user):
    return next(iter(user.find(marker='habit-selector').elements))


def add_habit(user, name='exercise'):
    '''
    Add a new habit using the dropdown
    '''
    user.find('Add new habit').click()
    user.find(marker='new-habit-name').type(name).trigger('keydown.enter')


def select_habit(user, name):
    user.find(marker='habit-selector').click()
    user.find(name).click()


def assert_empty_grid(cells):
    assert date.today().isoformat() in cells
    assert all(cell._style['background-color'] == 'hsl(120, 60%, 95%)'
               for cell in cells.values())


@pytest.mark.asyncio
async def test_add_habit_selects_it_and_draws_empty_grid(user: User, habit_page, rendered_cells):
    await user.open(habit_page)
    rendered_cells.clear()
    add_habit(user, name='exercise')

    assert 'exercise' in habit_selector(user).options
    assert habit_selector(user).value == 'exercise'
    assert_empty_grid(rendered_cells)

    select_habit(user, 'reading')
    rendered_cells.clear()
    select_habit(user, 'exercise')
    assert_empty_grid(rendered_cells)


@pytest.mark.asyncio
async def test_new_habit_persists_and_its_edits_reload(
    user: User, habit_page, habit_db, rendered_cells,
):
    await user.open(habit_page)
    add_habit(user)

    await user.open('/reload-added-habit-test')
    assert 'exercise' in habit_selector(user).options
    select_habit(user, 'reading')
    rendered_cells.clear()
    select_habit(user, 'exercise')
    assert_empty_grid(rendered_cells)

    user.find(marker='today-label').click()
    user.find(marker='today-editor').type('0.5').trigger('keydown.enter')
    today = date.today().isoformat()
    assert get_db_all_as_dict(habit_db, 'completed_days', 'exercise') == {today: 0.5}
    assert get_db_all_as_dict(habit_db, 'completed_days', 'reading') == {today: 0.75}

    await user.open('/reload-added-habit-test')
    select_habit(user, 'reading')
    rendered_cells.clear()
    select_habit(user, 'exercise')
    assert rendered_cells[today]._style['background-color'] == 'hsl(120, 60%, 65.0%)'


@pytest.mark.asyncio
async def test_duplicate_habit_preserves_options_and_existing_data(
    user: User, habit_page, habit_db,
):
    await user.open(habit_page)
    add_habit(user, 'reading')

    assert list(habit_selector(user).options).count('reading') == 1
    assert get_db_all_as_dict(habit_db, 'completed_days', 'reading') == {
        date.today().isoformat(): 0.75,
    }

    await user.open('/reload-added-habit-test')
    assert list(habit_selector(user).options).count('reading') == 1

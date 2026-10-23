from datetime import datetime

import pytest
import yaml

from heatmap.api import gui_helper
from heatmap.data.database import add_to_db, get_db_all_as_dict


def test_database_write_and_read(tmp_path):
    db_path = tmp_path / "habits.db"
    table_name = "completed_days"
    data = [
        ("2026-10-16", 0.0),
        ("2026-10-17", 0.5),
        ("2026-10-18", 1.0),
    ]

    add_to_db(db_path, table_name, data)

    result = get_db_all_as_dict(db_path, table_name)

    assert result == dict(data)


def test_database_update_existing_date(tmp_path):
    db_path = tmp_path / "habits.db"
    table_name = "completed_days"
    add_to_db(db_path, table_name, [
        ("2026-10-17", 0.5),
        ("2026-10-18", 1.0),
    ])

    add_to_db(db_path, table_name, [("2026-10-17", 0.75)])

    result = get_db_all_as_dict(db_path, table_name)

    assert result == {
        "2026-10-17": 0.75,
        "2026-10-18": 1.0,
    }



def test_configuration_save_and_load(tmp_path, monkeypatch):
    db_path = tmp_path / "habits.db"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump({
            "database": {
                "db_path": str(db_path),
                "db_name": "completed_days",
            },
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(gui_helper, "DEFAULT_CONFIG_PATH", config_path)

    gui_helper.save_cell_value(datetime(2026, 10, 18), 0.75)

    result = gui_helper.load_habit_data()

    assert db_path.is_file()
    assert result == {"2026-10-18": 0.75}


def test_load_data_for_selected_habit(tmp_path):
    '''
    Checks habit data value loading
    '''
    db_path = tmp_path / "habits.db"
    table_name = "completed_days"

    add_to_db(
        db_path,
        table_name,
        [("2026-10-18", 0.25)],
        habit_id="reading",
    )
    add_to_db(
        db_path,
        table_name,
        [("2026-10-18", 0.75)],
        habit_id="exercise",
    )

    assert get_db_all_as_dict(
        db_path, table_name, habit_id="reading"
    ) == {"2026-10-18": 0.25}

    assert get_db_all_as_dict(
        db_path, table_name, habit_id="exercise"
    ) == {"2026-10-18": 0.75}

def test_empty_habit_persists_and_rejects_duplicates(tmp_path):
    from heatmap.data.database import create_habit, get_habits

    db_path = tmp_path / 'habits.db'
    assert create_habit(db_path, 'completed_days', ' exercise ')
    assert not create_habit(db_path, 'completed_days', 'exercise')
    assert get_habits(db_path, 'completed_days') == ['exercise']
    assert get_db_all_as_dict(db_path, 'completed_days', 'exercise') == {}
    with pytest.raises(ValueError, match='must not be empty'):
        create_habit(db_path, 'completed_days', '   ')


def test_existing_database_habits_are_discovered(tmp_path):
    import sqlite3
    from heatmap.data.database import get_habits

    db_path = tmp_path / 'legacy.db'
    with sqlite3.connect(db_path) as con:
        con.execute('CREATE TABLE completed_days '
                    '(date TEXT, value REAL, habit_id TEXT, PRIMARY KEY (date, habit_id))')
        con.execute('INSERT INTO completed_days VALUES (?, ?, ?)',
                    ('2026-10-18', 0.75, 'reading'))
    assert get_habits(db_path, 'completed_days') == ['reading']
    assert get_habits(db_path, 'completed_days') == ['reading']
    assert get_db_all_as_dict(db_path, 'completed_days', 'reading') == {'2026-10-18': 0.75}

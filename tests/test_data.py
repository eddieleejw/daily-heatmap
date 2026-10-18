from datetime import datetime

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
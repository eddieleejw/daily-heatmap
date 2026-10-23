import sqlite3
from datetime import date
from pathlib import Path

from heatmap.data.dates import list_dates

EMPTY_HABIT_ID = "EMPTY"


def create_db(db_path: Path, db_name: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {db_name}(
        date TEXT NOT NULL,
        value REAL NOT NULL,
        habit_id TEXT NOT NULL,
        PRIMARY KEY (date, habit_id)
        )
    """)

    cur.execute(f"CREATE TABLE IF NOT EXISTS {db_name}_habits (habit_id TEXT PRIMARY KEY)")
    cur.execute(f"INSERT OR IGNORE INTO {db_name}_habits SELECT DISTINCT habit_id FROM {db_name}")
    con.commit()
    return con

def add_to_db(db_path: Path, db_name: str, data: list[tuple[str, float]], habit_id: str = EMPTY_HABIT_ID) -> None:
    '''
    Commit some data to the database, updating data if primary key exists
    '''
    con = create_db(db_path, db_name)
    cur = con.cursor()

    cur.executemany(f"INSERT INTO {db_name} VALUES (?, ?, ?) ON CONFLICT(date, habit_id) DO UPDATE SET value = excluded.value", [(d[0], d[1], habit_id) for d in data])

    con.commit()

def create_habit(db_path: Path, db_name: str, habit_id: str) -> bool:
    '''
    Persist an empty habit; return False if its name already exists.
    '''
    habit_id = habit_id.strip()
    if not habit_id:
        raise ValueError("Habit name must not be empty.")
    con = create_db(db_path, db_name)
    try:
        with con:
            cursor = con.execute(
                f"INSERT OR IGNORE INTO {db_name}_habits (habit_id) VALUES (?)",
                (habit_id,),
            )
            return cursor.rowcount == 1
    finally:
        con.close()


def get_habits(db_path: Path, db_name: str) -> list[str]:
    con = create_db(db_path, db_name)
    try:
        return [row[0] for row in con.execute(
            f"SELECT habit_id FROM {db_name}_habits ORDER BY habit_id"
        )]
    finally:
        con.close()


def get_db_all(db_path: Path, db_name: str) -> list[sqlite3.Row]:
    '''
    Select all rows from db and return as a list of sqlite3.Row objects

    each row object can be used like a dictionary to access values (e.g. row['date'])
    '''
    con = create_db(db_path, db_name)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute(f"SELECT * FROM {db_name}")

    return cur.fetchall()

def create_test_db(db_path: Path, db_name: str, start_date: date = date(2026,1,1), end_date: date = date(2026,12,31)):
    import random

    days = list_dates(start_date, end_date)

    add_to_db(
        db_path,
        db_name,
        [
            (day.strftime("%Y-%m-%d"), random.random()) for day in days
        ]
    )

def get_db_all_as_dict(db_path: Path, db_name: str, habit_id:str = EMPTY_HABIT_ID) -> dict[str, int | float]:
    con = create_db(db_path, db_name)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute(f"SELECT * FROM {db_name} WHERE habit_id = ?", (habit_id,))

    rows = cur.fetchall()

    return {row['date']:row['value'] for row in rows for k,v in dict(row).items()}

if __name__ == "__main__":
    db_path = Path("data/test.db")
    db_name = "completed_days"

    create_test_db(db_path, db_name)

    print(get_db_all_as_dict(db_path, db_name))

import sqlite3
from pathlib import Path
from typing import List, Tuple
from heatmap.data.dates import list_dates
from datetime import date

def create_db(db_path: Path, db_name: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {db_name}(
        date TEXT PRIMARY KEY,
        value REAL NOT NULL
        )
    """)

    return con

def add_to_db(db_path: Path, db_name: str, data: List[Tuple[str, int]]) -> None:
    '''
    Commit some data to the database, updating data if primary key exists
    '''
    con = create_db(db_path, db_name)
    cur = con.cursor()

    cur.executemany(f"INSERT INTO {db_name} VALUES (?, ?) ON CONFLICT(date) DO UPDATE SET value = excluded.value", data)

    con.commit()

def get_db_all(db_path: Path, db_name: str):
    '''
    Select all rows from db
    '''
    con = create_db(db_path, db_name)
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

if __name__ == "__main__":
    db_path = Path("data/test.db")
    db_name = "completed_days"

    create_test_db(db_path, db_name)

    print(get_db_all(db_path, db_name))
"""One local SQLite table; parameterized queries keep data separate from SQL."""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.environ.get('RESUME_DB', Path(__file__).parent / 'data' / 'reports.db'))


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.row_factory = sqlite3.Row
        with connection:
            connection.execute('''CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, created_at TEXT NOT NULL,
                resume TEXT NOT NULL, job TEXT NOT NULL, result TEXT NOT NULL)''')
            yield connection
    finally:
        connection.close()


def save(report):
    with connect() as db:
        db.execute('INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)',
                   (report['id'], report['title'], report['created_at'], report['resume'],
                    report['job'], json.dumps(report['result'])))


def history():
    with connect() as db:
        return [dict(row) for row in db.execute(
            'SELECT id, title, created_at FROM reports ORDER BY created_at DESC LIMIT 100')]


def get(report_id):
    with connect() as db:
        row = db.execute('SELECT * FROM reports WHERE id = ?', (report_id,)).fetchone()
    if row is None:
        return None
    report = dict(row)
    report['result'] = json.loads(report['result'])
    return report


def delete(report_id):
    with connect() as db:
        return db.execute('DELETE FROM reports WHERE id = ?', (report_id,)).rowcount > 0

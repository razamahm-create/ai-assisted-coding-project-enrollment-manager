import sqlite3
from pathlib import Path
from typing import List
from config import Config
from data import AVAILABLE_COURSE_KEYS, SAMPLE_ENROLLMENTS


class ConnectionFactory:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn


class UnitOfWork:
    def __init__(self, conn_factory: ConnectionFactory):
        self.conn_factory = conn_factory
        self.connection = None

    def __enter__(self) -> sqlite3.Connection:
        self.connection = self.conn_factory.get_connection()
        return self.connection

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        finally:
            self.connection.close()


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]


def create_tables(conn_factory: ConnectionFactory) -> None:
    with conn_factory.get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                instructor TEXT NOT NULL,
                enrollment_key TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                course_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'enrolled',
                enrolled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            )
            """
        )


def seed_sample_data(conn_factory: ConnectionFactory) -> None:
    with conn_factory.get_connection() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO courses (
                course_id, course_name, instructor, enrollment_key
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    course["course_id"],
                    course["course_name"],
                    course["instructor"],
                    course["enrollment_key"],
                )
                for course in AVAILABLE_COURSE_KEYS
            ],
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO enrollments (user_id, email, course_id, status)
            VALUES (?, ?, ?, ?)
            """,
            SAMPLE_ENROLLMENTS,
        )

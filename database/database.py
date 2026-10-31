import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from core.paths import default_database_path

from .schema import DEFAULT_SUBJECTS, MIGRATIONS, SCHEMA, SCHEMA_VERSION


def utc_now() -> str:
    """Current time as a UTC string comparable with SQLite's CURRENT_TIMESTAMP."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


class Database:
    """Small SQLite connection manager. One connection, used from the UI thread only."""

    def __init__(self, path=None):
        if path == ":memory:":
            self.path = None
            target = ":memory:"
        else:
            self.path = Path(path) if path else default_database_path()
            self.path.parent.mkdir(parents=True, exist_ok=True)
            target = str(self.path)
        self.connection = sqlite3.connect(target, timeout=10.0)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA busy_timeout = 10000")
        if self.path is not None:
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA synchronous = NORMAL")
        self.initialize()

    def initialize(self):
        current = self.connection.execute("PRAGMA user_version").fetchone()[0]
        if current > SCHEMA_VERSION:
            raise RuntimeError(
                f"Database version {current} is newer than this app supports."
            )
        self.connection.executescript(SCHEMA)  # version 1, idempotent
        for version in range(max(current, 1) + 1, SCHEMA_VERSION + 1):
            try:
                self.connection.executescript(
                    f"BEGIN;{MIGRATIONS[version]}PRAGMA user_version = {version};COMMIT;"
                )
            except sqlite3.Error:
                if self.connection.in_transaction:
                    self.connection.rollback()
                raise
        with self.connection:
            self.connection.executemany(
                "INSERT OR IGNORE INTO subjects(name) VALUES (?)",
                [(name,) for name in DEFAULT_SUBJECTS],
            )
from pathlib import Path
from PySide6.QtCore import QStandardPaths

from .schema import SCHEMA, SCHEMA_VERSION


def default_database_path() -> Path:
    base = Path(QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    ))
    base.mkdir(parents=True, exist_ok=True)
    return base / "study_app.sqlite3"


class Database:
    """Small SQLite connection manager. Use one connection per app process."""

    def __init__(self, path=None):
        self.path = Path(path) if path else default_database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(
            str(self.path), timeout=10.0, check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA synchronous = NORMAL")
        self.connection.execute("PRAGMA busy_timeout = 10000")
        self.initialize()

    def initialize(self):
        with self.connection:
            self.connection.executescript(SCHEMA)
            current = self.connection.execute(
                "PRAGMA user_version"
            ).fetchone()[0]
            if current > SCHEMA_VERSION:
                raise RuntimeError(
                    f"Database version {current} is newer than this app supports."
                )
            self.connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            self._seed_subjects()

    def _seed_subjects(self):
        subjects = ["NT", "AE", "Math", "CS_P", "CS", "English", "BS", "PuG", "Ethik"]
        self.connection.executemany(
            "INSERT OR IGNORE INTO subjects(name) VALUES (?)",
            [(name,) for name in subjects],
        )

    def execute(self, sql, params=()):
        return self.connection.execute(sql, params)

    def fetch_one(self, sql, params=()):
        return self.execute(sql, params).fetchone()

    def fetch_all(self, sql, params=()):
        return self.execute(sql, params).fetchall()

    def close(self):
        self.connection.close()

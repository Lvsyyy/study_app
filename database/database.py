import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from core.paths import default_database_path

from .schema import DEFAULT_SUBJECTS, MIGRATIONS, SCHEMA, SCHEMA_VERSION


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


class Database:
    """SQLite connection manager. A single connection is used by the UI thread."""

    def __init__(self, path=None):
        if path == ":memory:":
            self.path = None
            target = ":memory:"
        else:
            self.path = Path(path) if path is not None else default_database_path()
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

        if current == 0:
            self.connection.executescript(SCHEMA)
            self.connection.execute("PRAGMA user_version = 1")
            current = 1

        with self.connection:
            self.connection.executemany(
                "INSERT OR IGNORE INTO subjects(name) VALUES (?)",
                [(name,) for name in DEFAULT_SUBJECTS],
            )

        for version in range(current + 1, SCHEMA_VERSION + 1):
            migration = MIGRATIONS.get(version)
            if migration is None:
                raise RuntimeError(f"Missing database migration {version}.")
            try:
                self.connection.executescript(
                    f"BEGIN;\n{migration}\nPRAGMA user_version = {version};\nCOMMIT;"
                )
            except sqlite3.Error:
                if self.connection.in_transaction:
                    self.connection.rollback()
                raise


    def execute(self, sql, params=()):
        return self.connection.execute(sql, params)

    def fetch_one(self, sql, params=()):
        return self.execute(sql, params).fetchone()

    def fetch_all(self, sql, params=()):
        return self.execute(sql, params).fetchall()

    def close(self):
        self.connection.close()

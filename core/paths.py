"""Filesystem locations used by the app."""
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QStandardPaths


def app_data_dir() -> Path:
    # Qt derives the data folder from these names, so scripts that use the database
    # without starting the app still end up in the same place as the app itself.
    if not QCoreApplication.organizationName():
        QCoreApplication.setOrganizationName("Lvsy")
    if not QCoreApplication.applicationName():
        QCoreApplication.setApplicationName("Study App")
    base = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    base.mkdir(parents=True, exist_ok=True)
    return base


def default_database_path() -> Path:
    return app_data_dir() / "study_app.sqlite3"

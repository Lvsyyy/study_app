"""Filesystem locations used by the app."""
import shutil
import uuid
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


def assets_dir() -> Path:
    path = app_data_dir() / "assets"
    path.mkdir(parents=True, exist_ok=True)
    return path


def store_image(source) -> str:
    """Copy an image into the app-managed assets folder and return the new path."""
    source = Path(source)
    if not source.is_file():
        raise FileNotFoundError(f"Image not found: {source}")
    target = assets_dir() / f"{uuid.uuid4().hex}{source.suffix.lower()}"
    shutil.copy2(source, target)
    return str(target)

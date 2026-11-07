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


def project_root() -> Path:
    """Return the repository/application root containing bundled assets."""
    return Path(__file__).resolve().parents[1]


def diagram_assets_dir() -> Path:
    """Directory for diagrams referenced by questions."""
    return project_root() / "assets" / "diagram"


def resolve_question_image_path(path: str | Path | None) -> Path | None:
    """Resolve a question image path, supporting diagram filenames and legacy paths.

    Absolute paths remain supported. Relative paths are resolved from the
    application root; a filename without a directory is looked up in
    assets/diagram.
    """
    if not path:
        return None

    image_path = Path(path).expanduser()
    if image_path.is_absolute():
        return image_path

    root = project_root()
    rooted_path = root / image_path
    if rooted_path.is_file() or len(image_path.parts) > 1:
        return rooted_path

    return diagram_assets_dir() / image_path


def default_database_path() -> Path:
    return app_data_dir() / "study_app.sqlite3"

import sys

from PySide6.QtWidgets import QApplication

from core.i18n import set_language
from core.settings_store import SettingsStore
from core.theme_manager import ThemeManager
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    # Application and organisation names define the data folder, so they are
    # intentionally not translated.
    app.setApplicationName("Study App")
    app.setOrganizationName("Lvsy")

    settings = SettingsStore()
    set_language(settings.language)
    ThemeManager.apply(app, settings.theme)

    window = MainWindow(app, settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

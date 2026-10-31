import sys
<<<<<<< HEAD

from PySide6.QtWidgets import QApplication

=======
from PySide6.QtWidgets import QApplication
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
from core.settings_store import SettingsStore
from core.theme_manager import ThemeManager
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Study App")
    app.setOrganizationName("Lvsy")

    settings = SettingsStore()
    ThemeManager.apply(app, settings.theme)

    window = MainWindow(app, settings)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

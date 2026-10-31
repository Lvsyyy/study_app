<<<<<<< HEAD
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from core.session_tracker import SessionTracker
from core.settings_store import SettingsStore
from core.theme_manager import ThemeManager
from database.attempt_repository import AttemptRepository
from database.database import Database
from database.question_repository import QuestionRepository
from database.session_repository import SessionRepository
from database.statistics_repository import StatisticsRepository
from ui.dashboard import Dashboard
from ui.question_page import QuestionPage
from ui.saved_page import SavedPage
from ui.settings_dialog import SettingsDialog
from ui.sidebar import NAV_ITEMS, Sidebar
from ui.statistics_page import StatisticsPage
from ui.subjects_page import SubjectsPage


class MainWindow(QMainWindow):
    theme_changed = Signal(str)

    def __init__(self, app, settings: SettingsStore, db: Database | None = None):
        super().__init__()
        self.app = app
        self.settings = settings
        self.db = db or Database()
        self.question_repository = QuestionRepository(self.db)
        self.attempt_repository = AttemptRepository(self.db)
        self.statistics_repository = StatisticsRepository(self.db)
        self.session = SessionTracker(SessionRepository(self.db), self)
        self.session.start()
        self._return_page = "Home"

        self.setWindowTitle("Study App")
        self.resize(1380, 860)
        self.setMinimumSize(1050, 680)
        if settings.window_geometry:
            self.restoreGeometry(settings.window_geometry)
=======
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout
from core.theme_manager import ThemeManager
from core.settings_store import SettingsStore
from database.database import Database
from database.question_repository import QuestionRepository
from database.attempt_repository import AttemptRepository
from database.session_repository import SessionRepository
from database.statistics_repository import StatisticsRepository
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.question_page import QuestionPage
from ui.settings_dialog import SettingsDialog
from ui.widgets import card, muted_label


class MainWindow(QMainWindow):
    def __init__(self, app, settings: SettingsStore):
        super().__init__()
        self.app = app
        self.settings = settings
        self.db = Database()
        self.question_repository = QuestionRepository(self.db)
        self.attempt_repository = AttemptRepository(self.db)
        self.session_repository = SessionRepository(self.db)
        self.statistics_repository = StatisticsRepository(self.db)
        self.setWindowTitle("Study App")
        self.resize(1380, 860)
        self.setMinimumSize(1050, 680)
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(central)

<<<<<<< HEAD
        self.subject_names = [row["name"] for row in self.question_repository.list_subjects()]
        self.sidebar = Sidebar(self.subject_names, settings.icon_pack,
                               self.show_page, self.open_settings)
        self.stack = QStackedWidget()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)

        self.dashboard = Dashboard(self.statistics_repository, self.attempt_repository, settings.theme)
        self.subjects_page = SubjectsPage(self.statistics_repository)
        self.statistics_page = StatisticsPage(self.statistics_repository, self.attempt_repository)
        self.saved_page = SavedPage(self.question_repository)
        self.question_page = QuestionPage(self.question_repository, self.attempt_repository)
        self.pages = {
            "Home": self.dashboard, "Subjects": self.subjects_page,
            "Statistics": self.statistics_page, "Saved": self.saved_page,
            "Question": self.question_page,
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        self.subjects_page.subject_requested.connect(self.show_page)
        self.saved_page.practice_requested.connect(self.practice_saved)
        self.question_page.back_requested.connect(lambda: self.show_page(self._return_page))
        self.question_page.answered.connect(lambda _: self.session.record_question())
        self.theme_changed.connect(self.dashboard.apply_theme)

        self.show_page("Home")

    # -- navigation ------------------------------------------------------
    def show_page(self, name):
        if name in NAV_ITEMS:
            self._return_page = name
            self.stack.setCurrentWidget(self.pages[name])
            self.sidebar.set_active(name)
        elif name in self.subject_names:
            self.question_page.set_subject(name)
            self.stack.setCurrentWidget(self.question_page)
            self.sidebar.set_active(name)
        else:
            self.show_page("Home")

    def practice_saved(self, ids):
        self.question_page.set_queue("Saved questions", ids)
        self.stack.setCurrentWidget(self.question_page)
        self.sidebar.set_active("")

    # -- actions ---------------------------------------------------------
=======
        self.stack = QStackedWidget()
        self.pages = {}
        self.sidebar = Sidebar(self.show_page, self.open_settings)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)

        self.dashboard = Dashboard(
            self.statistics_repository, self.attempt_repository, settings.theme
        )
        self.add_page("Home", self.dashboard)
        self.add_placeholder("Subjects", "Subjects", "Choose a subject from the sidebar to start practising.")
        self.add_placeholder("Statistics", "Statistics", "Statistics are calculated from your saved attempts and study sessions.")
        self.add_placeholder("Saved", "Saved questions", "Saved questions will appear here.")
        self.question_page = QuestionPage(
            self.question_repository, self.attempt_repository
        )
        self.add_page("Question", self.question_page)
        self.show_page("Home")

    def add_page(self, key, widget):
        self.pages[key] = widget
        self.stack.addWidget(widget)

    def add_placeholder(self, key, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 30, 34, 30)
        frame, box = card()
        heading = QLabel(title)
        heading.setStyleSheet("font-size: 27px; font-weight: 800;")
        box.addWidget(heading)
        box.addWidget(muted_label(description))
        layout.addWidget(frame)
        layout.addStretch()
        self.add_page(key, page)

    def show_page(self, name):
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])
            self.sidebar.set_active(name if name in self.sidebar.nav_buttons else "")
        elif name in ("NT", "AE", "Math", "CS_P", "CS", "English", "BS", "PuG", "Ethik"):
            self.question_page.set_subject(name)
            self.stack.setCurrentWidget(self.question_page)
            self.sidebar.set_active("")
        else:
            self.stack.setCurrentWidget(self.pages["Home"])

>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            dialog.save_values()
            ThemeManager.apply(self.app, self.settings.theme)
<<<<<<< HEAD
            self.sidebar.set_icon_pack(self.settings.icon_pack)
            self.theme_changed.emit(self.settings.theme)

    def closeEvent(self, event):
        self.session.stop()
        self.settings.set_window_geometry(self.saveGeometry())
=======
            self.dashboard.theme_name = self.settings.theme
            self.dashboard.refresh()

    def closeEvent(self, event):
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
        self.db.close()
        super().closeEvent(event)

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

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(central)

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
    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            dialog.save_values()
            ThemeManager.apply(self.app, self.settings.theme)
            self.sidebar.set_icon_pack(self.settings.icon_pack)
            self.theme_changed.emit(self.settings.theme)

    def closeEvent(self, event):
        self.session.stop()
        self.settings.set_window_geometry(self.saveGeometry())
        self.db.close()
        super().closeEvent(event)

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QWidget,
)

from core.csharp_question_generator import CSharpQuestionGenerator
from core.i18n import tr
from core.math_question_generator import MathQuestionGenerator
from core.relaunch import relaunch
from core.session_tracker import SessionTracker
from core.settings_store import SettingsStore
from core.theme_manager import ThemeManager
from core.updater import UpdateChecker, prompt_install
from core.webuntis import WebUntisExamManager
from database.attempt_repository import AttemptRepository
from database.database import Database
from database.info_repository import InfoRepository
from database.question_repository import QuestionRepository
from database.session_repository import SessionRepository
from database.statistics_repository import StatisticsRepository
from ui.dashboard import Dashboard
from ui.info_page import InfoPage
from ui.math_menu_page import MathMenuPage
from ui.question_page import QuestionPage
from ui.saved_page import SavedPage
from ui.settings_dialog import SettingsDialog
from ui.sidebar import NAV_ITEMS, Sidebar
from ui.statistics_page import StatisticsPage
from ui.subject_menu_page import SubjectMenuPage
from ui.subjects_page import SubjectsPage
from ui.subnetting_page import SubnettingPage

# Practice topics that generate a fresh AE exercise instead of a fixed queue.
AE_PRACTICE_TOPICS = (
    "Ausgabe",
    "Eingabe",
    "Ausgabe formatierung",
    "Variablen",
    "Operatoren",
    "Bedingungen",
    "Verzweigte Bedingungen",
)

AE_GROUPS = {
    "OOP": {
        "Praxis": list(AE_PRACTICE_TOPICS),
        "Theorie": ["Alles in einen Programm", "PAP"],
    },
    "DB / WEB": {
        "Themen": ["HTML", "CSS"],
    },
}

# Topics seeded once per subject so a fresh install is not empty.
SUBJECT_TOPIC_SEEDS = {
    "PuG": ("Arbeitsvertrag",),
    "BS": (
        "Bootvorgang",
        "BIOS update",
        "Windows Dateisysteme",
        "Festplatten",
        "Partitionierung",
        "Virtuelle PCs",
        "Batch",
        "Benutzer",
    ),
    "CS": (
        "IT-Systeme",
        "Komponenten",
        "Anschlüsse und Schnittstellen",
        "Neumann Architektur",
        "Bussystem",
    ),
    "CS_P": (
        "Strom- Spannungs- Wiederstandsmessung",
        "Elektrische Grundbasis",
        "Ohmsches Gesetz",
        "Reihenschaltung",
        "Parallelschaltung",
        "Mischschaltung",
    ),
    "NT": (
        "Grundbasis",
        "Ausdehnungen",
        "Topologien",
        "Architekturen",
        "Kommunikationsteilnehmer",
        "Adressbereiche",
        "Subnetting",
    ),
}


class MainWindow(QMainWindow):
    theme_changed = Signal(str)

    def __init__(self, app, settings: SettingsStore, db: Database | None = None):
        super().__init__()
        self.app = app
        self.settings = settings
        self.db = db or Database()
        self._owns_db = db is None

        self.question_repository = QuestionRepository(self.db)
        self._initialized_topic_subjects = set()
        self.math_question_generator = MathQuestionGenerator(self.question_repository)
        self.csharp_question_generator = CSharpQuestionGenerator(self.question_repository)
        self.attempt_repository = AttemptRepository(self.db)
        self.statistics_repository = StatisticsRepository(self.db)
        self.info_repository = InfoRepository(self.db)
        self.session = SessionTracker(SessionRepository(self.db), self)
        self._return_page = "Home"
        self._active_subject = None
        self._update_prompted = set()
        self.update_worker = None
        self.updater = UpdateChecker(self)
        self.updater.update_available.connect(self._offer_update)

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
        self.sidebar = Sidebar(
            self.subject_names, settings.icon_pack, self.show_page, self.open_settings
        )
        self.stack = QStackedWidget()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)

        self.dashboard = Dashboard(
            self.statistics_repository, self.attempt_repository, settings.theme
        )
        self.webuntis = WebUntisExamManager(self)
        self.webuntis.exams_updated.connect(self._set_exams)
        self.dashboard.study_exam_requested.connect(self.start_exam_practice)
        self.webuntis.timetable_updated.connect(self.dashboard.set_timetable)
        self.subjects_page = SubjectsPage(self.statistics_repository)
        self.statistics_page = StatisticsPage(
            self.statistics_repository, self.attempt_repository
        )
        self.saved_page = SavedPage(self.question_repository)
        self.info_page = InfoPage(self.info_repository)
        self.question_page = QuestionPage(
            self.question_repository, self.attempt_repository
        )
        self.math_menu_page = MathMenuPage()
        self.subject_menu_page = SubjectMenuPage()
        self.subnetting_page = SubnettingPage()
        self.pages = {
            "Home": self.dashboard,
            "Subjects": self.subjects_page,
            "Statistics": self.statistics_page,
            "Information": self.info_page,
            "Saved": self.saved_page,
            "Question": self.question_page,
            "MathMenu": self.math_menu_page,
            "SubjectMenu": self.subject_menu_page,
            "Subnetting": self.subnetting_page,
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        self.subjects_page.subject_requested.connect(self.show_page)
        self.math_menu_page.back_requested.connect(lambda: self.show_page("Subjects"))
        self.math_menu_page.question_type_requested.connect(self.start_math_practice)
        self.subject_menu_page.back_requested.connect(lambda: self.show_page("Subjects"))
        self.subject_menu_page.topic_requested.connect(self.start_subject_practice)
        self.subject_menu_page.exam_practice_requested.connect(self.start_exam_practice)
        self.subnetting_page.back_requested.connect(lambda: self.show_page("SubjectMenu"))
        self.saved_page.practice_requested.connect(self.practice_saved)
        self.question_page.back_requested.connect(lambda: self.show_page(self._return_page))
        self.question_page.answered.connect(lambda _correct: self.session.record_question())
        self.theme_changed.connect(self.dashboard.apply_theme)
        self.theme_changed.connect(self.question_page.apply_theme)
        self.question_page.apply_theme(settings.theme)

        self.session.start()
        self.show_page("Home")
        self.webuntis.check()
        self.updater.start()

    def show_page(self, name):
        if name in ("Math", "MathMenu"):
            self.show_math_menu()
        elif name == "SubjectMenu":
            self.stack.setCurrentWidget(self.subject_menu_page)
            self.sidebar.set_active(self._active_subject)
        elif name in NAV_ITEMS:
            self._return_page = name
            self.stack.setCurrentWidget(self.pages[name])
            self.sidebar.set_active(name)
            self._refresh_page(name)
        elif name in self.subject_names:
            self.show_subject_menu(name)
        else:
            self.show_page("Home")

    def _offer_update(self, commit):
        """Prompt once per new commit; "Later" silences that commit."""
        if commit in self._update_prompted:
            return
        if not prompt_install(self, commit):
            self._update_prompted.add(commit)

    def _refresh_page(self, name):
        if name == "Statistics":
            self.statistics_page.refresh()
        elif name == "Saved":
            self.saved_page.refresh()
        elif name == "Subjects":
            self.subjects_page.refresh()
        elif name == "Information":
            self.info_page.show_subjects()

    def show_math_menu(self):
        self._return_page = "Subjects"
        self.stack.setCurrentWidget(self.math_menu_page)
        self.sidebar.set_active("Math")

    def show_subject_menu(self, subject):
        self._return_page = "Subjects"
        self._active_subject = subject
        groups = AE_GROUPS if subject == "AE" else None
        if subject not in self._initialized_topic_subjects:
            seeds = list(SUBJECT_TOPIC_SEEDS.get(subject, ()))
            if groups:
                seeds.extend(
                    topic_name
                    for group in groups.values()
                    for subgroup_topics in group.values()
                    for topic_name in subgroup_topics
                )
            if seeds:
                self.question_repository.add_topics(subject, seeds)
            self._initialized_topic_subjects.add(subject)

        topics = self.question_repository.list_topics(subject)
        self.subject_menu_page.set_subject(
            subject, topics, groups=groups,
            exam_available=subject in self._subjects_with_upcoming_exams(),
        )
        self.stack.setCurrentWidget(self.subject_menu_page)
        self.sidebar.set_active(subject)

    @staticmethod
    def _exam_subject_code(exam):
        aliases = {
            "netzwerktechnik": "NT",
            "betriebssysteme": "BS",
            "computersystem": "CS",
            "computersystem praxis": "CS_P",
        }
        for value in (exam.get("subject_short"), exam.get("subject")):
            normalized = " ".join(str(value or "").strip().casefold().split())
            if normalized in {"nt", "bs", "cs", "cs_p"}:
                return normalized.upper()
            if normalized in aliases:
                return aliases[normalized]
        return None

    def _set_exams(self, exams, error=""):
        self.dashboard.set_exams(exams, error)
        if hasattr(self, "_active_subject") and self.stack.currentWidget() is self.subject_menu_page:
            self.show_subject_menu(self._active_subject)

    def _subjects_with_upcoming_exams(self):
        return {
            code for exam in self.dashboard.exams
            if (code := self._exam_subject_code(exam)) is not None
        }

    def _enter_practice(self, subject, return_page="SubjectMenu", page=None):
        """Show the practice page (or a dedicated exercise page) for a subject."""
        self._return_page = return_page
        self.stack.setCurrentWidget(page or self.question_page)
        self.sidebar.set_active(subject)

    def start_exam_practice(self, subject_or_code):
        code = self._exam_subject_code({
            "subject_short": subject_or_code,
            "subject": subject_or_code,
        })
        if code not in {"NT", "BS", "CS", "CS_P"}:
            return

        if code == "NT":
            # Exclude questions assigned to the exact "Topologien" topic.
            def rebuild():
                return self.question_repository.get_study_queue_excluding_topic(
                    code, "Topologien"
                )
        else:
            def rebuild():
                return self.question_repository.get_study_queue(code)

        self.question_page.set_queue(
            f"{code} · {tr('Exam practice')}", rebuild(), rebuild=rebuild
        )
        self._enter_practice(code)

    def start_subject_practice(self, subject, topic):
        if subject == "AE" and topic in AE_PRACTICE_TOPICS:
            self.question_page.set_generator(
                f"AE · {topic}",
                lambda: self.csharp_question_generator.generate_question_id(topic),
            )
            self._enter_practice(subject)
            return
        if subject == "NT" and topic == "Subnetting":
            self.subnetting_page.new_exercise()
            self._enter_practice(subject, page=self.subnetting_page)
            return

        if topic is None:
            def rebuild():
                return self.question_repository.get_study_queue(subject)
            heading = f"{subject} · {tr('Mixed practice')}"
        elif isinstance(topic, (tuple, list)):
            selected_topics = tuple(topic)

            def rebuild():
                return self.question_repository.get_topics_study_queue(
                    subject, selected_topics
                )
            heading = f"{subject} · {tr('Mixed practice')}"
        else:
            def rebuild():
                return self.question_repository.get_topic_study_queue(subject, topic)
            heading = f"{subject} · {topic}"

        self.question_page.set_queue(heading, rebuild(), rebuild=rebuild)
        self._enter_practice(subject)

    def start_math_practice(self, question_type):
        self.question_page.set_generator(
            "Math",
            lambda: self.math_question_generator.generate_question_id(question_type),
        )
        self._enter_practice("Math", return_page="MathMenu")

    def practice_saved(self, ids):
        self.question_page.set_queue(tr("Saved questions"), ids)
        self._enter_practice("Saved", return_page="Saved")

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if not dialog.exec():
            return
        previous_language = self.settings.language
        dialog.save_values()
        if self.settings.language != previous_language:
            self._relaunch_for_language()
            return
        ThemeManager.apply(self.app, self.settings.theme)
        self.sidebar.set_icon_pack(self.settings.icon_pack)
        self.dashboard.apply_theme(self.settings.theme)
        self.question_page.apply_theme(self.settings.theme)

    def _relaunch_for_language(self):
        """Restart straight into the new language instead of asking for it."""
        if not relaunch():
            QMessageBox.warning(
                self,
                tr("Language changed"),
                tr("Restart Study App to apply the new language."),
            )
            return
        self.close()
        self.app.quit()

    def closeEvent(self, event):
        self.updater.stop()
        self.webuntis.shutdown()
        self.session.stop()
        self.settings.set_window_geometry(self.saveGeometry())
        self.settings.sync()
        if self._owns_db:
            self.db.close()
        super().closeEvent(event)

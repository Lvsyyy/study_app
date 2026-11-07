"""Reference information: subjects → topics → sections, plus one long document.

The page is read-only. It shows exactly the text stored in the `infos` table, so
the study material and the questions never drift apart.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr
from ui.widgets import (
    action_button,
    card,
    clear_layout,
    muted_label,
    section_title,
    title_label,
)

SUBJECT_COLUMNS = 3


class InfoPage(QWidget):
    def __init__(self, infos):
        super().__init__()
        self.infos = infos
        self._all_back = self.show_subjects
        self._anchors = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(0)

        self.stack = QStackedWidget()
        root.addWidget(self.stack)
        self.subjects_view = self._build_subjects_view()
        self.topics_view = self._build_topics_view()
        self.topic_view = self._build_topic_view()
        self.all_view = self._build_all_view()
        for view in (self.subjects_view, self.topics_view, self.topic_view, self.all_view):
            self.stack.addWidget(view)
        self.show_subjects()

    # ---------------------------------------------------------------- subjects
    def _build_subjects_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.addWidget(title_label("Information"))
        titles.addWidget(muted_label("Pick a subject to read"))
        header.addLayout(titles)
        header.addStretch()
        show_all = action_button("Show all information", primary=True)
        show_all.clicked.connect(lambda: self.show_all())
        header.addWidget(show_all)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        self.subjects_grid = QGridLayout(content)
        self.subjects_grid.setContentsMargins(0, 0, 8, 0)
        self.subjects_grid.setSpacing(14)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        return view

    def show_subjects(self):
        clear_layout(self.subjects_grid)
        for index, subject in enumerate(self.infos.list_subjects()):
            frame, box = card()
            box.addWidget(section_title(subject["name"]))
            box.addWidget(
                muted_label(
                    tr("{count} section(s)", count=subject["sections"])
                    if subject["sections"]
                    else tr("No information for this subject yet.")
                )
            )
            open_button = action_button("Open", primary=subject["sections"] > 0)
            open_button.clicked.connect(
                lambda _checked=False, name=subject["name"]: self.show_topics(name)
            )
            box.addWidget(open_button)
            self.subjects_grid.addWidget(
                frame, index // SUBJECT_COLUMNS, index % SUBJECT_COLUMNS
            )
        self.subjects_grid.setRowStretch(self.subjects_grid.rowCount(), 1)
        self.stack.setCurrentWidget(self.subjects_view)

    # ------------------------------------------------------------------ topics
    def _build_topics_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        back = action_button("←  Back")
        back.clicked.connect(self.show_subjects)
        layout.addWidget(back, 0)

        self.topics_title = title_label("Information")
        layout.addWidget(self.topics_title)

        header = QHBoxLayout()
        header.addWidget(muted_label("All information in this subject"))
        header.addStretch()
        self.subject_all_button = action_button("All info", primary=True)
        self.subject_all_button.clicked.connect(self._show_subject_all)
        header.addWidget(self.subject_all_button)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        self.topics_layout = QVBoxLayout(content)
        self.topics_layout.setContentsMargins(0, 0, 8, 0)
        self.topics_layout.setSpacing(12)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        return view

    def show_topics(self, subject):
        self._subject = subject
        self.topics_title.setText(subject)
        clear_layout(self.topics_layout)
        topics = self.infos.list_topics(subject)
        if not topics:
            self.topics_layout.addWidget(muted_label("No information for this subject yet."))
        grid = QGridLayout()
        grid.setSpacing(10)
        for index, topic in enumerate(topics):
            button = action_button(
                tr("{topic}  ·  {count} section(s)", topic=topic["name"], count=topic["sections"])
                if topic["sections"]
                else tr("{topic}  ·  empty", topic=topic["name"])
            )
            button.setMinimumHeight(48)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(
                lambda _checked=False, name=topic["name"], subject=subject:
                    self.show_topic(subject, name)
            )
            grid.addWidget(button, index // 2, index % 2)
        for column in range(2):
            grid.setColumnStretch(column, 1)
        self.topics_layout.addLayout(grid)
        self.topics_layout.addStretch()
        self.stack.setCurrentWidget(self.topics_view)

    def _show_subject_all(self):
        self.show_all(self._subject, return_to=lambda: self.show_topics(self._subject))

    # ------------------------------------------------------------------- topic
    def _build_topic_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.topic_back = action_button("←  Back")
        self.topic_back.clicked.connect(self._leave_topic)
        layout.addWidget(self.topic_back, 0)

        self.topic_title = title_label("Information")
        layout.addWidget(self.topic_title)
        self.topic_subtitle = muted_label()
        layout.addWidget(self.topic_subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        self.topic_layout = QVBoxLayout(content)
        self.topic_layout.setContentsMargins(0, 0, 8, 0)
        self.topic_layout.setSpacing(12)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        return view

    def _leave_topic(self):
        self.show_topics(self._topic_subject)

    def show_topic(self, subject, topic):
        self._topic_subject = subject
        self.topic_title.setText(topic)
        self.topic_subtitle.setText(subject)
        clear_layout(self.topic_layout)
        sections = self.infos.topic_sections(subject, topic)
        if not sections:
            self.topic_layout.addWidget(muted_label("No information for this topic yet."))
        for row in sections:
            frame, box = card()
            box.addWidget(section_title(row["heading"]))
            box.addWidget(self._body_label(row["body"]))
            self.topic_layout.addWidget(frame)
        self.topic_layout.addStretch()
        self.stack.setCurrentWidget(self.topic_view)

    # -------------------------------------------------------------- all sections
    def _build_all_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.all_back = action_button("←  Back")
        self.all_back.clicked.connect(self._leave_all)
        layout.addWidget(self.all_back, 0)

        self.all_title = title_label("All info")
        layout.addWidget(self.all_title)
        layout.addWidget(muted_label("Every subject and topic in one document"))

        body = QHBoxLayout()
        body.setSpacing(16)

        self.all_scroll = QScrollArea()
        self.all_scroll.setWidgetResizable(True)
        self.all_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.all_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        self.all_content = QVBoxLayout(content)
        self.all_content.setContentsMargins(0, 0, 8, 0)
        self.all_content.setSpacing(10)
        self.all_scroll.setWidget(content)
        body.addWidget(self.all_scroll, 1)

        nav_column = QVBoxLayout()
        nav_column.setSpacing(6)
        nav_column.addWidget(muted_label("Contents"))
        self.all_nav = QListWidget()
        self.all_nav.setFixedWidth(250)
        self.all_nav.setWordWrap(True)
        self.all_nav.currentItemChanged.connect(self._jump_to_section)
        nav_column.addWidget(self.all_nav, 1)
        body.addLayout(nav_column)

        layout.addLayout(body, 1)
        return view

    def _leave_all(self):
        self._all_back()

    def show_all(self, subject=None, return_to=None):
        self._all_back = return_to or self.show_subjects
        self.all_title.setText(subject or tr("All info"))
        clear_layout(self.all_content)
        self.all_nav.clear()
        self._anchors = {}

        rows = [
            row for row in self.infos.all_sections()
            if subject is None or row["subject"] == subject
        ]
        if not rows:
            self.all_content.addWidget(muted_label("No information for this subject yet."))

        current_subject = current_topic = None
        for row in rows:
            if row["subject"] != current_subject:
                current_subject = row["subject"]
                current_topic = None
                self.all_content.addWidget(title_label(current_subject))
            if row["topic"] != current_topic:
                current_topic = row["topic"]
                anchor = section_title(current_topic)
                self.all_content.addWidget(anchor)
                key = f"{current_subject} · {current_topic}"
                self.all_nav.addItem(QListWidgetItem(key))
                self._anchors[key] = anchor
            frame, box = card()
            box.addWidget(section_title(row["heading"]))
            box.addWidget(self._body_label(row["body"]))
            self.all_content.addWidget(frame)
        self.all_content.addStretch()
        self.stack.setCurrentWidget(self.all_view)

    def _jump_to_section(self, *_):
        item = self.all_nav.currentItem()
        if item is None:
            return
        anchor = self._anchors.get(item.text())
        if anchor is not None:
            self.all_scroll.ensureWidgetVisible(anchor, 0, 12)

    @staticmethod
    def _body_label(text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

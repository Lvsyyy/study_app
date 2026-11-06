from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from core.i18n import tr
from ui.widgets import action_button, card, clear_layout, muted_label, section_title, title_label


class SubjectMenuPage(QWidget):
    back_requested = Signal()
    topic_requested = Signal(str, object)
    exam_practice_requested = Signal(str)

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(18)

        back = action_button("←  Back")
        back.clicked.connect(self.back_requested)
        root.addWidget(back, 0)

        self.title = title_label("Subject")
        root.addWidget(self.title)
        root.addWidget(muted_label("Choose a topic or practise a selection."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content_widget = QWidget()
        self.content = QVBoxLayout(content_widget)
        self.content.setContentsMargins(0, 0, 8, 0)
        self.content.setSpacing(14)
        self.content.addStretch()

        scroll.setWidget(content_widget)
        root.addWidget(scroll, 1)

    def set_subject(self, subject, topics, groups=None, exam_available=False):
        self.title.setText(subject)
        clear_layout(self.content)
        self.content.addStretch()

        self._add_mix_card(
            subject,
            tr("Mixed practice"),
            tr("Questions from every topic in this subject"),
            None,
            exam_available=exam_available,
        )

        grouped_topics = set()
        if groups:
            for group_name, subgroups in groups.items():
                group_frame, group_layout = card(padding=18)
                group_layout.addWidget(section_title(group_name))

                group_topics = [
                    topic
                    for subgroup_topics in subgroups.values()
                    for topic in subgroup_topics
                ]
                grouped_topics.update(group_topics)
                mix_button = action_button(
                    tr("Mixed {group} practice", group=group_name), primary=True
                )
                mix_button.setMinimumHeight(44)
                mix_button.clicked.connect(
                    lambda _checked=False, name=subject, selected=tuple(group_topics):
                        self.topic_requested.emit(name, selected)
                )
                group_layout.addWidget(mix_button)

                for subgroup_name, subgroup_topics in subgroups.items():
                    group_layout.addWidget(section_title(subgroup_name))
                    self._add_topic_grid(group_layout, subject, subgroup_topics, columns=2)

                self.content.insertWidget(self.content.count() - 1, group_frame)

        remaining_topics = [topic for topic in topics if topic not in grouped_topics]
        if remaining_topics:
            topics_frame, topics_layout = card(padding=18)
            topics_layout.addWidget(section_title("Topics"))
            self._add_topic_grid(topics_layout, subject, remaining_topics, columns=2)
            self.content.insertWidget(self.content.count() - 1, topics_frame)
        elif not groups:
            self.content.insertWidget(
                self.content.count() - 1,
                muted_label("No topics available yet."),
            )

    def _add_mix_card(self, subject, heading, description, selected_topics, exam_available=False):
        mix_frame, mix_layout = card(padding=18)
        mix_layout.addWidget(section_title(heading))
        mix_layout.addWidget(muted_label(description))
        mix_button = action_button("Start mixed practice", primary=True)
        mix_button.setMinimumHeight(44)
        mix_button.clicked.connect(
            lambda _checked=False, name=subject, selected=selected_topics:
                self.topic_requested.emit(name, selected)
        )
        if exam_available:
            buttons = QGridLayout()
            buttons.setSpacing(10)
            buttons.addWidget(mix_button, 0, 0)
            exam_button = action_button("Study for exam")
            exam_button.setMinimumHeight(44)
            exam_button.clicked.connect(
                lambda _checked=False, name=subject:
                    self.exam_practice_requested.emit(name)
            )
            buttons.addWidget(exam_button, 0, 1)
            buttons.setColumnStretch(0, 1)
            buttons.setColumnStretch(1, 1)
            mix_layout.addLayout(buttons)
        else:
            mix_layout.addWidget(mix_button)
        self.content.insertWidget(self.content.count() - 1, mix_frame)

    def _add_topic_grid(self, layout, subject, topics, columns=2):
        if not topics:
            layout.addWidget(muted_label("No topics available yet."))
            return

        grid = QGridLayout()
        grid.setSpacing(10)
        for index, topic in enumerate(topics):
            button = action_button(topic)
            button.setMinimumHeight(48)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(
                lambda _checked=False, name=subject, selected=topic:
                    self.topic_requested.emit(name, selected)
            )
            grid.addWidget(button, index // columns, index % columns)

        for column in range(columns):
            grid.setColumnStretch(column, 1)
        layout.addLayout(grid)

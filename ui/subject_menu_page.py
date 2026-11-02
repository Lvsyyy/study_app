from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QWidget

from ui.widgets import action_button, card, clear_layout, muted_label, section_title, title_label


class SubjectMenuPage(QWidget):
    back_requested = Signal()
    topic_requested = Signal(str, object)

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

        self.content = QVBoxLayout()
        self.content.setSpacing(14)
        root.addLayout(self.content)
        root.addStretch()

    def set_subject(self, subject, topics, groups=None):
        self.title.setText(subject)
        clear_layout(self.content)

        self._add_mix_card(
            subject,
            "Mixed practice",
            "Questions from every topic in this subject",
            None,
        )

        if groups:
            for group_name, subgroups in groups.items():
                group_frame, group_layout = card(padding=18)
                group_layout.addWidget(section_title(group_name))

                group_topics = [
                    topic
                    for subgroup_topics in subgroups.values()
                    for topic in subgroup_topics
                ]
                mix_button = action_button(f"Mixed {group_name} practice", primary=True)
                mix_button.clicked.connect(
                    lambda _checked=False, name=subject, selected=tuple(group_topics):
                        self.topic_requested.emit(name, selected)
                )
                group_layout.addWidget(mix_button)

                for subgroup_name, subgroup_topics in subgroups.items():
                    group_layout.addWidget(section_title(subgroup_name))
                    self._add_topic_grid(group_layout, subject, subgroup_topics)

                self.content.addWidget(group_frame)
        elif topics:
            topics_frame, topics_layout = card(padding=18)
            topics_layout.addWidget(section_title("Topics"))
            self._add_topic_grid(topics_layout, subject, topics)
            self.content.addWidget(topics_frame)
        else:
            self.content.addWidget(muted_label("No topics available yet."))

    def _add_mix_card(self, subject, heading, description, selected_topics):
        mix_frame, mix_layout = card(padding=18)
        mix_layout.addWidget(section_title(heading))
        mix_layout.addWidget(muted_label(description))
        mix_button = action_button("Start mixed practice", primary=True)
        mix_button.clicked.connect(
            lambda _checked=False, name=subject, selected=selected_topics:
                self.topic_requested.emit(name, selected)
        )
        mix_layout.addWidget(mix_button)
        self.content.addWidget(mix_frame)

    @staticmethod
    def _add_topic_grid(layout, subject, topics):
        if not topics:
            layout.addWidget(muted_label("No topics available yet."))
            return

        grid = QGridLayout()
        grid.setSpacing(10)
        for index, topic in enumerate(topics):
            button = action_button(topic)
            button.clicked.connect(
                lambda _checked=False, name=subject, selected=topic:
                    self.topic_requested.emit(name, selected)
            )
            grid.addWidget(button, index // 3, index % 3)
        layout.addLayout(grid)

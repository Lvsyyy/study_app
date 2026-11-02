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
        root.addWidget(muted_label("Choose a topic or practise all topics."))

        self.content = QVBoxLayout()
        self.content.setSpacing(14)
        root.addLayout(self.content)
        root.addStretch()

    def set_subject(self, subject, topics):
        self.title.setText(subject)
        clear_layout(self.content)

        mix_frame, mix_layout = card(padding=18)
        mix_layout.addWidget(section_title("Mixed practice"))
        mix_layout.addWidget(muted_label("Questions from every topic in this subject"))
        mix_button = action_button("Start mixed practice", primary=True)
        mix_button.clicked.connect(
            lambda _checked=False, name=subject: self.topic_requested.emit(name, None)
        )
        mix_layout.addWidget(mix_button)
        self.content.addWidget(mix_frame)

        if topics:
            topics_frame, topics_layout = card(padding=18)
            topics_layout.addWidget(section_title("Topics"))
            grid = QGridLayout()
            grid.setSpacing(10)
            for index, topic in enumerate(topics):
                button = action_button(topic)
                button.clicked.connect(
                    lambda _checked=False, name=subject, selected=topic:
                        self.topic_requested.emit(name, selected)
                )
                grid.addWidget(button, index // 3, index % 3)
            topics_layout.addLayout(grid)
            self.content.addWidget(topics_frame)
        else:
            self.content.addWidget(muted_label("No topics available yet."))

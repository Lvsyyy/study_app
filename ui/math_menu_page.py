from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from core.math_question_generator import MATH_QUESTION_TYPES
from ui.widgets import action_button, card, muted_label, section_title, title_label


class MathMenuPage(QWidget):
    back_requested = Signal()
    question_type_requested = Signal(str)

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(18)

        back = action_button("←  Back")
        back.clicked.connect(self.back_requested)
        root.addWidget(back, 0)
        root.addWidget(title_label("Math"))
        root.addWidget(muted_label("Choose which type of question to practise."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content_widget = QWidget()
        content = QVBoxLayout(content_widget)
        content.setContentsMargins(0, 0, 8, 0)
        content.setSpacing(14)

        mix_frame, mix_layout = card(padding=18)
        mix_layout.addWidget(section_title("Mixed practice"))
        mix_layout.addWidget(muted_label("All question types in random order"))
        mix_button = action_button("Start mixed practice", primary=True)
        mix_button.setMinimumHeight(44)
        mix_button.clicked.connect(lambda: self.question_type_requested.emit("mix"))
        mix_layout.addWidget(mix_button)
        content.addWidget(mix_frame)

        types_frame, types_layout = card(padding=18)
        types_layout.addWidget(section_title("Question types"))
        grid = QGridLayout()
        grid.setSpacing(10)
        for index, (key, label) in enumerate(MATH_QUESTION_TYPES):
            button = action_button(label)
            button.setMinimumHeight(48)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(
                lambda _checked=False, question_type=key:
                    self.question_type_requested.emit(question_type)
            )
            grid.addWidget(button, index // 2, index % 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        types_layout.addLayout(grid)
        content.addWidget(types_frame)
        content.addStretch()

        scroll.setWidget(content_widget)
        root.addWidget(scroll, 1)

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QWidget

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

        mix_frame, mix_layout = card(padding=18)
        mix_layout.addWidget(section_title("Mixed practice"))
        mix_layout.addWidget(muted_label("All question types in random order"))
        mix_button = action_button("Start mixed practice", primary=True)
        mix_button.clicked.connect(lambda: self.question_type_requested.emit("mix"))
        mix_layout.addWidget(mix_button)
        root.addWidget(mix_frame)

        types_frame, types_layout = card(padding=18)
        types_layout.addWidget(section_title("Question types"))
        grid = QGridLayout()
        grid.setSpacing(10)
        for index, (key, label) in enumerate(MATH_QUESTION_TYPES):
            button = action_button(label)
            button.clicked.connect(
                lambda _checked=False, question_type=key:
                    self.question_type_requested.emit(question_type)
            )
            grid.addWidget(button, index // 3, index % 3)
        types_layout.addLayout(grid)
        root.addWidget(types_frame)
        root.addStretch()

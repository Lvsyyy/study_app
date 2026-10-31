<<<<<<< HEAD
from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QPushButton, QVBoxLayout


def repolish(widget):
    """Re-apply the stylesheet after a dynamic property changed."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
=======
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f


def card(parent=None, padding=16):
    frame = QFrame(parent)
    frame.setProperty("role", "card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(padding, padding, padding, padding)
    layout.setSpacing(8)
    return frame, layout


<<<<<<< HEAD
def _role_label(text, role):
    label = QLabel(text)
    label.setProperty("role", role)
    return label


def title_label(text):
    return _role_label(text, "title")


def section_title(text):
    return _role_label(text, "section")


def muted_label(text=""):
=======
def muted_label(text):
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
    label = QLabel(text)
    label.setProperty("muted", True)
    return label


def action_button(text, primary=False):
    button = QPushButton(text)
    if primary:
        button.setProperty("primary", True)
    return button


<<<<<<< HEAD
def stat_card(name, detail=""):
    """A small card with a big number. Returns (frame, number_label, detail_label)."""
    frame, box = card()
    box.addWidget(muted_label(name))
    number = _role_label("0", "stat")
    box.addWidget(number)
    detail_label = muted_label(detail)
    box.addWidget(detail_label)
    return frame, number, detail_label


def progress_bar(value):
    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(int(value))
    bar.setTextVisible(False)
    return bar


def set_state(label, state):
    """Colour a label 'good', 'bad' or neutral (None)."""
    label.setProperty("state", state)
    repolish(label)


def clear_layout(layout):
    """Remove and delete everything in a layout, including nested layouts."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())
            item.layout().deleteLater()
=======
def section_title(text):
    label = QLabel(text)
    label.setStyleSheet("font-size: 16px; font-weight: 700;")
    return label
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f

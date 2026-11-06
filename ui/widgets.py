from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from core.i18n import tr


def repolish(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def card(parent=None, padding=16):
    frame = QFrame(parent)
    frame.setProperty("role", "card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(padding, padding, padding, padding)
    layout.setSpacing(8)
    return frame, layout


def _role_label(text, role):
    label = QLabel(tr(text))
    label.setProperty("role", role)
    return label


def title_label(text):
    return _role_label(text, "title")


def section_title(text):
    return _role_label(text, "section")


def muted_label(text=""):
    label = QLabel(tr(text))
    label.setProperty("muted", True)
    return label


def action_button(text, primary=False):
    button = QPushButton(tr(text))
    if primary:
        button.setProperty("primary", True)
    return button


def stat_card(name, detail=""):
    frame, layout = card()
    layout.addWidget(muted_label(name))
    number = _role_label("0", "stat")
    layout.addWidget(number)
    detail_label = muted_label(detail)
    layout.addWidget(detail_label)
    return frame, number, detail_label


def progress_bar(value):
    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(max(0, min(100, int(value or 0))))
    bar.setTextVisible(False)
    return bar


def set_state(label, state):
    label.setProperty("state", state)
    repolish(label)


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif child_layout is not None:
            clear_layout(child_layout)
            child_layout.deleteLater()

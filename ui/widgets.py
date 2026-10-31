from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


def card(parent=None, padding=16):
    frame = QFrame(parent)
    frame.setProperty("role", "card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(padding, padding, padding, padding)
    layout.setSpacing(8)
    return frame, layout


def muted_label(text):
    label = QLabel(text)
    label.setProperty("muted", True)
    return label


def action_button(text, primary=False):
    button = QPushButton(text)
    if primary:
        button.setProperty("primary", True)
    return button


def section_title(text):
    label = QLabel(text)
    label.setStyleSheet("font-size: 16px; font-weight: 700;")
    return label

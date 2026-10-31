from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt


class Sidebar(QWidget):
    def __init__(self, on_navigate, on_settings):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(218)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 22, 14, 16)
        layout.setSpacing(7)

        brand = QLabel("◈  STUDY")
        brand.setStyleSheet("font-size: 18px; font-weight: 800; padding: 0 8px 20px 8px;")
        layout.addWidget(brand)

        self.nav_buttons = {}
        entries = [
            ("Home", "⌂"), ("Subjects", "▦"), ("Statistics", "▤"), ("Saved", "◇")
        ]
        for name, glyph in entries:
            button = QPushButton(f"{glyph}   {name}")
            button.setProperty("nav", True)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, n=name: on_navigate(n))
            layout.addWidget(button)
            self.nav_buttons[name] = button

        label = QLabel("SUBJECTS")
        label.setProperty("muted", True)
        label.setStyleSheet("font-size: 10px; font-weight: 700; padding: 20px 8px 5px;")
        layout.addWidget(label)

        subjects = ["NT", "AE", "Math", "CS_P", "CS", "English", "BS", "PuG", "Ethik"]
        for subject in subjects:
            button = QPushButton(f"  {subject}")
            button.setProperty("nav", True)
            button.clicked.connect(lambda checked=False, s=subject: on_navigate(s))
            layout.addWidget(button)

        layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        settings = QPushButton("⚙   Settings")
        settings.setProperty("nav", True)
        settings.clicked.connect(on_settings)
        layout.addWidget(settings)
        self.nav_buttons["Home"].setChecked(True)

    def set_active(self, name):
        for key, button in self.nav_buttons.items():
            button.setChecked(key == name)

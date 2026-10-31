from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from core.icons import icon

NAV_ITEMS = ("Home", "Subjects", "Statistics", "Saved")


class Sidebar(QWidget):
    def __init__(self, subjects, icon_pack, on_navigate, on_settings):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedWidth(218)
        self.icon_pack = icon_pack
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

        self.brand = QLabel()
        self.brand.setProperty("role", "brand")
        layout.addWidget(self.brand)

        self.buttons = {}  # page/subject name -> button
        self._icon_buttons = {}  # icon key -> (button, label)
        for name in NAV_ITEMS:
            button = self._nav_button(lambda _=False, n=name: on_navigate(n))
            layout.addWidget(button)
            self.buttons[name] = button
            self._icon_buttons[name] = (button, name)

        caption = QLabel("SUBJECTS")
        caption.setProperty("role", "caption")
        layout.addWidget(caption)
        for subject in subjects:
            button = self._nav_button(lambda _=False, s=subject: on_navigate(s))
            button.setText(f"  {subject}")
            layout.addWidget(button)
            self.buttons[subject] = button

        layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        settings = self._nav_button(on_settings, checkable=False)
        layout.addWidget(settings)
        self._icon_buttons["Settings"] = (settings, "Settings")

        self.set_icon_pack(icon_pack)
        self.set_active("Home")

    @staticmethod
    def _nav_button(slot, checkable=True):
        button = QPushButton()
        button.setProperty("nav", True)
        button.setCheckable(checkable)
        button.clicked.connect(slot)
        return button

    def set_icon_pack(self, pack):
        self.icon_pack = pack
        self.brand.setText(f"{icon('brand', pack)}  STUDY")
        for key, (button, label) in self._icon_buttons.items():
            button.setText(f"{icon(key, pack)}   {label}")

    def set_active(self, name):
        for key, button in self.buttons.items():
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

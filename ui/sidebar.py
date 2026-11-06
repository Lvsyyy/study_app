from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from core.i18n import tr
from core.icons import icon

NAV_ITEMS = ("Home", "Subjects", "Statistics", "Saved")


class Sidebar(QWidget):
    def __init__(self, subjects, icon_pack, on_navigate, on_settings):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(218)
        self.icon_pack = icon_pack

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 22, 14, 16)
        layout.setSpacing(7)

        self.brand = QLabel()
        self.brand.setProperty("role", "brand")
        layout.addWidget(self.brand)

        self.buttons = {}
        self._icon_buttons = {}
        self.nav_buttons = {}
        for name in NAV_ITEMS:
            button = self._nav_button(lambda _=False, target=name: on_navigate(target))
            layout.addWidget(button)
            self.buttons[name] = button
            self.nav_buttons[name] = button
            self._icon_buttons[name] = (button, name)

        caption = QLabel(tr("SUBJECTS"))
        caption.setProperty("role", "caption")
        layout.addWidget(caption)
        self.subject_buttons = {}
        for subject in subjects:
            button = self._nav_button(lambda _=False, target=subject: on_navigate(target))
            button.setText(subject)
            layout.addWidget(button)
            self.buttons[subject] = button
            self.subject_buttons[subject] = button

        layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
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
            button.setText(f"{icon(key, pack)}   {tr(label)}")
        for subject, button in self.subject_buttons.items():
            button.setText(subject)

    def set_active(self, name):
        for key, button in self.buttons.items():
            button.setChecked(key == name)

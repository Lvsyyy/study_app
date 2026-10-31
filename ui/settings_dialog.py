from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton
from core.settings_store import SettingsStore
from ui.widgets import muted_label


class SettingsDialog(QDialog):
    def __init__(self, settings: SettingsStore, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(340)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Appearance"))
        layout.addWidget(muted_label("Color theme"))
        self.theme = QComboBox()
        self.theme.addItems(SettingsStore.THEMES)
        self.theme.setCurrentText(settings.theme)
        layout.addWidget(self.theme)

        layout.addWidget(muted_label("Icon pack"))
        self.icons = QComboBox()
        self.icons.addItems(SettingsStore.ICON_PACKS)
        self.icons.setCurrentText(settings.icon_pack)
        layout.addWidget(self.icons)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        save = QPushButton("Save")
        save.setProperty("primary", True)
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def save_values(self):
        self.settings.set_theme(self.theme.currentText())
        self.settings.set_icon_pack(self.icons.currentText())

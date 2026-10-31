from PySide6.QtCore import QSettings


class SettingsStore:
    THEMES = ("Rose Pine", "Catppuccin Mocha", "Dracula")
    ICON_PACKS = ("Catppuccin Icons", "Lucide Icons")

    def __init__(self):
        self._settings = QSettings("Lvsy", "StudyApp")

    @property
    def theme(self):
        return self._settings.value("appearance/theme", "Rose Pine")

    @property
    def icon_pack(self):
        return self._settings.value("appearance/icon_pack", "Lucide Icons")

    def set_theme(self, value: str):
        if value in self.THEMES:
            self._settings.setValue("appearance/theme", value)

    def set_icon_pack(self, value: str):
        if value in self.ICON_PACKS:
            self._settings.setValue("appearance/icon_pack", value)

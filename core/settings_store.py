from PySide6.QtCore import QByteArray, QSettings

from core.icons import ICON_PACKS


class SettingsStore:
    THEMES = ("Rose Pine", "Catppuccin Mocha", "Dracula")
    ICON_PACKS = tuple(ICON_PACKS)

    def __init__(self, settings=None):
        self._settings = settings or QSettings("Lvsy", "StudyApp")

    def _choice(self, key, allowed, default):
        value = self._settings.value(key, default)
        return value if value in allowed else default

    @property
    def theme(self):
        return self._choice("appearance/theme", self.THEMES, self.THEMES[0])

    @property
    def icon_pack(self):
        return self._choice("appearance/icon_pack", self.ICON_PACKS, "Lucide Icons")

    @property
    def window_geometry(self):
        value = self._settings.value("window/geometry")
        return value if isinstance(value, QByteArray) and not value.isEmpty() else None

    def set_theme(self, value):
        if value in self.THEMES:
            self._settings.setValue("appearance/theme", value)

    def set_icon_pack(self, value):
        if value in self.ICON_PACKS:
            self._settings.setValue("appearance/icon_pack", value)

    def set_window_geometry(self, value):
        self._settings.setValue("window/geometry", value)

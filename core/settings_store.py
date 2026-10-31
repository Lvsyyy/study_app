<<<<<<< HEAD
from PySide6.QtCore import QByteArray, QSettings

from core.icons import ICON_PACKS
=======
from PySide6.QtCore import QSettings
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f


class SettingsStore:
    THEMES = ("Rose Pine", "Catppuccin Mocha", "Dracula")
<<<<<<< HEAD
    ICON_PACKS = tuple(ICON_PACKS)

    def __init__(self, settings: QSettings | None = None):
        self._settings = settings or QSettings("Lvsy", "StudyApp")

    def _choice(self, key, allowed, default):
        value = self._settings.value(key, default)
        return value if value in allowed else default

    @property
    def theme(self) -> str:
        return self._choice("appearance/theme", self.THEMES, self.THEMES[0])

    @property
    def icon_pack(self) -> str:
        return self._choice("appearance/icon_pack", self.ICON_PACKS, "Lucide Icons")
=======
    ICON_PACKS = ("Catppuccin Icons", "Lucide Icons")

    def __init__(self):
        self._settings = QSettings("Lvsy", "StudyApp")

    @property
    def theme(self):
        return self._settings.value("appearance/theme", "Rose Pine")

    @property
    def icon_pack(self):
        return self._settings.value("appearance/icon_pack", "Lucide Icons")
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f

    def set_theme(self, value: str):
        if value in self.THEMES:
            self._settings.setValue("appearance/theme", value)

    def set_icon_pack(self, value: str):
        if value in self.ICON_PACKS:
            self._settings.setValue("appearance/icon_pack", value)
<<<<<<< HEAD

    @property
    def window_geometry(self) -> QByteArray | None:
        value = self._settings.value("window/geometry")
        return value if isinstance(value, QByteArray) and not value.isEmpty() else None

    def set_window_geometry(self, value: QByteArray):
        self._settings.setValue("window/geometry", value)
=======
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f

from PySide6.QtCore import QByteArray, QSettings

from core.i18n import DEFAULT_LANGUAGE, LANGUAGES
from core.icons import ICON_PACKS


class SettingsStore:
    THEMES = ("Rose Pine", "Catppuccin Mocha", "Dracula")
    ICON_PACKS = tuple(ICON_PACKS)
    LANGUAGES = LANGUAGES
    # Deliberately not "general/...": Qt's INI backend escapes a group called
    # "general" as "[%General]" and reads it back as "General/...", so a value
    # saved there is never found again by the next process.
    LANGUAGE_KEY = "ui/language"

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
    def language(self):
        value = self._settings.value(
            self.LANGUAGE_KEY,
            self._settings.value("general/language", DEFAULT_LANGUAGE),
        )
        return value if value in self.LANGUAGES else DEFAULT_LANGUAGE

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

    def set_language(self, value):
        if value in self.LANGUAGES:
            self._settings.setValue(self.LANGUAGE_KEY, value)

    def set_window_geometry(self, value):
        self._settings.setValue("window/geometry", value)

    def sync(self):
        """Write pending changes to disk immediately.

        QSettings flushes lazily, so a value saved right before the app closes
        would otherwise be lost on the next launch.
        """
        self._settings.sync()

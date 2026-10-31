from PySide6.QtWidgets import QApplication

<<<<<<< HEAD
=======

>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
PALETTES = {
    "Rose Pine": {
        "bg": "#191724", "panel": "#1f1d2e", "card": "#26233a",
        "raised": "#2a273f", "text": "#e0def4", "muted": "#908caa",
        "accent": "#eb6f92", "accent_hover": "#f08aa8",
        "border": "#393552", "good": "#9ccfd8", "bad": "#eb6f92",
        "heat": ["#26233a", "#52445d", "#9a647c", "#d18b75", "#ebbcba"],
    },
    "Catppuccin Mocha": {
        "bg": "#1e1e2e", "panel": "#181825", "card": "#313244",
        "raised": "#45475a", "text": "#cdd6f4", "muted": "#a6adc8",
        "accent": "#cba6f7", "accent_hover": "#d9b8ff",
        "border": "#45475a", "good": "#a6e3a1", "bad": "#f38ba8",
        "heat": ["#313244", "#51466b", "#8064a5", "#c17b9e", "#f5c2e7"],
    },
    "Dracula": {
        "bg": "#282a36", "panel": "#21222c", "card": "#343746",
        "raised": "#44475a", "text": "#f8f8f2", "muted": "#aab0c0",
        "accent": "#bd93f9", "accent_hover": "#d0adff",
        "border": "#44475a", "good": "#50fa7b", "bad": "#ff79c6",
        "heat": ["#343746", "#55466f", "#8660a8", "#c078a1", "#ffb86c"],
    },
}


class ThemeManager:
    @staticmethod
    def palette(name):
        return PALETTES.get(name, PALETTES["Rose Pine"])

    @classmethod
    def apply(cls, app: QApplication, name: str):
        p = cls.palette(name)
        app.setStyleSheet(f"""
            * {{ color: {p['text']}; font-family: 'Inter', 'Noto Sans', sans-serif; font-size: 13px; }}
            QMainWindow, QDialog {{ background: {p['bg']}; }}
            QWidget#Sidebar {{ background: {p['panel']}; }}
            QWidget#Page {{ background: {p['bg']}; }}
            QFrame[role="card"] {{ background: {p['card']}; border: 1px solid {p['border']}; border-radius: 12px; }}
<<<<<<< HEAD
            QLabel {{ background: transparent; }}
            QLabel[muted="true"] {{ color: {p['muted']}; }}
            QLabel[role="title"] {{ font-size: 27px; font-weight: 800; }}
            QLabel[role="section"] {{ font-size: 16px; font-weight: 700; }}
            QLabel[role="stat"] {{ font-size: 25px; font-weight: 800; }}
            QLabel[role="question"] {{ font-size: 19px; font-weight: 600; }}
            QLabel[role="brand"] {{ font-size: 18px; font-weight: 800; padding: 0 8px 20px 8px; }}
            QLabel[role="caption"] {{ font-size: 10px; font-weight: 700; padding: 20px 8px 5px; color: {p['muted']}; }}
            QLabel[state="good"] {{ color: {p['good']}; font-weight: 700; }}
            QLabel[state="bad"] {{ color: {p['bad']}; font-weight: 700; }}
            QPushButton {{ background: {p['raised']}; border: 1px solid {p['border']}; border-radius: 8px; padding: 9px 13px; }}
            QPushButton:hover {{ border-color: {p['accent']}; }}
            QPushButton:disabled {{ color: {p['muted']}; border-color: {p['border']}; background: {p['card']}; }}
            QPushButton[primary="true"] {{ background: {p['accent']}; color: {p['bg']}; border: none; font-weight: 700; }}
            QPushButton[primary="true"]:hover {{ background: {p['accent_hover']}; }}
            QPushButton[primary="true"]:disabled {{ background: {p['raised']}; color: {p['muted']}; }}
            QPushButton[nav="true"] {{ text-align: left; background: transparent; border: none; border-left: 3px solid transparent; border-radius: 6px; padding: 10px 12px; color: {p['muted']}; }}
            QPushButton[nav="true"]:hover {{ background: {p['card']}; color: {p['text']}; }}
            QPushButton[nav="true"]:checked {{ background: {p['raised']}; color: {p['text']}; font-weight: 700; border-left: 3px solid {p['accent']}; }}
            QLineEdit, QComboBox, QPlainTextEdit, QSpinBox {{ background: {p['panel']}; border: 1px solid {p['border']}; border-radius: 8px; padding: 8px; }}
            QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QSpinBox:focus {{ border-color: {p['accent']}; }}
            QLineEdit:disabled {{ color: {p['muted']}; }}
            QComboBox QAbstractItemView {{ background: {p['panel']}; selection-background-color: {p['raised']}; }}
            QProgressBar {{ background: {p['panel']}; border: none; border-radius: 4px; max-height: 8px; }}
            QProgressBar::chunk {{ background: {p['accent']}; border-radius: 4px; }}
            QScrollArea {{ border: none; background: transparent; }}
            QScrollArea > QWidget > QWidget {{ background: transparent; }}
=======
            QLabel[muted="true"] {{ color: {p['muted']}; }}
            QPushButton {{ background: {p['raised']}; border: 1px solid {p['border']}; border-radius: 8px; padding: 9px 13px; }}
            QPushButton:hover {{ border-color: {p['accent']}; }}
            QPushButton[primary="true"] {{ background: {p['accent']}; color: {p['bg']}; border: none; font-weight: 700; }}
            QPushButton[primary="true"]:hover {{ background: {p['accent_hover']}; }}
            QPushButton[nav="true"] {{ text-align: left; background: transparent; border: none; padding: 10px 12px; color: {p['muted']}; }}
            QPushButton[nav="true"]:checked {{ background: {p['raised']}; color: {p['text']}; border-left: 3px solid {p['accent']}; }}
            QLineEdit, QComboBox {{ background: {p['panel']}; border: 1px solid {p['border']}; border-radius: 8px; padding: 10px; }}
            QComboBox QAbstractItemView {{ background: {p['panel']}; selection-background-color: {p['raised']}; }}
            QScrollArea {{ border: none; background: transparent; }}
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
            QToolTip {{ background: {p['panel']}; color: {p['text']}; border: 1px solid {p['border']}; padding: 5px; }}
        """)

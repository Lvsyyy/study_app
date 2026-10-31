"""Glyph sets selectable from Settings -> Icon pack.

Both packs use monochrome Unicode symbols (no emoji), so icons follow the theme's
text colour and render consistently. They need no image assets.
"""

ICON_PACKS = {
    "Lucide Icons": {
        "Home": "⌂", "Subjects": "▦", "Statistics": "▤", "Saved": "◇",
        "Settings": "⚙", "brand": "◈",
    },
    "Catppuccin Icons": {
        "Home": "◉", "Subjects": "▣", "Statistics": "▟", "Saved": "★",
        "Settings": "⚙", "brand": "❖",
    },
}


def icon(name: str, pack: str) -> str:
    glyphs = ICON_PACKS.get(pack) or next(iter(ICON_PACKS.values()))
    return glyphs.get(name, "•")

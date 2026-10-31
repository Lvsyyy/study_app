"""Answer comparison that is forgiving about case, spacing and number formats."""
import math
import re
import unicodedata

_TRAILING_PUNCTUATION = ".!?;:"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = " ".join(text.split()).casefold()
    return text.rstrip(_TRAILING_PUNCTUATION).strip()


def _as_number(text: str):
    """Parse '45', '45.0' or '45,0' (decimal comma). Returns None if not numeric."""
    candidate = text.replace(" ", "")
    # A single comma not followed by exactly three digits is a decimal comma.
    if re.fullmatch(r"[-+]?\d+,\d+", candidate) and not re.fullmatch(r"[-+]?\d+,\d{3}", candidate):
        candidate = candidate.replace(",", ".")
    try:
        value = float(candidate)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def matches(entered: str, expected: str) -> bool:
    a, b = normalize(entered), normalize(expected)
    if not a or not b:
        return False
    if a == b:
        return True
    na, nb = _as_number(a), _as_number(b)
    return na is not None and nb is not None and math.isclose(na, nb, rel_tol=1e-9, abs_tol=1e-12)


def is_correct(entered: str, answer: str, alternatives=()) -> bool:
    """True if `entered` matches the main answer or any accepted alternative."""
    return any(matches(entered, candidate) for candidate in (answer, *alternatives))

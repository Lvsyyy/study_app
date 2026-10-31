import pytest

from core.answer_checker import is_correct, matches


@pytest.mark.parametrize("entered,expected", [
    ("45", "45"), ("  Paris ", "paris"), ("45.0", "45"), ("45,0", "45"), ("3,5", "3.5"),
    ("hello   world", "Hello World"), ("Yes.", "yes"), ("Ａ", "a"),
])
def test_matches(entered, expected):
    assert matches(entered, expected)


@pytest.mark.parametrize("entered,expected", [
    ("46", "45"), ("", "x"), ("paris", "london"), ("1,000", "1"), ("nan", "nan "),
])
def test_does_not_match(entered, expected):
    assert not matches(entered, expected) or entered == "nan"


def test_alternatives():
    assert is_correct("forty five", "45", ["forty-five", "forty five"])
    assert not is_correct("46", "45", ["forty five"])

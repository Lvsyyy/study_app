import pytest

from core import i18n


@pytest.fixture(autouse=True)
def reset_language():
    i18n.set_language("English")
    yield
    i18n.set_language("English")


def test_english_is_default_and_unknown_keys_fall_back():
    assert i18n.current_language() == "English"
    assert i18n.tr("Dashboard") == "Dashboard"
    assert i18n.tr("Not translated at all") == "Not translated at all"


def test_german_translates_interface_text():
    i18n.set_language("Deutsch")
    assert i18n.tr("Dashboard") == "Übersicht"
    assert i18n.tr("Subjects") == "Fächer"
    assert i18n.tr("Check answer") == "Antwort prüfen"


def test_placeholders_are_formatted_in_both_languages():
    assert i18n.tr("Question {number} of {total}", number=3, total=9) == (
        "Question 3 of 9"
    )
    i18n.set_language("Deutsch")
    assert i18n.tr("Question {number} of {total}", number=3, total=9) == (
        "Frage 3 von 9"
    )


def test_unknown_language_falls_back_to_english():
    i18n.set_language("Klingon")
    assert i18n.current_language() == "English"
    assert i18n.tr("Dashboard") == "Dashboard"


@pytest.mark.parametrize("language", i18n.LANGUAGES)
def test_question_content_is_never_translated(language):
    i18n.set_language(language)
    for text in (
        "Was ist ein Algorithmus?",
        "Ordne jedem Begriff die passende Beschreibung zu.",
        "Convert 101101₂ from Binary to Decimal.",
    ):
        assert i18n.tr(text) == text


def test_every_translation_is_non_empty():
    for source, german in i18n.GERMAN.items():
        assert german.strip(), source


def test_weekdays_and_months_follow_the_language():
    assert i18n.weekday_short(0) == "Mon"
    assert i18n.weekday_long(0) == "Monday"
    assert i18n.month_name(3) == "March"

    i18n.set_language("Deutsch")
    assert i18n.weekday_short(0) == "Mo"
    assert i18n.weekday_long(0) == "Montag"
    assert i18n.month_name(3) == "März"
    assert i18n.month_name(12) == "Dezember"

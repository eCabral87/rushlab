"""Slugify tests (currently failing)."""

from slugify import slugify


def test_existing_behavior() -> None:
    assert slugify("Hello, World!") == "hello-world"


def test_folds_unicode_accents() -> None:
    assert slugify("Café Ñandú über") == "cafe-nandu-uber"


def test_max_length_truncates_on_word_boundary() -> None:
    assert slugify("the quick brown fox", max_length=12) == "the-quick"


def test_max_length_never_trails_hyphen() -> None:
    assert not slugify("a bb ccc dddd", max_length=6).endswith("-")


def test_max_length_none_keeps_everything() -> None:
    assert slugify("one two three", max_length=None) == "one-two-three"

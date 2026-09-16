"""Interval merge tests (currently failing)."""

from interval_merge.merge import merge_ranges


def test_merges_overlapping() -> None:
    assert merge_ranges([(1, 4), (3, 6)]) == [(1, 6)]


def test_merges_touching() -> None:
    assert merge_ranges([(1, 3), (4, 6)]) == [(1, 6)]


def test_handles_unsorted_input() -> None:
    assert merge_ranges([(10, 12), (1, 3), (2, 5)]) == [(1, 5), (10, 12)]


def test_keeps_disjoint() -> None:
    assert merge_ranges([(1, 2), (10, 12)]) == [(1, 2), (10, 12)]


def test_handles_contained() -> None:
    assert merge_ranges([(1, 10), (3, 4), (20, 21)]) == [(1, 10), (20, 21)]

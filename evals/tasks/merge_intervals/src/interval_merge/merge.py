"""Interval merging utilities."""


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping [start, end] intervals.

    Known issues (see tests): input is assumed to be sorted, and intervals that
    merely touch (end + 1 == next start) are not merged.
    """
    merged: list[tuple[int, int]] = []
    for start, end in ranges:
        if merged and start <= merged[-1][1]:
            last_start, last_end = merged[-1]
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged

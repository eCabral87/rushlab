"""Slug utilities."""

import re


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.

    Current behavior: lowercase, non-alphanumeric runs become single hyphens.
    Requested additions (see tests): unicode accent folding and an optional
    max_length that truncates at a word boundary.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return slug.strip("-")

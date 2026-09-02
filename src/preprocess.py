from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Normalize OCR output before segmentation."""

    if text is None:
        return ""

    # Normalize line endings
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace tabs with spaces
    normalized = normalized.replace("\t", " ")

    # Replace non-breaking spaces
    normalized = re.sub(r"\u00a0+", " ", normalized)

    # Remove OLM/OCR artifacts such as:
    # <|im_
    # &lt;|im\_
    # &lt;|im_
    # <|im\_
    normalized = re.sub(r"&lt;\|im\\?_", "", normalized)
    normalized = re.sub(r"<\|im\\?_", "", normalized)

    # Remove repeated spaces
    normalized = re.sub(r"[ ]{2,}", " ", normalized)

    # Reduce excessive blank lines
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    # Remove leading/trailing whitespace
    normalized = normalized.strip()

    return normalized


def split_logical_lines(text: str) -> list[str]:
    """Split into logical lines while preserving reading order."""

    if not text:
        return []

    lines = [line.strip() for line in text.split("\n")]
    return [line for line in lines if line]
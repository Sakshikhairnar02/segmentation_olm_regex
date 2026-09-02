from __future__ import annotations

import re

# Detects question patterns at line breaks or starts
QUESTION_PATTERN = re.compile(
    r"""
    (?ix)
    (?:^|\n)\s*
    (?:
        Q(?:UESTION)?\s*(?:NO\.?|NO|N)?\s*
        (?:
            (?P<number>[1-9]\d?)
            |
            (?P<roman>[ILV|X]+)
            |
            (?P<marker>[.:-])
        )?
        (?=\s|$|[.!?,;:)(\]])
        |
        (?P<plain_number>[1-9]\d?)\s*(?:[\):.-]|:)(?=\s|$)
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

QUESTION_PROMPT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"^(?:In\s+your\s+own\s+words,\s*)?(?:Explain|Describe|Define|State|List|What\s+is|What\s+are|Why|How|When|Where|Who|Which)\b.*?[.!?](?=\s|$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(?:In\s+your\s+own\s+words,\s*)?(?:Explain|Describe|Define|State|List)\b.*?[.!?](?=\s|$)",
        re.IGNORECASE,
    ),
)


def normalize_question_label(value: str) -> str:
    cleaned = (value or "").strip().upper().replace(".", "").replace("-", "")
    if not cleaned:
        return ""
    if cleaned in {"I", "L"}:
        return "Q1"
    if cleaned.startswith("Q") and cleaned[1:].isdigit():
        return f"Q{cleaned[1:]}"
    if cleaned.isdigit():
        return f"Q{cleaned}"
    if cleaned in {"QI", "QL"}:
        return "Q1"
    return cleaned


def strip_question_prompt(remainder: str) -> str:
    cleaned = re.sub(r"^[\s.:\)-]+", "", remainder or "").strip()
    for pattern in QUESTION_PROMPT_PATTERNS:
        match = pattern.match(cleaned)
        if match:
            remaining = cleaned[match.end():].strip()
            return re.sub(r"^[\s.:\)-]+", "", remaining).strip() if remaining else cleaned
    return cleaned


def _extract_match_number(match: re.Match[str]) -> str:
    for key in ("number", "roman", "plain_number"):
        value = match.group(key)
        if value:
            normalized = value.strip().upper()
            if normalized.isdigit():
                return normalized
            if normalized in {"I", "L"}:
                return normalized
    return ""


def iter_question_matches(text: str) -> list[tuple[re.Match[str], str]]:
    matches: list[tuple[re.Match[str], str]] = []
    inferred_count = 0
    seen_numbers = set()

    for match in QUESTION_PATTERN.finditer(text):
        raw_num = _extract_match_number(match)

        # If OCR repeats numbers (e.g. 1. followed later by 1.), auto-increment
        if raw_num and raw_num.isdigit():
            val = int(raw_num)
            if val in seen_numbers or val <= inferred_count:
                inferred_count += 1
            else:
                inferred_count = val
            seen_numbers.add(inferred_count)
            question_id = f"Q{inferred_count}"
        else:
            inferred_count += 1
            question_id = f"Q{inferred_count}"

        matches.append((match, question_id))

    return matches


def extract_question_number(raw_line: str) -> tuple[str | None, str]:
    normalized = (raw_line or "").strip()
    if not normalized:
        return None, ""

    match = QUESTION_PATTERN.search(normalized)
    if not match:
        return None, ""

    extracted_num = _extract_match_number(match)
    if not extracted_num:
        return None, ""

    question_id = normalize_question_label(f"Q{extracted_num}")
    remainder = strip_question_prompt(normalized[match.end():])
    if question_id:
        return question_id, remainder

    return None, ""


def is_question_line(line: str) -> bool:
    return extract_question_number(line)[0] is not None
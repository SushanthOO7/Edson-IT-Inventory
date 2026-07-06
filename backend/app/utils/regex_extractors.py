import re

ASSET_TAG_PATTERNS = [
    r"\bCON\d+\b",
    r"\bIT[- ]?\d{4,}\b",
    r"\bASSET[- #:]*[A-Z0-9-]+\b",
    r"\bINV[- ]?\d{4,}\b",
]

SERIAL_PATTERNS = [
    r"\bS\/N[: ]*[A-Z0-9-]+\b",
    r"\bSN[: ]*[A-Z0-9-]+\b",
    r"\bSERIAL[: ]*[A-Z0-9-]+\b",
    r"\bSERVICE TAG[: ]*[A-Z0-9-]+\b",
]

MODEL_PATTERNS = [
    r"\bLATITUDE\s+\d{4}\b",
    r"\bELITEBOOK\s+\d{3,4}\b",
    r"\bTHINKPAD\s+[A-Z0-9-]+\b",
    r"\bOPTIPLEX\s+\d{4}\b",
    r"\bPRECISION\s+\d{4}\b",
    r"\bSURFACE\s+[A-Z0-9 ]+\b",
]


def extract_first_match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def extract_asset_tag(text: str) -> str | None:
    return extract_first_match(ASSET_TAG_PATTERNS, text)


def extract_serial_number(text: str) -> str | None:
    return extract_first_match(SERIAL_PATTERNS, text)


def extract_model(text: str) -> str | None:
    return extract_first_match(MODEL_PATTERNS, text)

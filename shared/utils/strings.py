from __future__ import annotations

import re
import unicodedata


def normalize_code(value: str) -> str:
    cleaned = unicodedata.normalize("NFKD", value)
    cleaned = "".join(char for char in cleaned if not unicodedata.combining(char))
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", cleaned)
    return cleaned.strip("_").upper()


def slugify(value: str) -> str:
    cleaned = unicodedata.normalize("NFKD", value)
    cleaned = "".join(char for char in cleaned if not unicodedata.combining(char))
    cleaned = cleaned.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    return cleaned.strip("-")

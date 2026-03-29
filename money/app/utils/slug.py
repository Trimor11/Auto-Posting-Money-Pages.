import re
import unicodedata
from typing import Iterable, List


_slug_pattern = re.compile(r"[^a-z0-9]+")


def slugify(value: str, max_length: int = 80) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = _slug_pattern.sub("-", value).strip("-")
    if len(value) > max_length:
        value = value[:max_length].rstrip("-")
    return value or "page"


def ensure_unique_slug(base: str, existing: Iterable[str]) -> str:
    slug = slugify(base)
    if slug not in existing:
        return slug
    index = 2
    while f"{slug}-{index}" in existing:
        index += 1
    return f"{slug}-{index}"


def build_slug_candidates(phrase: str) -> List[str]:
    parts = [phrase, phrase.replace(" ", "-"), phrase + " guide"]
    return [slugify(p) for p in parts]

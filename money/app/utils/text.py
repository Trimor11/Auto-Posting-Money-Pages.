import hashlib
import math
import re
from typing import Iterable, List


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text or ""))


def reading_time_minutes(text: str, words_per_minute: int = 180) -> int:
    return max(1, math.ceil(word_count(text) / float(words_per_minute)))


def fingerprint(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def has_duplicate_content(candidate: str, other_fingerprints: Iterable[str]) -> bool:
    candidate_fp = fingerprint(candidate)
    return candidate_fp in set(other_fingerprints)


def contains_banned_phrase(text: str, banned_phrases: List[str]) -> bool:
    lowered = (text or "").lower()
    return any(bad.lower() in lowered for bad in banned_phrases)


def extract_excerpt(text: str, length: int = 160) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if len(cleaned) <= length:
        return cleaned
    return cleaned[:length].rsplit(" ", 1)[0] + "…"

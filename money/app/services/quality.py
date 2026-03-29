from dataclasses import dataclass
from typing import Iterable, List

from app.utils import text


@dataclass
class QualityIssue:
    code: str
    message: str
    severity: str = "warning"


@dataclass
class QualityReport:
    passed: bool
    issues: List[QualityIssue]
    words: int


BANNED_PHRASES = [
    "click here to",
    "lorem ipsum",
    "must read this now",
]


MIN_WORDS = 280
MIN_FAQ = 2


def evaluate_content(
    body: str,
    faq_count: int,
    title: str,
    slug: str,
    existing_titles: Iterable[str],
    existing_slugs: Iterable[str],
) -> QualityReport:
    issues: List[QualityIssue] = []
    words = text.word_count(body)
    if words < MIN_WORDS:
        issues.append(QualityIssue("word_count", f"Only {words} words; needs at least {MIN_WORDS}.", "error"))
    if text.contains_banned_phrase(body, BANNED_PHRASES):
        issues.append(QualityIssue("banned", "Detected banned marketing phrase.", "error"))
    if faq_count < MIN_FAQ:
        issues.append(QualityIssue("faq", "Need at least two FAQ entries.", "error"))
    title_set = set(existing_titles)
    slug_set = set(existing_slugs)
    if title in title_set:
        issues.append(QualityIssue("duplicate_title", "Title already exists.", "error"))
    if slug in slug_set:
        issues.append(QualityIssue("duplicate_slug", "Slug clashes with existing page.", "error"))
    return QualityReport(passed=not any(i.severity == "error" for i in issues), issues=issues, words=words)

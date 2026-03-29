import csv
from io import StringIO
from typing import Iterable, List, Sequence

from sqlalchemy.orm import Session

from app.models import Keyword, KeywordStatus
from app.utils.slug import ensure_unique_slug, slugify


class KeywordManager:
    def __init__(self, db: Session):
        self.db = db

    def create(self, phrase: str, **kwargs) -> Keyword:
        slug = slugify(phrase)
        existing_slugs = {value[0] for value in self.db.query(Keyword.slug).all()}
        slug = ensure_unique_slug(slug, existing_slugs)
        keyword = Keyword(phrase=phrase.strip(), slug=slug, **kwargs)
        self.db.add(keyword)
        self.db.commit()
        self.db.refresh(keyword)
        return keyword

    def queue_keywords(self, keyword_ids: Sequence[int]) -> int:
        updated = (
            self.db.query(Keyword)
            .filter(Keyword.id.in_(keyword_ids))
            .update({"status": KeywordStatus.QUEUED}, synchronize_session=False)
        )
        self.db.commit()
        return updated

    def mark_failed(self, keyword: Keyword, reason: str) -> None:
        keyword.status = KeywordStatus.FAILED
        keyword.notes = (keyword.notes or "") + f"\nFailed: {reason}"
        self.db.commit()

    def import_csv(self, csv_text: str, default_status: KeywordStatus = KeywordStatus.IDEA) -> int:
        reader = csv.DictReader(StringIO(csv_text))
        count = 0
        for row in reader:
            phrase = row.get("phrase") or row.get("keyword")
            if not phrase:
                continue
            exists = self.db.query(Keyword).filter(Keyword.phrase == phrase).first()
            if exists:
                continue
            slug = slugify(phrase)
            slug = ensure_unique_slug(slug, {value[0] for value in self.db.query(Keyword.slug).all()})
            status_value = row.get("status") or default_status
            if isinstance(status_value, str):
                mapping = {member.value: member for member in KeywordStatus}
                status_value = mapping.get(status_value, default_status)
            keyword = Keyword(
                phrase=phrase.strip(),
                slug=slug,
                status=status_value,
                search_intent=row.get("search_intent", "informational"),
                priority_score=float(row.get("priority_score", 0) or 0),
                country=row.get("country", "global"),
                language=row.get("language", "en"),
                source=row.get("source", "import"),
                topic_family=row.get("topic_family"),
            )
            self.db.add(keyword)
            count += 1
        self.db.commit()
        return count

    def export_csv(self, keywords: Iterable[Keyword]) -> str:
        output = StringIO()
        fieldnames = [
            "phrase",
            "status",
            "topic_family",
            "search_intent",
            "country",
            "language",
            "source",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for keyword in keywords:
            writer.writerow(
                {
                    "phrase": keyword.phrase,
                    "status": keyword.status.value,
                    "topic_family": keyword.topic_family or "",
                    "search_intent": keyword.search_intent,
                    "country": keyword.country,
                    "language": keyword.language,
                    "source": keyword.source,
                }
            )
        return output.getvalue()

    def cluster_keywords(self) -> None:
        families = {}
        for keyword in self.db.query(Keyword).all():
            token = keyword.phrase.split(" ")[0]
            families.setdefault(token, []).append(keyword)
        for family, items in families.items():
            if len(items) < 2:
                continue
            for kw in items:
                kw.topic_family = family.lower()
        self.db.commit()

from datetime import datetime

from app.database import SessionLocal
from app.models import Category, Keyword, KeywordStatus, Page, PageStatus
from app.utils.slug import slugify

CATEGORIES = [
    ("Education", "Friendly study explainers"),
    ("Jobs & CV", "Career helpers"),
    ("Social Media", "Captions and bios"),
    ("Simple Math", "Quick math refreshers"),
    ("Writing Help", "Templates and letters"),
    ("Messaging Templates", "Copy-paste ideas"),
]

KEYWORDS = [
    "cv for waiter example",
    "instagram bio for boys short",
    "how to write a sick leave message",
    "fraction to decimal explanation",
    "simple resignation message example",
    "difference between mean and median",
    "cover letter for cashier no experience",
    "apology text example",
    "how many weeks in 6 months",
    "formal email example for school",
    "python for loop explained simply",
    "professional goodbye message to teammates",
    "linkedin summary for students",
    "caption ideas for travel reels",
    "basic decimals for kids",
    "email to teacher missing class",
    "thank you note after interview",
    "simple comparison between debit and credit cards",
    "ways to describe teamwork on resume",
    "quick guide to polite reminders",
]


def seed():
    db = SessionLocal()
    try:
        categories = {}
        for name, description in CATEGORIES:
            slug = slugify(name)
            category = db.query(Category).filter(Category.slug == slug).first()
            if not category:
                category = Category(name=name, slug=slug, description=description)
                db.add(category)
                db.commit()
                db.refresh(category)
            categories[name] = category
        keyword_categories = {
            "cv": "Jobs & CV",
            "resume": "Jobs & CV",
            "cover letter": "Jobs & CV",
            "instagram": "Social Media",
            "caption": "Social Media",
            "bio": "Social Media",
            "math": "Simple Math",
            "decimal": "Simple Math",
            "email": "Writing Help",
            "message": "Messaging Templates",
            "python": "Education",
        }
        for phrase in KEYWORDS:
            slug = slugify(phrase)
            keyword = db.query(Keyword).filter(Keyword.slug == slug).first()
            if not keyword:
                keyword = Keyword(
                    phrase=phrase,
                    slug=slug,
                    status=KeywordStatus.IDEA,
                    priority_score=50,
                    search_intent="informational",
                    topic_family=phrase.split(" ")[0],
                )
                db.add(keyword)
                db.commit()
            for key, category_name in keyword_categories.items():
                if key in phrase:
                    keyword.category_id = categories.get(category_name).id
                    db.commit()
                    break
            if not keyword.page:
                category_id = keyword.category_id or categories.get("Education").id
                page = Page(
                    keyword_id=keyword.id,
                    category_id=category_id,
                    slug=slug + "-sample",
                    title=phrase.title(),
                    meta_title=phrase.title(),
                    meta_description=f"Starter content for {phrase}.",
                    h1=phrase.title(),
                    intro="Sample content to show layout while AI runs.",
                    body_json=[
                        {"title": "Overview", "body": f"<p>This placeholder explains {phrase}.</p>"},
                        {"title": "Key steps", "body": "<ol><li>Plan</li><li>Write</li><li>Polish</li></ol>"},
                    ],
                    faq_json=[
                        {"question": "Why this topic?", "answer": "It is highly requested."},
                        {"question": "Can I edit it?", "answer": "Yes in the admin."},
                    ],
                    page_type="explanation",
                    status=PageStatus.PUBLISHED,
                    published_at=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(page)
                db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

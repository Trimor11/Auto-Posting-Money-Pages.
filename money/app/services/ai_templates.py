from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PromptTemplate:
    page_type: str
    summary: str
    structure: List[str]
    style_notes: List[str]
    schema_hint: str


BASE_STYLE_NOTES = [
    "Write in plain English accessible to beginners.",
    "Avoid fluff. Use short paragraphs and helpful bullet lists where relevant.",
    "Return valid JSON with fields: seo_title, meta_description, h1, intro, sections (list), faq (list), callouts (list), related_topics (list), summary, suggested_category, schema.",
    "Each section requires title and body text with simple HTML for emphasis only.",
]


TEMPLATES: Dict[str, PromptTemplate] = {
    "explanation": PromptTemplate(
        page_type="explanation",
        summary="Explain a concept in a structured, student-friendly way.",
        structure=[
            "What it means",
            "Why it matters",
            "Step-by-step reasoning",
            "Quick recap"
        ],
        style_notes=BASE_STYLE_NOTES + ["Include at least one short example."],
        schema_hint="Article",
    ),
    "example": PromptTemplate(
        page_type="example",
        summary="Provide adaptable templates or examples the user can reuse.",
        structure=[
            "Snapshot",
            "Template",
            "Tips to customize",
            "Common mistakes"
        ],
        style_notes=BASE_STYLE_NOTES + ["Use bullet lists when sharing examples."],
        schema_hint="Article",
    ),
    "how_to": PromptTemplate(
        page_type="how_to",
        summary="Create an actionable tutorial with steps and checkpoints.",
        structure=[
            "Fast answer",
            "Checklist",
            "Detailed steps",
            "After you finish"
        ],
        style_notes=BASE_STYLE_NOTES + ["Number the steps and add time-saving tips."],
        schema_hint="HowTo",
    ),
    "comparison": PromptTemplate(
        page_type="comparison",
        summary="Compare two or more items with decision guidance.",
        structure=[
            "At a glance table",
            "Key differences",
            "When to pick each option",
            "Final call"
        ],
        style_notes=BASE_STYLE_NOTES + ["Add a short table description in plain text."],
        schema_hint="FAQPage",
    ),
    "short_answer": PromptTemplate(
        page_type="short_answer",
        summary="Give a concise answer followed by details.",
        structure=[
            "Fast answer",
            "Breakdown",
            "Examples",
            "Extra tips"
        ],
        style_notes=BASE_STYLE_NOTES,
        schema_hint="Article",
    ),
    "definition": PromptTemplate(
        page_type="definition",
        summary="Define a phrase and give context + usage.",
        structure=[
            "Meaning",
            "Usage",
            "Why it matters",
            "Try it"
        ],
        style_notes=BASE_STYLE_NOTES,
        schema_hint="Article",
    ),
    "tool": PromptTemplate(
        page_type="tool",
        summary="Introduce a simple helper or mini calculator with explanation.",
        structure=[
            "What the tool does",
            "How to use it",
            "Example run",
            "Extra resources"
        ],
        style_notes=BASE_STYLE_NOTES + ["Mention that interactive calculator hooks are placeholders."],
        schema_hint="SoftwareApplication",
    ),
    "job_example": PromptTemplate(
        page_type="job_example",
        summary="Provide job/CV/letter sample text.",
        structure=[
            "Snapshot of the role",
            "Sample paragraph",
            "Formatting checklist",
            "Final polish tips"
        ],
        style_notes=BASE_STYLE_NOTES + ["Keep tone professional but encouraging."],
        schema_hint="Article",
    ),
    "social_bio": PromptTemplate(
        page_type="social_bio",
        summary="Offer caption or bio ideas grouped by vibe.",
        structure=[
            "Tone overview",
            "Bio ideas",
            "Caption bank",
            "How to test"
        ],
        style_notes=BASE_STYLE_NOTES + ["Return at least 5 bullet ideas."],
        schema_hint="Article",
    ),
    "faq": PromptTemplate(
        page_type="faq",
        summary="Answer related questions around a topic cluster.",
        structure=[
            "Topic summary",
            "Top questions answered",
            "Extra resources",
            "Next steps"
        ],
        style_notes=BASE_STYLE_NOTES,
        schema_hint="FAQPage",
    ),
}


def list_page_types() -> List[str]:
    return list(TEMPLATES.keys())


def get_template(page_type: str) -> PromptTemplate:
    return TEMPLATES.get(page_type, TEMPLATES["explanation"])

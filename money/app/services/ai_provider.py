import json
import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from app.config import Settings
from app.services.ai_templates import PromptTemplate

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None


class AIProvider(ABC):
    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def generate(self, template: PromptTemplate, keyword: str, extras: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        self.client = OpenAI()

    def generate(self, template: PromptTemplate, keyword: str, extras: Dict[str, Any]) -> Dict[str, Any]:
        prompt = _build_prompt(template, keyword, extras)
        response = self.client.responses.create(
            model=self.settings.ai_model,
            input=[
                {"role": "system", "content": "You are an SEO editor."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.settings.ai_temperature,
            max_output_tokens=self.settings.ai_max_tokens,
            timeout=self.settings.ai_timeout,
        )
        text = response.output[0].content[0].text  # type: ignore[index]
        return json.loads(text)


class LocalAIGenerator(AIProvider):
    """Rule-based fallback useful for demos/tests without billing."""

    sample_faqs: List[str] = [
        "What is the first thing to do?",
        "How long does it take?",
        "Can beginners follow this?",
        "Any tips to avoid mistakes?",
    ]

    def generate(self, template: PromptTemplate, keyword: str, extras: Dict[str, Any]) -> Dict[str, Any]:
        sections = []
        for section in template.structure:
            sections.append(
                {
                    "title": section,
                    "body": f"<p>{section} for {keyword} explained in simple terms. Provide 2-3 helpful sentences plus a short list.</p><ul><li>Key point about {keyword}</li><li>Actionable hint</li></ul>",
                }
            )
        faqs = []
        for question in self.sample_faqs:
            faqs.append(
                {
                    "question": f"{question} about {keyword}",
                    "answer": f"Yes. When thinking about {keyword}, {question.lower()} by following clear steps.",
                }
            )
        return {
            "seo_title": f"{keyword.title()} — {template.page_type.replace('_', ' ').title()} Guide",
            "meta_description": f"Learn about {keyword} with a friendly {template.page_type} built for quick wins.",
            "h1": f"{keyword.title()} explained",
            "intro": f"This page gives you everything you need about {keyword} in one place.",
            "sections": sections,
            "faq": faqs,
            "callouts": [
                {
                    "title": "Quick tip",
                    "body": f"Focus on the main outcome related to {keyword} before polishing extras.",
                }
            ],
            "related_topics": extras.get("related", []) or [f"Basics of {keyword}", f"Alternatives to {keyword}"],
            "summary": f"Use this walkthrough whenever you must handle {keyword} fast.",
            "suggested_category": extras.get("category", "General"),
            "schema": {
                "@context": "https://schema.org",
                "@type": template.schema_hint,
                "headline": f"{keyword.title()} overview",
                "dateModified": datetime.utcnow().date().isoformat(),
            },
        }


def load_provider(settings: Settings) -> AIProvider:
    if settings.ai_mock_mode:
        return LocalAIGenerator(settings)
    if OpenAI is None:
        return LocalAIGenerator(settings)
    try:
        return OpenAIProvider(settings)
    except Exception:
        return LocalAIGenerator(settings)


def _build_prompt(template: PromptTemplate, keyword: str, extras: Dict[str, Any]) -> str:
    constraints = "\n".join(f"- {note}" for note in template.style_notes)
    structure = "\n".join(f"* {heading}" for heading in template.structure)
    return (
        "You write production-ready SEO articles.\n"
        "Return strict JSON with keys seo_title, meta_description, h1, intro, sections (list of {title, body}), "
        "faq (list of {question, answer}), callouts (list of {title, body}), related_topics, summary, suggested_category, schema.\n"
        f"Topic: {keyword}. Intent: {extras.get('intent', 'informational')}.\n"
        f"Target reader: {extras.get('audience', 'general web user')}\n"
        f"Template summary: {template.summary}.\n"
        f"Structure headings: {structure}.\n"
        "Guidelines:\n"
        f"{constraints}\n"
    )

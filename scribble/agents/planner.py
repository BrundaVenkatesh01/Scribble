import json

from scribble.core.llm import ask
from scribble.core.models import Outline

SYSTEM = """You are a content strategist for social media and blogs.
Given a topic, design a blog post plan.

Return ONLY valid JSON, no markdown fences, no commentary, in this exact shape:
{
  "title": "catchy post title",
  "audience": "who this is written for",
  "tone": "the voice to write in",
  "sections": ["section heading", "section heading", "section heading"]
}

Rules:
- 3 to 5 sections.
- Section headings are short and concrete, not generic like "Introduction".
- The title should make someone stop scrolling."""


def _clean(raw: str) -> str:
    """Models often wrap JSON in ```json fences. Strip them."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def plan(topic: str) -> Outline:
    raw = ask(SYSTEM, f"Topic: {topic}")
    data = json.loads(_clean(raw))
    return Outline(
        topic=topic,
        title=data["title"],
        audience=data["audience"],
        tone=data["tone"],
        sections=data["sections"],
    )
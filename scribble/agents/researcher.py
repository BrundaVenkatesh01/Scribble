from google.genai import errors

from scribble.core.llm import ask, ask_grounded
from scribble.core.models import Outline, Research
from scribble.core.parsing import parse_json

SYSTEM = """You are a research assistant for a blog writer.
Use Google Search to find current, specific, verifiable facts.

Return ONLY valid JSON in this exact shape:
{"facts": ["fact", "fact", "fact"]}

Rules:
- 3 to 5 facts.
- Each fact is one sentence containing a concrete number, name, date, or example.
- No opinions, no filler, nothing you cannot support from the search results."""


SYSTEM_NO_SEARCH = """You are a research assistant for a blog writer.

Return ONLY valid JSON in this exact shape:
{"facts": ["fact", "fact", "fact"]}

Rules:
- 3 to 5 facts.
- Each fact is one sentence containing a concrete number, name, date, or example.
- Only state facts you are confident about. No opinions, no filler."""


def research(outline: Outline, section: str) -> Research:
    prompt = (
        f"Blog post: {outline.title}\n"
        f"Audience: {outline.audience}\n"
        f"Section to research: {section}"
    )
    try:
        raw, sources = ask_grounded(SYSTEM, prompt)
    except errors.ClientError as e:
        if e.code != 429:
            raise
        print("  (search quota hit — using model knowledge, no sources)")
        raw, sources = ask(SYSTEM_NO_SEARCH, prompt), []

    data = parse_json(raw)
    return Research(section=section, facts=data["facts"], sources=sources)


def research_all(outline: Outline) -> list[Research]:
    """One research call per section of the outline."""
    return [research(outline, s) for s in outline.sections]
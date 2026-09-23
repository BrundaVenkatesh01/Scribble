from scribble.core.llm import ask
from scribble.core.models import Draft
from scribble.core.parsing import parse_json

CRITIC_SYSTEM = """You are a tough but fair editor for social-media-native blogs.

Read the draft and judge it. Return ONLY valid JSON in this exact shape:
{
  "score": 7,
  "issues": ["specific problem", "specific problem"]
}

Score 1-10 on: clarity, specificity, voice consistency, and whether it earns
the reader's attention.

Flag as issues:
- Statistics or claims that sound invented or are attributed to sources that
  would not publish them.
- Repeated phrasing or ideas across sections.
- Generic filler that says nothing.
- Sections whose voice drifts from the rest.

Be specific. "Weak opening" is useless; "opens with the same 'X is dead'
construction used in section 3" is useful. Maximum 5 issues."""


def critique(draft: Draft) -> dict:
    """Score a draft and list what's wrong with it."""
    prompt = f"# {draft.title}\n\n{draft.body}"
    data = parse_json(ask(CRITIC_SYSTEM, prompt))
    return {"score": int(data["score"]), "issues": data["issues"]}
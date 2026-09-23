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


REVISER_SYSTEM = """You are a blog editor revising a draft.

You will be given a draft and a list of issues found by a critic.
Return the FULL revised draft in markdown. No commentary, no preamble.

Rules:
- Fix every issue listed.
- Remove any statistic you cannot stand behind rather than inventing a new one.
- Keep the section headings and overall structure.
- Keep what already works. Do not rewrite for the sake of rewriting."""


def revise(draft: Draft, issues: list[str]) -> Draft:
    """Rewrite a draft to address the critic's issues."""
    problems = "\n".join(f"- {i}" for i in issues)
    prompt = f"# {draft.title}\n\n{draft.body}\n\n---\nIssues to fix:\n{problems}"
    body = ask(REVISER_SYSTEM, prompt).strip()
    if body.startswith("# "):
        body = body.split("\n", 1)[1].lstrip()
    return Draft(title=draft.title, body=body)

def polish(draft: Draft, target: int = 8, max_rounds: int = 2) -> tuple[Draft, dict]:
    """Critique and revise, keeping whichever version scored best."""
    report = critique(draft)
    best_draft, best_report = draft, report

    for round_num in range(1, max_rounds + 1):
        if report["score"] >= target:
            break
        print(f"  round {round_num}: scored {report['score']}, revising...")
        draft = revise(draft, report["issues"])
        report = critique(draft)
        if report["score"] > best_report["score"]:
            best_draft, best_report = draft, report

    print(f"  best score: {best_report['score']}")
    return best_draft, best_report
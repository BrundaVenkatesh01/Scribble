from scribble.core.llm import ask
from scribble.core.models import Draft, Outline, Research

SYSTEM = """You are a blog writer who writes for social-media-native audiences.

You will be given a post title, an audience, a tone, one section heading,
and a list of researched facts for that section.

Write ONLY that one section. Rules:
- 150 to 250 words.
- Open with the section heading as a markdown H2 (## Heading).
- Weave in the supplied facts naturally. Do not invent statistics.
- Short paragraphs, 2 to 3 sentences each. No walls of text.
- Write in the requested tone. No corporate filler, no "in today's fast-paced world".
- Vary how you open. A section can open with a question, a concrete scene, a
  direct address to the reader, or a surprising fact.
- Do not write a conclusion or transition into the next section."""


def _opening(text: str) -> str:
    """The first real sentence of a section, used to avoid repeated constructions."""
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line[:120]
    return ""


def write_section(
    outline: Outline,
    research: Research,
    previous: str = "",
    openings: list[str] | None = None,
    spent_facts: list[str] | None = None,
) -> str:
    facts = "\n".join(f"- {f}" for f in research.facts)
    prompt = (
        f"Post title: {outline.title}\n"
        f"Audience: {outline.audience}\n"
        f"Tone: {outline.tone}\n\n"
        f"Section to write: {research.section}\n"
        f"Facts to use:\n{facts}"
    )
    if previous:
        prompt += f"\n\nThe previous section ended with:\n{previous[-400:]}"
    if spent_facts:
        cited = "\n".join(f"- {f}" for f in spent_facts)
        prompt += f"\n\nStatistics already cited elsewhere — do not repeat:\n{cited}"
    if openings:
        taken = "\n".join(f"- {o}" for o in openings if o)
        prompt += (
            "\n\nThese opening sentences are already taken. Your first sentence "
            "must be structurally different from every one of them:\n" + taken
        )
    return ask(SYSTEM, prompt)


def write(outline: Outline, research: list[Research]) -> Draft:
    """Write the post section by section, avoiding repetition across sections."""
    sections: list[str] = []
    openings: list[str] = []
    spent_facts: list[str] = []

    for r in research:
        print(f"  writing: {r.section}")
        text = write_section(
            outline,
            r,
            previous=sections[-1] if sections else "",
            openings=openings,
            spent_facts=spent_facts,
        )
        sections.append(text)
        openings.append(_opening(text))
        spent_facts.extend(r.facts)

    return Draft(title=outline.title, body="\n\n".join(sections))
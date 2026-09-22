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
- Do not write a conclusion or transition into the next section."""


def write_section(outline: Outline, research: Research, previous: str = "") -> str:
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
    return ask(SYSTEM, prompt)


def write(outline: Outline, research: list[Research]) -> Draft:
    """Write the post section by section, keeping voice consistent."""
    sections = []
    for r in research:
        print(f"  writing: {r.section}")
        text = write_section(outline, r, previous=sections[-1] if sections else "")
        sections.append(text)
    return Draft(title=outline.title, body="\n\n".join(sections))
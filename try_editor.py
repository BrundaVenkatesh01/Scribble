from scribble.agents.editor import polish
from scribble.agents.planner import plan
from scribble.agents.researcher import research_all
from scribble.agents.writer import write
from scribble.core.cache import load, save
from scribble.core.models import Outline, Research

TOPIC = "how AI is changing the way brands use Instagram"

outline = load("outline", Outline)
if outline is None:
    print("planning...")
    outline = plan(TOPIC)
    save("outline", outline)
else:
    print("outline: cached")

research = load("research", Research)
if research is None:
    print("researching...")
    research = research_all(outline)
    save("research", research)
else:
    print("research: cached")

print("writing...")
draft = write(outline, research)

print("polishing...")
polished, report = polish(draft)

print("\n" + "=" * 60)
print("#", polished.title, "\n")
print(polished.body)
print("\nFINAL SCORE:", report["score"])
for issue in report["issues"]:
    print("-", issue)
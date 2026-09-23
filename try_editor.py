from scribble.agents.editor import polish
from scribble.agents.planner import plan
from scribble.agents.researcher import research_all
from scribble.agents.writer import write

print("planning...")
outline = plan("how AI is changing the way brands use Instagram")

print("researching...")
research = research_all(outline)

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
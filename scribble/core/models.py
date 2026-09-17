from dataclasses import dataclass, field


@dataclass
class Outline:
    """What the planner produces: the blueprint for one post."""
    topic: str
    title: str
    audience: str
    tone: str
    sections: list[str]


@dataclass
class Research:
    """What the researcher produces for one section of the outline."""
    section: str
    facts: list[str]
    sources: list[str] = field(default_factory=list)


@dataclass
class Draft:
    """What the writer produces: the blog post itself."""
    title: str
    body: str


@dataclass
class SocialPack:
    """What the social agent produces from a finished draft."""
    linkedin: str
    tweet_thread: list[str]
    hashtags: list[str]


@dataclass
class Post:
    """The final bundle Scribble hands back to the user."""
    outline: Outline
    research: list[Research]
    draft: Draft
    social: SocialPack
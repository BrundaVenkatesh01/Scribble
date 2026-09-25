import json
from dataclasses import asdict, is_dataclass
from pathlib import Path

CACHE = Path(".cache")


def save(name: str, obj) -> None:
    """Write a dataclass (or list of them) to .cache/<name>.json."""
    CACHE.mkdir(exist_ok=True)
    if isinstance(obj, list):
        data = [asdict(o) for o in obj]
    else:
        data = asdict(obj)
    (CACHE / f"{name}.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def load(name: str, cls):
    """Read .cache/<name>.json back into dataclass instances, or None if absent."""
    path = CACHE / f"{name}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [cls(**d) for d in data]
    return cls(**data)
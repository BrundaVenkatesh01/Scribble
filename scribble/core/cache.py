import json
from dataclasses import asdict
from pathlib import Path

CACHE = Path(".cache")


def save(name: str, obj) -> None:
    CACHE.mkdir(exist_ok=True)
    data = [asdict(o) for o in obj] if isinstance(obj, list) else asdict(obj)
    (CACHE / f"{name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def load(name: str, cls):
    path = CACHE / f"{name}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return [cls(**d) for d in data] if isinstance(data, list) else cls(**data)
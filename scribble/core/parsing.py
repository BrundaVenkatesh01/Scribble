import json


def parse_json(raw: str) -> dict:
    """Pull the JSON object out of a model reply, even if wrapped in fences or prose."""
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output:\n{raw[:300]}")
    return json.loads(raw[start:end + 1])
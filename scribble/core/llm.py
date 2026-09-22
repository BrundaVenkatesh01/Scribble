import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()                  # reads .env into environment variables
client = genai.Client()        # picks up GEMINI_API_KEY automatically

MODEL = "gemini-3.5-flash-lite"

def _retry_delay(err) -> float | None:
    """Pull Google's suggested retry delay out of a 429, if present."""
    try:
        for detail in err.details["error"]["details"]:
            if detail.get("@type", "").endswith("RetryInfo"):
                return float(detail["retryDelay"].rstrip("s"))
    except (KeyError, TypeError, ValueError):
        pass
    return None

def _retry(call, attempts: int = 4):
    """Retry transient API failures, backing off between attempts."""
    delay = 2
    for attempt in range(attempts):
        try:
            return call()
        except errors.ServerError:          # 5xx: Google's problem, always retry
            if attempt == attempts - 1:
                raise
            print(f"  (retrying in {delay}s...)")
            time.sleep(delay)
            delay *= 2
        except errors.ClientError as e:     # 4xx: only a short-window 429 is retryable
            if e.code != 429 or attempt == attempts - 1:
                raise
            wait = _retry_delay(e)
            if wait is None or wait > 60:   # daily quota — retrying won't help
                raise
            print(f"  (rate limited — waiting {wait}s...)")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def ask(system: str, user: str, thinking: bool = True) -> str:
    """One LLM call. Every agent goes through this."""
    response = _retry(lambda: client.models.generate_content(
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(system_instruction=system),
    ))
    if not response.text:
        reason = response.candidates[0].finish_reason if response.candidates else "no candidates"
        raise RuntimeError(f"Empty model response (finish_reason={reason})")
    return response.text
    


def ask_grounded(system: str, user: str) -> tuple[str, list[str]]:
    """LLM call with Google Search enabled. Returns (text, source_urls)."""
    response = _retry(lambda: client.models.generate_content(
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    ))
    if not response.text:
        reason = response.candidates[0].finish_reason if response.candidates else "no candidates"
        raise RuntimeError(f"Empty model response (finish_reason={reason})")
    sources = []
    meta = response.candidates[0].grounding_metadata
    if meta and meta.grounding_chunks:
        for chunk in meta.grounding_chunks:
            if chunk.web and chunk.web.uri:
                sources.append(chunk.web.uri)
    return response.text, sources
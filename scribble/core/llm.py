import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()                  # reads .env into environment variables
client = genai.Client()        # picks up GEMINI_API_KEY automatically

MODEL = "gemini-3.6-flash"


def _retry(call, attempts: int = 4):
    """Retry transient API failures with exponential backoff."""
    delay = 2
    for attempt in range(attempts):
        try:
            return call()
        except errors.ServerError:          # 5xx: Google's problem, always retry
            if attempt == attempts - 1:
                raise
        except errors.ClientError as e:     # 4xx: only 429 is worth retrying
            if e.code != 429 or attempt == attempts - 1:
                raise
        print(f"  (retrying in {delay}s...)")
        time.sleep(delay)
        delay *= 2
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
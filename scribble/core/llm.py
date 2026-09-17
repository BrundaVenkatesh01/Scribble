from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

MODEL = "gemini-3.6-flash"


def ask(system: str, user: str, thinking: bool = False) -> str:
    """One LLM call. Every agent goes through this."""
    config = types.GenerateContentConfig(system_instruction=system)
    if not thinking:
        config.thinking_config = types.ThinkingConfig(thinking_budget=0)

    response = client.models.generate_content(
        model=MODEL,
        contents=user,
        config=config,
    )
    return response.text
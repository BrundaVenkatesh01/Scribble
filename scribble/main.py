from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()                  # reads .env into environment variables
client = genai.Client()        # picks up GEMINI_API_KEY automatically

def ask(system: str, user: str) -> str:
    """One LLM call. Every agent will go through this."""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return response.text

if __name__ == "__main__":
    print(ask("You are a friendly assistant.", "Say hello in one sentence."))
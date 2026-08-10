import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the environment."
    )


client = genai.Client(api_key=API_KEY)


def generate_answer(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the generated answer.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text
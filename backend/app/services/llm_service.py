import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

# Keep API calls from hanging for a very long time.
# Value is in milliseconds.
REQUEST_TIMEOUT_MS = int(
    os.getenv(
        "GEMINI_TIMEOUT_MS",
        "30000"
    )
)

# Number of retries for temporary API failures.
MAX_RETRIES = int(
    os.getenv(
        "GEMINI_MAX_RETRIES",
        "1"
    )
)


if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the environment."
    )


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        timeout=REQUEST_TIMEOUT_MS
    )
)


# --------------------------------------------------
# Generate answer
# --------------------------------------------------

def generate_answer(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the generated answer.

    Temporary API failures are retried once.
    Long-running requests are limited by GEMINI_TIMEOUT_MS.
    """

    last_error = None

    for attempt in range(
        MAX_RETRIES + 1
    ):

        start_time = time.perf_counter()

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1200,
                    candidate_count=1
                )
            )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            print(
                f"[LLM] Gemini response: "
                f"{elapsed:.3f}s"
            )

            if not response.text:

                return (
                    "Gemini returned an empty response."
                )

            return response.text

        except Exception as error:

            elapsed = (
                time.perf_counter()
                - start_time
            )

            last_error = error

            print(
                f"[LLM ERROR] Attempt "
                f"{attempt + 1}/{MAX_RETRIES + 1} "
                f"failed after "
                f"{elapsed:.3f}s"
            )

            print(
                f"[LLM ERROR] {error}"
            )

            # Don't immediately retry every possible
            # error. Only retry temporary-looking failures.
            error_text = str(
                error
            ).upper()

            temporary_error = any(
                code in error_text
                for code in [
                    "429",
                    "500",
                    "502",
                    "503",
                    "504",
                    "UNAVAILABLE",
                    "RESOURCE_EXHAUSTED",
                    "TIMEOUT",
                    "DEADLINE"
                ]
            )

            if (
                not temporary_error
                or attempt >= MAX_RETRIES
            ):
                break

            # Small delay before retry.
            time.sleep(1)


    # --------------------------------------------------
    # Final failure
    # --------------------------------------------------

    return (
        "The AI generation service is temporarily "
        "unavailable. The repository search completed "
        "successfully, but Gemini could not generate "
        "the final answer. Please try again."
    )
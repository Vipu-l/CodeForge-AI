import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set."
    )


client = genai.Client(
    api_key=api_key
)


print("=" * 70)
print("AVAILABLE GEMINI MODELS")
print("=" * 70)

try:

    for model in client.models.list():

        supported_actions = getattr(
            model,
            "supported_actions",
            []
        )

        if (
            not supported_actions
            or "generateContent" in supported_actions
        ):

            print(
                f"\nName: {model.name}"
            )

            print(
                f"Display name: "
                f"{getattr(model, 'display_name', '')}"
            )

            print(
                f"Supported actions: "
                f"{supported_actions}"
            )

except Exception as error:

    print("\nERROR:")
    print(error)


print("\n" + "=" * 70)
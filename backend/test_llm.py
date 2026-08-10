from app.services.llm_service import generate_answer


answer = generate_answer(
    "Explain what a REST API is in two simple sentences."
)


print("\nGemini Response:\n")
print(answer)
import time

from app.services.llm_service import generate_answer


print("=" * 60)
print("GEMINI DIRECT TEST")
print("=" * 60)

prompt = """
Answer in one short sentence:

What is a Python function?
"""


start = time.perf_counter()

answer = generate_answer(prompt)

elapsed = time.perf_counter() - start


print()
print("Response time:", f"{elapsed:.3f}s")

print()
print("Response:")
print("-" * 60)
print(answer)

print()
print("=" * 60)
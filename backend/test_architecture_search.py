from app.services.code_index_service import build_code_index
from app.services.embedding_service import generate_embedding


repository_path = r"repositories\CodeForge-AI"

question = (
    "How do repository_service.py, "
    "code_index_service.py, "
    "vector_store.py, "
    "rag_service.py, and "
    "llm_service.py work together?"
)


print("Building code index...")

search_index = build_code_index(
    repository_path
)

print("Index created.")
print()

query_embedding = generate_embedding(
    question
)

results = search_index.search(
    query_embedding,
    top_k=10,
    query_text=question
)


print("======================")
print("ARCHITECTURE SEARCH")
print("======================")


for result in results:

    document = result["document"]

    print()
    print("Type:", document.get("type"))
    print("Name:", document.get("name"))
    print("File:", document.get("file"))
    print(
        "Lines:",
        document.get("start_line"),
        "-",
        document.get("end_line")
    )

    print(
        "Combined Score:",
        round(result["score"], 4)
    )

    print(
        "Semantic Score:",
        round(
            result.get("semantic_score", 0),
            4
        )
    )

    print(
        "Text Score:",
        round(
            result.get("text_score", 0),
            4
        )
    )
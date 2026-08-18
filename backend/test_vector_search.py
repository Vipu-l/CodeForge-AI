from app.services.code_index_service import build_code_index
from app.services.embedding_service import generate_embedding


print("Building code index...")

index = build_code_index(
    r"repositories\CodeForge-AI"
)

print("Index created.")

print()
print("======================")
print("VECTOR SEARCH RESULTS")
print("======================")

question = "How does the API handle repository analysis?"

query_embedding = generate_embedding(
    question
)

results = index.search(
    query_embedding,
    top_k=5,
    min_score=0.20
)

if not results:

    print("No relevant results found.")

else:

    for result in results:

        document = result["document"]
        score = result["score"]

        print()
        print(
            f"File: {document.get('file')}"
        )

        print(
            f"Type: {document.get('type')}"
        )

        print(
            f"Name: {document.get('name')}"
        )

        print(
            f"Lines: "
            f"{document.get('start_line')}-"
            f"{document.get('end_line')}"
        )

        print(
            f"Score: {score:.4f}"
        )
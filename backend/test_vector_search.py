from app.services.code_index_service import build_code_index
from app.services.embedding_service import generate_embedding
from app.services.vector_store import VectorStore


repository_path = "repositories/CodeForge-AI"


print("Building code index...")

hnsw_index = build_code_index(
    repository_path
)

print("Index created.")


# Create a separate brute-force store
store = VectorStore()


for index, document in enumerate(
    hnsw_index.documents
):

    embedding = hnsw_index.vectors[index]

    store.add(
        document,
        embedding
    )


question = (
    "How does the API handle "
    "repository analysis?"
)


query_embedding = generate_embedding(
    question
)


results = store.search(
    query_embedding,
    top_k=5
)


print("\n======================")
print("BRUTE FORCE RESULTS")
print("======================")


for result in results:

    document = result["document"]

    print(
        f"\nFile: {document.get('file')}"
    )

    print(
        f"Type: {document.get('type')}"
    )

    print(
        f"Name: {document.get('name')}"
    )

    print(
        f"Score: {result['score']:.4f}"
    )
import time

from app.services.index_manager import get_index
from app.services.embedding_service import generate_embedding
from app.services.rag_service import answer_question


REPOSITORY = "CodeForge-AI"

QUESTION = "What does build_code_index do?"


print("=" * 60)
print("CODEFORGE AI RAG PERFORMANCE TEST")
print("=" * 60)


# --------------------------------------------------
# 1. Load saved index
# --------------------------------------------------

start = time.perf_counter()

search_index = get_index(
    REPOSITORY
)

index_time = time.perf_counter() - start


if search_index is None:

    print("ERROR: Repository index not found.")

    raise SystemExit(1)


print(
    f"\nIndex loading time: "
    f"{index_time:.4f} seconds"
)

print(
    f"Indexed documents: "
    f"{len(search_index.documents)}"
)


# --------------------------------------------------
# 2. Generate question embedding
# --------------------------------------------------

start = time.perf_counter()

query_embedding = generate_embedding(
    QUESTION
)

embedding_time = time.perf_counter() - start


print(
    f"\nEmbedding time: "
    f"{embedding_time:.4f} seconds"
)


# --------------------------------------------------
# 3. Vector search
# --------------------------------------------------

start = time.perf_counter()

results = search_index.search(
    query_embedding,
    top_k=8,
    query_text=QUESTION
)

search_time = time.perf_counter() - start


print(
    f"Vector search time: "
    f"{search_time:.4f} seconds"
)

print(
    f"Retrieved results: "
    f"{len(results)}"
)


# --------------------------------------------------
# 4. Display retrieved files
# --------------------------------------------------

print("\nTOP RESULTS")
print("-" * 60)

for result in results:

    document = result["document"]

    print(
        f"{document.get('file')} | "
        f"{document.get('name')} | "
        f"score={result.get('score', 0):.4f}"
    )


# --------------------------------------------------
# 5. Full RAG + LLM
# --------------------------------------------------

start = time.perf_counter()

try:

    answer = answer_question(
        QUESTION,
        search_index
    )

    rag_time = time.perf_counter() - start

    print(
        f"\nFull RAG response time: "
        f"{rag_time:.4f} seconds"
    )

    print("\nANSWER")
    print("-" * 60)

    print(
        answer.get(
            "answer",
            answer
        )
    )

except Exception as error:

    rag_time = time.perf_counter() - start

    print(
        f"\nRAG failed after "
        f"{rag_time:.4f} seconds"
    )

    print(
        f"Error: {error}"
    )


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("PERFORMANCE SUMMARY")
print("=" * 60)

print(
    f"Index loading : {index_time:.4f}s"
)

print(
    f"Embedding      : {embedding_time:.4f}s"
)

print(
    f"Vector search  : {search_time:.4f}s"
)

print(
    f"Full RAG       : {rag_time:.4f}s"
)

print("=" * 60)
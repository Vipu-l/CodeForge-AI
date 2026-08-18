import time

from app.services.code_index_service import build_code_index


REPOSITORY_PATH = r"repositories\CodeForge-AI"


print("=" * 50)
print("CODE INDEX PERFORMANCE TEST")
print("=" * 50)

start = time.perf_counter()

index = build_code_index(
    REPOSITORY_PATH
)

elapsed = time.perf_counter() - start

print()
print(f"Indexed chunks: {len(index.documents)}")
print(f"Embeddings: {len(index.embeddings)}")
print(f"Time: {elapsed:.2f} seconds")

if index.documents:
    print()
    print("FIRST CHUNK:")
    print("-" * 50)

    first = index.documents[0]

    print("File:", first.get("file"))
    print("Type:", first.get("type"))
    print("Name:", first.get("name"))
    print(
        "Lines:",
        first.get("start_line"),
        "-",
        first.get("end_line")
    )

print()
print("=" * 50)
print("INDEX TEST COMPLETE")
print("=" * 50)
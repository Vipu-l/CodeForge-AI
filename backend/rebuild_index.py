from app.services.code_index_service import build_code_index
from app.services.index_manager import save_index


REPOSITORY_NAME = "CodeForge-AI"
REPOSITORY_PATH = r"repositories\CodeForge-AI"


print("========================================")
print("REBUILDING CODEFORGE AI INDEX")
print("========================================")

print("\n1. Building index from current source code...")

index = build_code_index(
    REPOSITORY_PATH
)

print(
    f"Indexed chunks: {len(index.documents)}"
)

print("\n2. Saving latest index...")

save_index(
    REPOSITORY_NAME,
    index
)

print("\n3. Index saved successfully.")

print("\n========================================")
print("INDEX REBUILD COMPLETE")
print("========================================")
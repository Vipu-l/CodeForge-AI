from app.services.index_manager import get_index


REPOSITORY_NAME = "CodeForge-AI"


index = get_index(
    REPOSITORY_NAME
)

if index is None:
    print("NO INDEX FOUND")
    raise SystemExit


print("INDEX LOADED")
print("Documents:", len(index.documents))

print("\nVECTOR STORE SEARCH IMPLEMENTATION:")
print("=" * 60)


for document in index.documents:

    file_path = str(
        document.get("file", "")
    ).replace("\\", "/")

    if file_path.endswith(
        "/backend/app/services/vector_store.py"
    ):

        print(
            "\nTYPE:",
            document.get("type")
        )

        print(
            "NAME:",
            document.get("name")
        )

        print(
            "LINES:",
            document.get("start_line"),
            "-",
            document.get("end_line")
        )

        print("\nCODE:")
        print(
            document.get("code", "")
        )

        print("=" * 60)
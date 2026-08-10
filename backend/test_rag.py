from app.services.code_index_service import build_code_index
from app.services.rag_service import answer_question


repository_path = "repositories/CodeForge-AI"


print("Building code index...")

index = build_code_index(
    repository_path
)

print("Index created.")

print("\nTotal indexed documents:")
print(len(index.documents))

print("\nIndexed files:")

for document in index.documents:
    print(
        document.get("file"),
        document.get("type"),
        document.get("name")
    )


    
question = "How does the API handle repository analysis?"


result = answer_question(
    question,
    index,
    top_k=5
)


print("\n====================")
print("ANSWER")
print("====================")

print(result["answer"])


print("\n====================")
print("SOURCES")
print("====================")


for source in result["sources"]:

    print(
        f"{source['file']}:"
        f"{source['start_line']}-"
        f"{source['end_line']}"
    )
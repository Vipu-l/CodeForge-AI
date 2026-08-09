from app.services.embedding_service import generate_embedding
from app.services.vector_store import VectorStore


store = VectorStore()


documents = [
    {
        "file": "auth.py",
        "code": "def authenticate_user(username, password): ..."
    },
    {
        "file": "shipping.py",
        "code": "def calculate_shipping(weight, distance): ..."
    },
    {
        "file": "payment.py",
        "code": "def process_payment(card, amount): ..."
    }
]


for document in documents:
    embedding = generate_embedding(
        document["code"]
    )

    store.add(
        document,
        embedding
    )


query = "Where does the application handle user login?"

query_embedding = generate_embedding(query)


results = store.search(
    query_embedding,
    top_k=2
)


for result in results:
    print("\nFile:", result["document"]["file"])
    print("Score:", result["score"])
    print("Code:", result["document"]["code"])
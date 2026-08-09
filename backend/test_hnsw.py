from app.services.embedding_service import generate_embedding
from app.services.hnsw_index import HNSWIndex


documents = [
    {
        "file": "auth.py",
        "code": """
        def authenticate_user(username, password):
            return check_credentials(username, password)
        """
    },
    {
        "file": "payment.py",
        "code": """
        def process_payment(card, amount):
            return charge_card(card, amount)
        """
    },
    {
        "file": "shipping.py",
        "code": """
        def calculate_shipping(weight, distance):
            return weight * distance
        """
    },
    {
        "file": "users.py",
        "code": """
        def create_user(name, email):
            return save_user(name, email)
        """
    }
]


index = HNSWIndex()


for document in documents:

    embedding = generate_embedding(
        document["code"]
    )

    index.add(
        embedding,
        document
    )


query = "Where does the application handle user login?"

query_embedding = generate_embedding(query)


results = index.search(
    query_embedding,
    top_k=3
)


for result in results:

    print("\nFile:", result["document"]["file"])

    print(
        "Similarity:",
        result["score"]
    )

    print(
        "Code:",
        result["document"]["code"]
    )
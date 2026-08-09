from app.services.embedding_service import generate_embedding


text = """
def login_user(username, password):
    authenticate_user(username, password)
"""


embedding = generate_embedding(text)

print("Embedding dimensions:", len(embedding))
print("First 10 values:", embedding[:10])
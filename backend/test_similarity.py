from app.services.embedding_service import generate_embedding


text1 = "How does the application handle user login?"

text2 = """
def authenticate_user(username, password):
    # Verify the user's credentials
    return check_credentials(username, password)
"""

text3 = """
def calculate_shipping_cost(weight, distance):
    return weight * distance
"""


embedding1 = generate_embedding(text1)
embedding2 = generate_embedding(text2)
embedding3 = generate_embedding(text3)


import numpy as np


def cosine_similarity(vector_a, vector_b):
    a = np.array(vector_a)
    b = np.array(vector_b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


similarity_login = cosine_similarity(
    embedding1,
    embedding2
)

similarity_shipping = cosine_similarity(
    embedding1,
    embedding3
)


print("Login similarity:", similarity_login)
print("Shipping similarity:", similarity_shipping)
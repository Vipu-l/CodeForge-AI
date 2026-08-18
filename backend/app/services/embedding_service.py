from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

# Load the model only once when the service starts.
model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding for a single piece of text.
    """

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


def generate_embeddings(
    texts: list[str],
    batch_size: int = 32
) -> list[list[float]]:
    """
    Generate embeddings for multiple texts in batches.

    Batch processing is significantly faster than calling
    model.encode() separately for every chunk.
    """

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()
import numpy as np


class VectorStore:
    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add(self, document: dict, embedding: list[float]):
        self.documents.append(document)
        self.embeddings.append(embedding)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5
    ):
        if not self.embeddings:
            return []

        query = np.array(query_embedding)

        scores = []

        for index, embedding in enumerate(self.embeddings):
            vector = np.array(embedding)

            similarity = np.dot(query, vector) / (
                np.linalg.norm(query)
                * np.linalg.norm(vector)
            )

            scores.append((index, similarity))

        scores.sort(
            key=lambda item: item[1],
            reverse=True
        )

        results = []

        for index, score in scores[:top_k]:
            results.append({
                "document": self.documents[index],
                "score": float(score)
            })

        return results
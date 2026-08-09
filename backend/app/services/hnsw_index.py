import random
import numpy as np


class HNSWIndex:
    """
    Simplified educational implementation of
    a Hierarchical Navigable Small World index.
    """

    def __init__(
        self,
        max_connections: int = 8,
        max_layers: int = 4
    ):
        self.max_connections = max_connections
        self.max_layers = max_layers

        self.vectors = []
        self.documents = []
        self.graph = []
        self.levels = []

    def _similarity(self, vector_a, vector_b):
        a = np.array(vector_a)
        b = np.array(vector_b)

        denominator = (
            np.linalg.norm(a) *
            np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(a, b) / denominator
        )

    def _random_level(self):
        level = 0

        while (
            random.random() < 0.5
            and level < self.max_layers - 1
        ):
            level += 1

        return level

    def add(self, vector, document):
        index = len(self.vectors)

        self.vectors.append(vector)
        self.documents.append(document)

        level = self._random_level()
        self.levels.append(level)

        connections = []

        if index > 0:

            similarities = []

            for existing_index, existing_vector in enumerate(
                self.vectors[:-1]
            ):
                score = self._similarity(
                    vector,
                    existing_vector
                )

                similarities.append(
                    (existing_index, score)
                )

            similarities.sort(
                key=lambda item: item[1],
                reverse=True
            )

            connections = [
                item[0]
                for item in similarities[
                    :self.max_connections
                ]
            ]

        self.graph.append(connections)

    def search(
        self,
        query_vector,
        top_k: int = 5
    ):
        if not self.vectors:
            return []

        visited = set()
        candidates = []

        # Start from a random entry point.
        current = random.randrange(
            len(self.vectors)
        )

        while True:

            if current in visited:
                break

            visited.add(current)

            current_score = self._similarity(
                query_vector,
                self.vectors[current]
            )

            candidates.append(
                (current, current_score)
            )

            neighbors = self.graph[current]

            best_neighbor = None
            best_score = current_score

            for neighbor in neighbors:

                if neighbor in visited:
                    continue

                score = self._similarity(
                    query_vector,
                    self.vectors[neighbor]
                )

                if score > best_score:
                    best_score = score
                    best_neighbor = neighbor

            if best_neighbor is None:
                break

            current = best_neighbor

        candidates.sort(
            key=lambda item: item[1],
            reverse=True
        )

        results = []

        for index, score in candidates[:top_k]:
            results.append({
                "document": self.documents[index],
                "score": float(score)
            })

        return results
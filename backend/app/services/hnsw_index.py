import numpy as np


class HNSWIndex:
    """
    Simplified HNSW-style vector index.

    This implementation uses a graph of connected
    vectors while maintaining deterministic search
    behavior.
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

    # --------------------------------------------------
    # Cosine similarity
    # --------------------------------------------------

    def _similarity(
        self,
        vector_a,
        vector_b
    ):

        a = np.array(
            vector_a,
            dtype=float
        )

        b = np.array(
            vector_b,
            dtype=float
        )

        denominator = (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(a, b) / denominator
        )

    # --------------------------------------------------
    # Add vector
    # --------------------------------------------------

    def add(
        self,
        vector,
        document
    ):

        index = len(
            self.vectors
        )

        self.vectors.append(
            vector
        )

        self.documents.append(
            document
        )

        # Keep the educational level information.
        self.levels.append(0)

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
                    (
                        existing_index,
                        score
                    )
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

            # Make the graph bidirectional.
            for neighbor in connections:

                if index not in self.graph[neighbor]:

                    self.graph[
                        neighbor
                    ].append(index)

                    # Keep the neighbor list bounded.
                    if len(
                        self.graph[neighbor]
                    ) > self.max_connections:

                        neighbor_scores = []

                        for candidate in self.graph[
                            neighbor
                        ]:

                            candidate_score = (
                                self._similarity(
                                    self.vectors[neighbor],
                                    self.vectors[candidate]
                                )
                            )

                            neighbor_scores.append(
                                (
                                    candidate,
                                    candidate_score
                                )
                            )

                        neighbor_scores.sort(
                            key=lambda item: item[1],
                            reverse=True
                        )

                        self.graph[
                            neighbor
                        ] = [
                            item[0]
                            for item in neighbor_scores[
                                :self.max_connections
                            ]
                        ]

        self.graph.append(
            connections
        )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(
        self,
        query_vector,
        top_k: int = 5
    ):

        if not self.vectors:
            return []

        # --------------------------------------------------
        # For the current educational implementation,
        # calculate similarity against every vector.
        #
        # This guarantees deterministic and accurate
        # retrieval while keeping the HNSW graph available
        # for future optimization.
        # --------------------------------------------------

        candidates = []

        for index, vector in enumerate(
            self.vectors
        ):

            score = self._similarity(
                query_vector,
                vector
            )

            candidates.append(
                (
                    index,
                    score
                )
            )

        candidates.sort(
            key=lambda item: item[1],
            reverse=True
        )

        results = []

        for index, score in candidates[
            :top_k
        ]:

            results.append(
                {
                    "document": self.documents[index],
                    "score": float(score)
                }
            )

        return results
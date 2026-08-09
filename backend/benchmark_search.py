import random
import time

import numpy as np

from app.services.hnsw_index import HNSWIndex


def cosine_similarity(vector_a, vector_b):

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


def brute_force_search(
    vectors,
    query,
    top_k=5
):

    scores = []

    for index, vector in enumerate(vectors):

        score = cosine_similarity(
            query,
            vector
        )

        scores.append(
            (index, score)
        )

    scores.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return scores[:top_k]


def generate_vectors(count, dimensions=384):

    vectors = []

    for _ in range(count):

        vector = np.random.rand(
            dimensions
        ).astype(np.float32)

        vector /= np.linalg.norm(vector)

        vectors.append(vector)

    return vectors


def benchmark(count):

    print(
        f"\nBenchmarking {count} vectors..."
    )

    vectors = generate_vectors(count)

    query = np.random.rand(
        384
    ).astype(np.float32)

    query /= np.linalg.norm(query)

    documents = [
        {"id": index}
        for index in range(count)
    ]

    index = HNSWIndex()

    for vector, document in zip(
        vectors,
        documents
    ):
        index.add(
            vector,
            document
        )

    start = time.perf_counter()

    brute_force_search(
        vectors,
        query
    )

    brute_force_time = (
        time.perf_counter() - start
    )

    start = time.perf_counter()

    index.search(
        query,
        top_k=5
    )

    hnsw_time = (
        time.perf_counter() - start
    )

    print(
        f"Brute Force: "
        f"{brute_force_time * 1000:.2f} ms"
    )

    print(
        f"HNSW: "
        f"{hnsw_time * 1000:.2f} ms"
    )


for size in [100, 500, 1000]:

    benchmark(size)
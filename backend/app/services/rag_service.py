from app.services.embedding_service import generate_embedding
from app.services.llm_service import generate_answer


def cosine_similarity(vector_a, vector_b):
    """
    Calculate cosine similarity between two vectors.
    """

    import numpy as np

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


def build_context(results: list[dict]) -> str:
    """
    Convert retrieved code chunks into
    context for Gemini.
    """

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):

        document = result["document"]
        score = result["score"]

        context_parts.append(
            f"""
SOURCE {index}

File:
{document.get("file", "unknown")}

Type:
{document.get("type", "unknown")}

Name:
{document.get("name", "unknown")}

Lines:
{document.get("start_line", "?")}-{document.get("end_line", "?")}

Similarity:
{score:.4f}

CODE:
{document.get("code", "")}
"""
        )

    return "\n".join(context_parts)


def answer_question(
    question: str,
    search_index,
    top_k: int = 5
) -> dict:

    query_embedding = generate_embedding(
        question
    )

    results = search_index.search(
        query_embedding,
        top_k=top_k
    )

    if not results:

        return {
            "answer": (
                "I couldn't find relevant code "
                "in the repository."
            ),
            "sources": []
        }

    context = build_context(
        results
    )

    prompt = f"""
You are CodeForge AI, an AI assistant
that understands software repositories.

Answer the user's question using ONLY
the supplied repository context.

Do not invent files, functions, classes,
or behavior that are not present.

If the context is insufficient, say so.

Always mention relevant source files
and line numbers when possible.

USER QUESTION:
{question}

REPOSITORY CONTEXT:
{context}

Give a clear and technically accurate
answer based only on the provided code.
"""

    answer = generate_answer(prompt)

    sources = []

    for result in results:

        document = result["document"]

        sources.append({
            "file": document.get("file"),
            "start_line": document.get("start_line"),
            "end_line": document.get("end_line"),
            "score": result["score"]
        })

    return {
        "answer": answer,
        "sources": sources
    }
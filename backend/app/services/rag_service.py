from app.services.embedding_service import generate_embedding
from app.services.llm_service import generate_answer


def build_context(results: list[dict]) -> str:
    """
    Convert retrieved code chunks into context
    that can be sent to the LLM.
    """

    context_parts = []

    for index, result in enumerate(results, start=1):

        document = result["document"]
        score = result["score"]

        context_parts.append(
            f"""
SOURCE {index}
File: {document.get("file", "unknown")}
Type: {document.get("type", "unknown")}
Name: {document.get("name", "unknown")}
Lines: {document.get("start_line", "?")}-{document.get("end_line", "?")}
Similarity: {score:.4f}

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
    """
    Retrieve relevant code and ask Gemini
    to answer using that context.
    """

    # Convert the question into an embedding
    query_embedding = generate_embedding(question)

    # Search the HNSW index
    results = search_index.search(
        query_embedding,
        top_k=top_k
    )

    if not results:
        return {
            "answer": "I couldn't find relevant code in the repository.",
            "sources": []
        }

    # Convert retrieved code into context
    context = build_context(results)

    prompt = f"""
You are CodeForge AI, an AI assistant that understands
software repositories.

Answer the user's question using ONLY the supplied
repository context.

Do not invent files, functions, classes, or behavior
that are not present in the context.

If the context is insufficient, clearly say that you
do not have enough information.

Always mention relevant source files and line numbers
when possible.

USER QUESTION:
{question}

REPOSITORY CONTEXT:
{context}

Give a clear and technically accurate answer.
"""

    # Send the RAG prompt to Gemini
    answer = generate_answer(prompt)

    # Prepare source information
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
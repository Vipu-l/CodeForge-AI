import re
import time

from app.services.embedding_service import generate_embedding
from app.services.llm_service import generate_answer


# --------------------------------------------------
# Retrieval configuration
# --------------------------------------------------

# Semantic candidate pool.
RETRIEVAL_K = 20

# Maximum number of chunks sent to Gemini.
CONTEXT_K = 8

# Maximum source-code characters per chunk.
MAX_CHARS_PER_CHUNK = 12000

# Additional candidates collected using exact/lexical matching.
LEXICAL_CANDIDATE_K = 20


# --------------------------------------------------
# Similarity
# --------------------------------------------------

def cosine_similarity(
    vector_a,
    vector_b
):
    """
    Calculate cosine similarity between two vectors.
    """

    import numpy as np

    a = np.asarray(
        vector_a,
        dtype=float
    )

    b = np.asarray(
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
# Context formatting
# --------------------------------------------------

def _get_chunk_text(
    chunk: dict
) -> str:
    """
    Convert a repository chunk into the exact context
    representation sent to the LLM.
    """

    file_path = chunk.get(
        "file",
        "Unknown file"
    )

    chunk_type = chunk.get(
        "type",
        "unknown"
    )

    name = chunk.get(
        "name",
        "unknown"
    )

    start_line = chunk.get(
        "start_line",
        "?"
    )

    end_line = chunk.get(
        "end_line",
        "?"
    )

    code = chunk.get(
        "code",
        ""
    )

    if len(code) > MAX_CHARS_PER_CHUNK:

        code = (
            code[:MAX_CHARS_PER_CHUNK]
            + "\n\n[Code truncated]"
        )

    return (
        f"File: {file_path}\n"
        f"Type: {chunk_type}\n"
        f"Name: {name}\n"
        f"Lines: {start_line}-{end_line}\n"
        f"Code:\n"
        f"{code}"
    )


def build_context(
    results: list[dict]
) -> str:
    """
    Build a clean, source-grounded context for Gemini.
    """

    if not results:
        return (
            "No relevant repository code was retrieved."
        )

    context_parts = []

    for position, result in enumerate(
        results[:CONTEXT_K],
        start=1
    ):

        document = result.get(
            "document",
            {}
        )

        score = result.get(
            "combined_score",
            result.get(
                "score",
                0.0
            )
        )

        chunk_text = _get_chunk_text(
            document
        )

        context_parts.append(
            (
                f"===== SOURCE {position} =====\n"
                f"Combined score: {score:.4f}\n"
                f"{chunk_text}\n"
                f"===== END SOURCE {position} ====="
            )
        )

    return "\n\n".join(
        context_parts
    )


# --------------------------------------------------
# Text normalization
# --------------------------------------------------

def _normalize_text(
    value: str
) -> str:
    """
    Normalize text for reliable identifier matching.
    """

    if not value:
        return ""

    value = str(value).lower()

    return re.sub(
        r"[^a-z0-9_]",
        "",
        value
    )


def _extract_identifier(
    question: str
):
    """
    Extract a likely code identifier from a question.

    Examples:

        get_index()
        VectorStore.search()
        build_code_index
    """

    if not question:
        return None

    # Match function-style identifiers first.
    match = re.search(
        r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        question
    )

    if match:
        return match.group(1)

    candidates = re.findall(
        r"\b[A-Za-z_][A-Za-z0-9_]*\b",
        question
    )

    ignored_words = {
        "what",
        "does",
        "how",
        "exactly",
        "show",
        "me",
        "the",
        "exact",
        "implementation",
        "of",
        "work",
        "function",
        "method",
        "class",
        "is",
        "do",
        "when",
        "repository",
        "contains",
        "code",
        "python",
        "happens",
        "with",
        "from",
        "to",
        "and",
        "travel"
    }

    for candidate in reversed(
        candidates
    ):

        if candidate.lower() not in ignored_words:
            return candidate

    return None


def _question_tokens(
    question: str
) -> set[str]:
    """
    Extract useful words from the question.
    """

    if not question:
        return set()

    words = re.findall(
        r"[A-Za-z_][A-Za-z0-9_]*",
        question.lower()
    )

    stop_words = {
        "what",
        "does",
        "how",
        "exactly",
        "show",
        "me",
        "the",
        "exact",
        "implementation",
        "of",
        "work",
        "function",
        "method",
        "class",
        "is",
        "do",
        "when",
        "repository",
        "contains",
        "code",
        "python",
        "a",
        "an",
        "and",
        "or",
        "to",
        "from",
        "with",
        "in",
        "on",
        "for",
        "about",
        "travel"
    }

    return {
        word
        for word in words
        if word not in stop_words
        and len(word) > 2
    }


# --------------------------------------------------
# Exact matching
# --------------------------------------------------

def _text_match_score(
    question: str,
    document: dict
) -> float:
    """
    Calculate exact identifier relevance.

    Exact function/method/class/module matches receive
    the strongest score.
    """

    identifier = _extract_identifier(
        question
    )

    normalized_identifier = _normalize_text(
        identifier or ""
    )

    document_name = _normalize_text(
        document.get(
            "name",
            ""
        )
    )

    document_file = _normalize_text(
        document.get(
            "file",
            ""
        )
    )

    document_type = str(
        document.get(
            "type",
            ""
        )
    ).lower()

    code = str(
        document.get(
            "code",
            ""
        )
    )

    normalized_code = _normalize_text(
        code
    )

    # Exact function or method.
    if (
        normalized_identifier
        and document_name == normalized_identifier
        and document_type in {
            "function",
            "method"
        }
    ):
        return 1.0

    # Exact class.
    if (
        normalized_identifier
        and document_name == normalized_identifier
        and document_type == "class"
    ):
        return 0.95

    # Exact module.
    if (
        normalized_identifier
        and document_name == normalized_identifier
        and document_type == "module"
    ):
        return 0.85

    # Identifier appears in filename.
    if (
        normalized_identifier
        and normalized_identifier in document_file
    ):
        return 0.85

    # Identifier appears in source code.
    if (
        normalized_identifier
        and normalized_identifier in normalized_code
    ):
        return 0.60

    return 0.0


# --------------------------------------------------
# Lexical matching
# --------------------------------------------------

def _lexical_question_score(
    question: str,
    document: dict
) -> float:
    """
    Calculate lexical relevance for architectural
    and behavioral questions.
    """

    tokens = _question_tokens(
        question
    )

    if not tokens:
        return 0.0

    name = str(
        document.get(
            "name",
            ""
        )
    ).lower()

    file_path = str(
        document.get(
            "file",
            ""
        )
    ).lower()

    code = str(
        document.get(
            "code",
            ""
        )
    ).lower()

    searchable_text = (
        f"{name} "
        f"{file_path} "
        f"{code}"
    )

    matches = 0

    for token in tokens:

        if token in searchable_text:
            matches += 1

    if matches == 0:
        return 0.0

    return min(
        matches / len(tokens),
        1.0
    )


# --------------------------------------------------
# Question classification
# --------------------------------------------------

def _is_architecture_question(
    question: str
) -> bool:
    """
    Detect questions that are likely to require
    multiple files or components.
    """

    text = question.lower()

    architecture_terms = {
        "how does",
        "how do",
        "flow",
        "travel",
        "work together",
        "communicate",
        "pipeline",
        "architecture",
        "frontend",
        "backend",
        "gemini",
        "request",
        "response",
        "calls",
        "calling"
    }

    return any(
        term in text
        for term in architecture_terms
    )


def _is_behavior_question(
    question: str
) -> bool:
    """
    Detect questions asking what happens during
    a particular behavior or failure.
    """

    text = question.lower()

    behavior_terms = {
        "what happens",
        "when",
        "invalid",
        "error",
        "exception",
        "failure",
        "fails",
        "handle",
        "handling",
        "if"
    }

    return any(
        term in text
        for term in behavior_terms
    )


# --------------------------------------------------
# Candidate augmentation
# --------------------------------------------------

def _get_all_documents(
    search_index
) -> list[dict]:
    """
    Return all documents currently stored in the index.

    VectorStore exposes documents as a public list.
    This allows exact identifier retrieval to recover
    a function even when semantic search ranks it poorly.
    """

    documents = getattr(
        search_index,
        "documents",
        None
    )

    if not isinstance(
        documents,
        list
    ):
        return []

    return documents


def _make_document_key(
    document: dict
) -> tuple:
    """
    Create a stable key for deduplicating chunks.
    """

    return (
        str(
            document.get(
                "file",
                ""
            )
        ),
        str(
            document.get(
                "type",
                ""
            )
        ),
        str(
            document.get(
                "name",
                ""
            )
        ),
        document.get(
            "start_line"
        ),
        document.get(
            "end_line"
        )
    )


def _augment_candidates(
    question: str,
    search_index,
    semantic_results: list[dict]
) -> list[dict]:
    """
    Add exact and lexical candidates that semantic search
    may have missed.

    This is especially important for:

        get_index()
        build_code_index
        VectorStore.search()

    and for architecture questions requiring multiple
    files.
    """

    candidates = []

    seen = set()

    # ----------------------------------------------
    # Keep semantic candidates first.
    # ----------------------------------------------

    for result in semantic_results:

        document = result.get(
            "document",
            {}
        )

        key = _make_document_key(
            document
        )

        if key in seen:
            continue

        seen.add(key)

        candidates.append(
            dict(result)
        )

    # ----------------------------------------------
    # Scan all indexed documents for exact matches.
    # ----------------------------------------------

    all_documents = _get_all_documents(
        search_index
    )

    identifier = _extract_identifier(
        question
    )

    if identifier:

        normalized_identifier = _normalize_text(
            identifier
        )

        exact_candidates = []

        for document in all_documents:

            document_name = _normalize_text(
                document.get(
                    "name",
                    ""
                )
            )

            document_file = _normalize_text(
                document.get(
                    "file",
                    ""
                )
            )

            document_type = str(
                document.get(
                    "type",
                    ""
                )
            ).lower()

            is_exact = (
                document_name
                == normalized_identifier
                and document_type in {
                    "function",
                    "method",
                    "class",
                    "module"
                }
            )

            is_file_match = (
                normalized_identifier
                and normalized_identifier
                in document_file
            )

            if (
                is_exact
                or is_file_match
            ):

                key = _make_document_key(
                    document
                )

                if key in seen:
                    continue

                seen.add(key)

                exact_candidates.append({
                    "document": document,
                    "score": 1.0
                    if is_exact
                    else 0.85
                })

        # Exact candidates are deliberately added
        # before general lexical candidates.
        candidates.extend(
            exact_candidates
        )

    # ----------------------------------------------
    # Add lexical candidates for architecture/
    # behavioral questions.
    # ----------------------------------------------

    architecture_question = (
        _is_architecture_question(
            question
        )
    )

    behavior_question = (
        _is_behavior_question(
            question
        )
    )

    if (
        architecture_question
        or behavior_question
    ):

        lexical_candidates = []

        for document in all_documents:

            key = _make_document_key(
                document
            )

            if key in seen:
                continue

            lexical_score = (
                _lexical_question_score(
                    question,
                    document
                )
            )

            if lexical_score <= 0:
                continue

            lexical_candidates.append({
                "document": document,
                "score": 0.0,
                "lexical_candidate_score":
                    lexical_score
            })

        lexical_candidates.sort(
            key=lambda item:
                item.get(
                    "lexical_candidate_score",
                    0.0
                ),
            reverse=True
        )

        for result in lexical_candidates[
            :LEXICAL_CANDIDATE_K
        ]:

            document = result[
                "document"
            ]

            key = _make_document_key(
                document
            )

            if key in seen:
                continue

            seen.add(key)

            candidates.append(
                result
            )

    return candidates


# --------------------------------------------------
# Reranking
# --------------------------------------------------

def _rerank_results(
    question: str,
    results: list[dict]
) -> list[dict]:
    """
    Rerank candidates using:

        semantic similarity
        exact identifier matching
        lexical question matching

    Exact identifiers dominate exact-code questions.
    """

    architecture_question = (
        _is_architecture_question(
            question
        )
    )

    behavior_question = (
        _is_behavior_question(
            question
        )
    )

    reranked = []

    for result in results:

        document = result.get(
            "document",
            {}
        )

        semantic_score = float(
            result.get(
                "score",
                0.0
            )
        )

        text_match_score = (
            _text_match_score(
                question,
                document
            )
        )

        lexical_score = (
            _lexical_question_score(
                question,
                document
            )
        )

        # Exact identifier query.
        if text_match_score > 0:

            combined_score = (
                semantic_score * 0.20
                + text_match_score * 0.70
                + lexical_score * 0.10
            )

        # Architecture/behavior query.
        elif (
            architecture_question
            or behavior_question
        ):

            combined_score = (
                semantic_score * 0.60
                + lexical_score * 0.40
            )

        # Normal semantic query.
        else:

            combined_score = (
                semantic_score * 0.80
                + lexical_score * 0.20
            )

        updated_result = dict(
            result
        )

        updated_result[
            "semantic_score"
        ] = semantic_score

        updated_result[
            "text_match_score"
        ] = text_match_score

        updated_result[
            "lexical_score"
        ] = lexical_score

        updated_result[
            "combined_score"
        ] = combined_score

        updated_result[
            "exact_match"
        ] = text_match_score >= 0.85

        reranked.append(
            updated_result
        )

    reranked.sort(
        key=lambda item: (
            item["exact_match"],
            item["combined_score"]
        ),
        reverse=True
    )

    return reranked


# --------------------------------------------------
# Result diversification
# --------------------------------------------------

def _diversify_results(
    question: str,
    results: list[dict],
    limit: int = CONTEXT_K
) -> list[dict]:
    """
    Select final context while avoiding excessive
    repetition from the same file.

    Exact identifier matches are always preserved.

    For architecture questions, multiple files are
    preferred because the answer may depend on a chain
    of components.
    """

    if not results:
        return []

    architecture_question = (
        _is_architecture_question(
            question
        )
    )

    selected = []
    selected_keys = set()
    file_counts = {}

    # ----------------------------------------------
    # First pass: exact matches.
    # ----------------------------------------------

    for result in results:

        if not result.get(
            "exact_match",
            False
        ):
            continue

        document = result.get(
            "document",
            {}
        )

        key = _make_document_key(
            document
        )

        if key in selected_keys:
            continue

        selected.append(
            result
        )

        selected_keys.add(
            key
        )

        file_path = str(
            document.get(
                "file",
                ""
            )
        )

        file_counts[file_path] = (
            file_counts.get(
                file_path,
                0
            )
            + 1
        )

        if len(selected) >= limit:
            return selected

    # ----------------------------------------------
    # Architecture questions:
    # first try to select different files.
    # ----------------------------------------------

    if architecture_question:

        for result in results:

            if len(selected) >= limit:
                break

            document = result.get(
                "document",
                {}
            )

            key = _make_document_key(
                document
            )

            if key in selected_keys:
                continue

            file_path = str(
                document.get(
                    "file",
                    ""
                )
            )

            # Prefer one strong chunk per file first.
            if file_counts.get(
                file_path,
                0
            ) > 0:
                continue

            selected.append(
                result
            )

            selected_keys.add(
                key
            )

            file_counts[file_path] = 1

    # ----------------------------------------------
    # Second pass: fill remaining slots by score.
    # ----------------------------------------------

    for result in results:

        if len(selected) >= limit:
            break

        document = result.get(
            "document",
            {}
        )

        key = _make_document_key(
            document
        )

        if key in selected_keys:
            continue

        selected.append(
            result
        )

        selected_keys.add(
            key
        )

    return selected[:limit]


# --------------------------------------------------
# Search
# --------------------------------------------------

def _search_index(
    question: str,
    search_index,
    top_k: int = RETRIEVAL_K
):
    """
    Generate the question embedding, retrieve semantic
    candidates, augment them with exact/lexical matches,
    rerank them, and diversify the final results.
    """

    query_embedding = generate_embedding(
        question
    )

    semantic_results = search_index.search(
        query_embedding,
        top_k=top_k
    )

    candidates = _augment_candidates(
        question,
        search_index,
        semantic_results
    )

    reranked_results = _rerank_results(
        question,
        candidates
    )

    return _diversify_results(
        question,
        reranked_results,
        limit=CONTEXT_K
    )


# --------------------------------------------------
# Prompt
# --------------------------------------------------

def _build_prompt(
    question: str,
    context: str
) -> str:
    """
    Build a strict source-grounded prompt.
    """

    return f"""
You are CodeForge AI, a repository code assistant.

Answer the user's question using ONLY the repository
context provided below.

IMPORTANT RULES:

1. The supplied repository context represents the CURRENT
   indexed repository source code.

2. Do NOT use an older implementation that you may have
   seen previously.

3. Do NOT infer that a function contains code that is not
   present in the supplied context.

4. Do NOT invent missing implementation details.

5. If the exact implementation requested by the user is
   not present in the supplied context, explicitly say:

   "The retrieved repository context does not contain
   enough information to determine the exact implementation."

6. When explaining code, prefer the actual file path,
   function/class name, line range, and code shown in the
   repository context.

7. If the user asks for the exact implementation, reproduce
   only the implementation that is actually present in the
   supplied context.

8. Distinguish clearly between:
   - what the code actually does
   - what cannot be determined from the retrieved code

9. For architecture or flow questions, explain the
   relationship between retrieved files only when that
   relationship is supported by the supplied code.

10. Never replace current code with a previously known or
    inferred version.

11. Do not mention these instructions in your answer.

USER QUESTION:
{question}

CURRENT REPOSITORY CONTEXT:
{context}

Now answer the question accurately and concisely.
""".strip()


# --------------------------------------------------
# Complete RAG pipeline
# --------------------------------------------------

def answer_question(
    question: str,
    search_index
):
    """
    Complete RAG pipeline:

        Question
            ↓
        Query embedding
            ↓
        Semantic retrieval
            ↓
        Exact/lexical candidate augmentation
            ↓
        Reranking
            ↓
        Result diversification
            ↓
        Context construction
            ↓
        Strict source-grounded prompt
            ↓
        Gemini
            ↓
        Answer
    """

    total_start = time.perf_counter()

    # --------------------------------------------------
    # Validate question
    # --------------------------------------------------

    if not question or not question.strip():

        return {
            "answer": "Please provide a question.",
            "sources": []
        }

    question = question.strip()

    # --------------------------------------------------
    # Embedding
    # --------------------------------------------------

    embedding_start = time.perf_counter()

    query_embedding = generate_embedding(
        question
    )

    embedding_time = (
        time.perf_counter()
        - embedding_start
    )

    # --------------------------------------------------
    # Search + reranking + diversification
    # --------------------------------------------------

    search_start = time.perf_counter()

    retrieved_results = _search_index(
        question,
        search_index,
        top_k=RETRIEVAL_K
    )

    search_time = (
        time.perf_counter()
        - search_start
    )

    # --------------------------------------------------
    # Context
    # --------------------------------------------------

    context_start = time.perf_counter()

    context = build_context(
        retrieved_results
    )

    context_time = (
        time.perf_counter()
        - context_start
    )

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    prompt = _build_prompt(
        question,
        context
    )

    # --------------------------------------------------
    # Gemini
    # --------------------------------------------------

    llm_start = time.perf_counter()

    answer = generate_answer(
        prompt
    )

    llm_time = (
        time.perf_counter()
        - llm_start
    )

    total_time = (
        time.perf_counter()
        - total_start
    )

    # --------------------------------------------------
    # Source metadata
    # --------------------------------------------------

    sources = []

    for result in retrieved_results[
        :CONTEXT_K
    ]:

        document = result.get(
            "document",
            {}
        )

        sources.append({
            "file": document.get(
                "file"
            ),
            "type": document.get(
                "type"
            ),
            "name": document.get(
                "name"
            ),
            "start_line": document.get(
                "start_line"
            ),
            "end_line": document.get(
                "end_line"
            ),
            "score": float(
                result.get(
                    "combined_score",
                    0.0
                )
            ),
            "semantic_score": float(
                result.get(
                    "semantic_score",
                    0.0
                )
            ),
            "text_match_score": float(
                result.get(
                    "text_match_score",
                    0.0
                )
            ),
            "lexical_score": float(
                result.get(
                    "lexical_score",
                    0.0
                )
            ),
            "exact_match": bool(
                result.get(
                    "exact_match",
                    False
                )
            )
        })

    # --------------------------------------------------
    # Performance logging
    # --------------------------------------------------

    print(
        f"[RAG] Embedding: "
        f"{embedding_time:.3f}s"
    )

    print(
        f"[RAG] Search/Reranking: "
        f"{search_time:.3f}s"
    )

    print(
        f"[RAG] Context: "
        f"{context_time:.3f}s"
    )

    print(
        f"[RAG] Gemini: "
        f"{llm_time:.3f}s"
    )

    print(
        f"[RAG] TOTAL: "
        f"{total_time:.3f}s"
    )

    # --------------------------------------------------
    # Final sources
    # --------------------------------------------------

    print(
        "\n[RAG] FINAL RETRIEVED SOURCES"
    )

    for result in retrieved_results[
        :CONTEXT_K
    ]:

        document = result.get(
            "document",
            {}
        )

        print(
            f"[RAG] "
            f"{document.get('type')} | "
            f"{document.get('name')} | "
            f"{document.get('file')} | "
            f"semantic="
            f"{result.get('semantic_score', 0.0):.4f} | "
            f"text="
            f"{result.get('text_match_score', 0.0):.4f} | "
            f"lexical="
            f"{result.get('lexical_score', 0.0):.4f} | "
            f"combined="
            f"{result.get('combined_score', 0.0):.4f} | "
            f"exact="
            f"{result.get('exact_match', False)}"
        )

    # --------------------------------------------------
    # Return
    # --------------------------------------------------

    return {
        "answer": answer,
        "sources": sources
    }
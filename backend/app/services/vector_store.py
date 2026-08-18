import re
import numpy as np

from app.services.hnsw_index import HNSWIndex


class VectorStore:

    def __init__(self):

        self.documents = []
        self.embeddings = []

        self.hnsw = HNSWIndex(
            max_connections=8,
            max_layers=4
        )

    # ==================================================
    # Add document
    # ==================================================

    def add(
        self,
        document: dict,
        embedding: list[float]
    ):

        self.documents.append(
            document
        )

        self.embeddings.append(
            embedding
        )

        self.hnsw.add(
            embedding,
            document
        )

    # ==================================================
    # Cosine similarity
    # ==================================================

    def cosine_similarity(
        self,
        vector_a,
        vector_b
    ) -> float:

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
            np.dot(a, b)
            / denominator
        )

    # ==================================================
    # Tokenization
    # ==================================================

    @staticmethod
    def _tokens(
        text: str
    ) -> set[str]:

        if not text:
            return set()

        return {
            token.lower()
            for token in re.findall(
                r"[A-Za-z_][A-Za-z0-9_]*",
                text
            )
            if len(token) > 2
        }

    # ==================================================
    # Detect architecture questions
    # ==================================================

    @staticmethod
    def _is_architecture_question(
        query: str
    ) -> bool:

        query_lower = (
            query.lower()
            if query
            else ""
        )

        architecture_phrases = {
            "how does",
            "how do",
            "how does a question",
            "travel from",
            "work together",
            "data flow",
            "request flow",
            "request path",
            "architecture",
            "pipeline",
            "frontend",
            "backend",
            "gemini",
            "api",
            "route",
            "service",
            "services",
            "communicate",
            "communication",
            "flow"
        }

        return any(
            phrase in query_lower
            for phrase in architecture_phrases
        )

    # ==================================================
    # Architecture path score
    # ==================================================

    @staticmethod
    def _architecture_path_score(
        query: str,
        document: dict
    ) -> float:

        if not query:
            return 0.0

        if not VectorStore._is_architecture_question(
            query
        ):
            return 0.0

        query_lower = query.lower()

        file_path = str(
            document.get(
                "file",
                ""
            )
        ).replace(
            "\\",
            "/"
        ).lower()

        name = str(
            document.get(
                "name",
                ""
            )
        ).lower()

        document_type = str(
            document.get(
                "type",
                ""
            )
        ).lower()

        score = 0.0

        # --------------------------------------------------
        # Frontend files
        # --------------------------------------------------

        if (
            "frontend/" in file_path
            or "/frontend/" in file_path
        ):

            if "frontend" in query_lower:
                score += 0.45

            if (
                document_type
                in {
                    "component",
                    "function",
                    "source_file"
                }
            ):
                score += 0.10

        # --------------------------------------------------
        # Question route
        # --------------------------------------------------

        if (
            name == "ask_question"
            or "question.py" in file_path
        ):

            if any(
                word in query_lower
                for word in {
                    "question",
                    "request",
                    "frontend",
                    "flow",
                    "api"
                }
            ):
                score += 0.35

        # --------------------------------------------------
        # RAG service
        # --------------------------------------------------

        if (
            "rag_service.py" in file_path
            or name in {
                "answer_question",
                "build_context",
                "_build_prompt"
            }
        ):

            if any(
                word in query_lower
                for word in {
                    "rag",
                    "question",
                    "flow",
                    "pipeline",
                    "context",
                    "gemini",
                    "service"
                }
            ):
                score += 0.35

        # --------------------------------------------------
        # Gemini / LLM service
        # --------------------------------------------------

        if (
            "llm_service.py" in file_path
            or name == "generate_answer"
        ):

            if any(
                word in query_lower
                for word in {
                    "gemini",
                    "llm",
                    "model",
                    "generation",
                    "frontend",
                    "flow"
                }
            ):
                score += 0.45

        # --------------------------------------------------
        # Backend API route
        # --------------------------------------------------

        if (
            "/routes/" in file_path
            or "\\routes\\" in file_path
        ):

            if any(
                word in query_lower
                for word in {
                    "frontend",
                    "backend",
                    "api",
                    "request",
                    "route",
                    "question"
                }
            ):
                score += 0.25

        # --------------------------------------------------
        # Main application
        # --------------------------------------------------

        if (
            file_path.endswith(
                "/main.py"
            )
            or name == "main.py"
        ):

            if any(
                word in query_lower
                for word in {
                    "backend",
                    "api",
                    "route",
                    "request",
                    "application"
                }
            ):
                score += 0.15

        return min(
            score,
            1.0
        )

    # ==================================================
    # Text matching
    # ==================================================

    def text_match_score(
        self,
        query: str,
        document: dict
    ) -> float:

        if not query:
            return 0.0

        query_lower = query.lower()

        file_path = str(
            document.get(
                "file",
                ""
            )
        ).lower()

        name = str(
            document.get(
                "name",
                ""
            )
        ).lower()

        code = str(
            document.get(
                "code",
                ""
            )
        ).lower()

        document_type = str(
            document.get(
                "type",
                ""
            )
        ).lower()

        score = 0.0

        # --------------------------------------------------
        # Normalize path
        # --------------------------------------------------

        normalized_path = file_path.replace(
            "\\",
            "/"
        )

        file_name = (
            normalized_path
            .split("/")[-1]
        )

        # --------------------------------------------------
        # Exact filename
        # --------------------------------------------------

        if (
            file_name
            and file_name in query_lower
        ):

            score += 0.40

        # --------------------------------------------------
        # Filename without extension
        # --------------------------------------------------

        file_stem = (
            file_name.rsplit(
                ".",
                1
            )[0]
        )

        if (
            file_stem
            and len(file_stem) > 3
            and file_stem in query_lower
        ):

            score += 0.20

        # --------------------------------------------------
        # Exact function / class / component
        # --------------------------------------------------

        if (
            name
            and len(name) > 2
            and name in query_lower
        ):

            score += 0.30

        # --------------------------------------------------
        # Architecture keywords
        # --------------------------------------------------

        architecture_words = {
            "architecture",
            "flow",
            "service",
            "services",
            "backend",
            "frontend",
            "relationship",
            "relationships",
            "connected",
            "connection",
            "pipeline",
            "component",
            "components",
            "work",
            "together",
            "analysis",
            "repository",
            "request",
            "response",
            "route",
            "routes",
            "api",
            "gemini",
            "llm",
            "model",
            "question"
        }

        query_words = self._tokens(
            query_lower
        )

        architecture_overlap = (
            query_words
            & architecture_words
        )

        # --------------------------------------------------
        # Module-level chunks
        # --------------------------------------------------

        if (
            architecture_overlap
            and document_type == "module"
        ):

            score += 0.15

        # --------------------------------------------------
        # Frontend component boost
        # --------------------------------------------------

        if (
            architecture_overlap
            and (
                "frontend/" in normalized_path
                or "/frontend/" in normalized_path
            )
        ):

            score += 0.20

        # --------------------------------------------------
        # Gemini service boost
        # --------------------------------------------------

        if (
            "gemini" in query_words
            and (
                "llm_service.py" in normalized_path
                or name == "generate_answer"
            )
        ):

            score += 0.25

        # --------------------------------------------------
        # RAG service boost
        # --------------------------------------------------

        if (
            (
                "rag" in query_words
                or "pipeline" in query_words
                or "flow" in query_words
                or "question" in query_words
            )
            and (
                "rag_service.py" in normalized_path
                or name == "answer_question"
            )
        ):

            score += 0.20

        # --------------------------------------------------
        # Question route boost
        # --------------------------------------------------

        if (
            (
                "question" in query_words
                or "request" in query_words
                or "api" in query_words
                or "frontend" in query_words
            )
            and (
                "question.py" in normalized_path
                or name == "ask_question"
            )
        ):

            score += 0.20

        # --------------------------------------------------
        # General keyword overlap
        # --------------------------------------------------

        if query_words:

            document_text = (
                f"{file_path} "
                f"{name} "
                f"{document_type} "
                f"{code}"
            )

            document_words = self._tokens(
                document_text
            )

            overlap = (
                query_words
                & document_words
            )

            useful_overlap = [
                word
                for word in overlap
                if len(word) > 3
            ]

            if useful_overlap:

                score += min(
                    len(useful_overlap)
                    * 0.03,
                    0.20
                )

        return min(
            score,
            1.0
        )

    # ==================================================
    # Exact symbol / file matching
    # ==================================================

    @staticmethod
    def _exact_match_type(
        query: str,
        document: dict
    ) -> str:

        """
        Determine whether the query contains an exact
        repository symbol and/or filename.

        Returns:

            "function_and_file"
            "symbol"
            "file"
            ""
        """

        if not query:
            return ""

        query_lower = query.lower()

        file_path = str(
            document.get(
                "file",
                ""
            )
        ).replace(
            "\\",
            "/"
        ).lower()

        file_name = (
            file_path
            .split("/")[-1]
        )

        name = str(
            document.get(
                "name",
                ""
            )
        ).strip().lower()

        document_type = str(
            document.get(
                "type",
                ""
            )
        ).lower()

        exact_name = (
            bool(name)
            and len(name) > 2
            and name in query_lower
        )

        exact_file = (
            bool(file_name)
            and file_name in query_lower
        )

        # Strongest case:
        # exact symbol + exact file.
        if (
            exact_name
            and exact_file
            and document_type in {
                "function",
                "method",
                "class",
                "component"
            }
        ):
            return "function_and_file"

        # Exact symbol.
        if (
            exact_name
            and document_type in {
                "function",
                "method",
                "class",
                "component"
            }
        ):
            return "symbol"

        # Exact file.
        if exact_file:
            return "file"

        return ""

    # ==================================================
    # Search
    # ==================================================

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        min_score: float = 0.20,
        query_text: str = ""
    ):

        if not self.documents:
            return []

        # --------------------------------------------------
        # Retrieve a large semantic candidate pool.
        # --------------------------------------------------

        candidate_count = min(
            max(
                top_k * 8,
                40
            ),
            len(self.documents)
        )

        semantic_results = self.hnsw.search(
            query_embedding,
            top_k=candidate_count
        )

        ranked_results = []

        # --------------------------------------------------
        # Score semantic candidates.
        # --------------------------------------------------

        for result in semantic_results:

            document = result[
                "document"
            ]

            semantic_score = float(
                result["score"]
            )

            text_score = (
                self.text_match_score(
                    query_text,
                    document
                )
            )

            architecture_score = (
                self._architecture_path_score(
                    query_text,
                    document
                )
            )

            # --------------------------------------------------
            # Base hybrid score
            # --------------------------------------------------

            combined_score = (
                semantic_score * 0.55
                + text_score * 0.25
                + architecture_score * 0.20
            )

            # --------------------------------------------------
            # Exact symbol/file priority
            #
            # This is the important fix.
            # --------------------------------------------------

            exact_match = (
                self._exact_match_type(
                    query_text,
                    document
                )
            )

            if exact_match == "function_and_file":

                combined_score = max(
                    combined_score,
                    1.0
                )

            elif exact_match == "symbol":

                combined_score = max(
                    combined_score,
                    0.95
                )

            elif exact_match == "file":

                combined_score = max(
                    combined_score,
                    0.85
                )

            ranked_results.append(
                {
                    "document": document,
                    "score": combined_score,
                    "semantic_score": semantic_score,
                    "text_score": text_score,
                    "architecture_score": architecture_score,
                    "exact_match": exact_match
                }
            )

        # --------------------------------------------------
        # Explicit filename / symbol matches.
        #
        # Scan the complete document list so an exact
        # function/file match is not lost because HNSW
        # failed to return it in the semantic candidate pool.
        # --------------------------------------------------

        if query_text:

            for index, document in enumerate(
                self.documents
            ):

                exact_match = (
                    self._exact_match_type(
                        query_text,
                        document
                    )
                )

                if not exact_match:
                    continue

                already_added = any(
                    item["document"] is document
                    for item in ranked_results
                )

                semantic_score = (
                    self.cosine_similarity(
                        query_embedding,
                        self.embeddings[index]
                    )
                )

                text_score = (
                    self.text_match_score(
                        query_text,
                        document
                    )
                )

                architecture_score = (
                    self._architecture_path_score(
                        query_text,
                        document
                    )
                )

                combined_score = (
                    semantic_score * 0.55
                    + text_score * 0.25
                    + architecture_score * 0.20
                )

                # Strong deterministic priority.
                if exact_match == "function_and_file":

                    combined_score = 1.0

                elif exact_match == "symbol":

                    combined_score = max(
                        combined_score,
                        0.95
                    )

                elif exact_match == "file":

                    combined_score = max(
                        combined_score,
                        0.85
                    )

                exact_result = {
                    "document": document,
                    "score": combined_score,
                    "semantic_score": semantic_score,
                    "text_score": text_score,
                    "architecture_score": architecture_score,
                    "exact_match": exact_match
                }

                if already_added:

                    # Update the existing result instead
                    # of adding a duplicate.
                    for item in ranked_results:

                        if item["document"] is document:

                            item.update(
                                exact_result
                            )

                            break

                else:

                    ranked_results.append(
                        exact_result
                    )

        # --------------------------------------------------
        # Architecture questions:
        #
        # Ensure important architectural components
        # are represented in the candidate list.
        # --------------------------------------------------

        if self._is_architecture_question(
            query_text
        ):

            architecture_documents = []

            for index, document in enumerate(
                self.documents
            ):

                architecture_score = (
                    self._architecture_path_score(
                        query_text,
                        document
                    )
                )

                if architecture_score <= 0:
                    continue

                already_added = any(
                    item["document"] is document
                    for item in ranked_results
                )

                if already_added:
                    continue

                semantic_score = (
                    self.cosine_similarity(
                        query_embedding,
                        self.embeddings[index]
                    )
                )

                text_score = (
                    self.text_match_score(
                        query_text,
                        document
                    )
                )

                combined_score = (
                    semantic_score * 0.55
                    + text_score * 0.25
                    + architecture_score * 0.20
                )

                exact_match = (
                    self._exact_match_type(
                        query_text,
                        document
                    )
                )

                if exact_match == "function_and_file":

                    combined_score = 1.0

                elif exact_match == "symbol":

                    combined_score = max(
                        combined_score,
                        0.95
                    )

                elif exact_match == "file":

                    combined_score = max(
                        combined_score,
                        0.85
                    )

                architecture_documents.append(
                    {
                        "document": document,
                        "score": combined_score,
                        "semantic_score": semantic_score,
                        "text_score": text_score,
                        "architecture_score": architecture_score,
                        "exact_match": exact_match
                    }
                )

            ranked_results.extend(
                architecture_documents
            )

        # --------------------------------------------------
        # Sort by final hybrid score.
        # --------------------------------------------------

        ranked_results.sort(
            key=lambda item: item[
                "score"
            ],
            reverse=True
        )

        # --------------------------------------------------
        # Remove weak results.
        # --------------------------------------------------

        filtered_results = [
            result
            for result in ranked_results
            if result["score"] >= min_score
        ]

        # --------------------------------------------------
        # Architecture questions need diversity.
        #
        # Avoid sending eight chunks from the same file
        # when the question asks about system flow.
        # --------------------------------------------------

        if self._is_architecture_question(
            query_text
        ):

            diversified = []
            used_files = set()

            # --------------------------------------------------
            # First pass:
            # exact/high-confidence results first.
            # --------------------------------------------------

            exact_results = [
                result
                for result in filtered_results
                if result.get(
                    "exact_match"
                ) in {
                    "function_and_file",
                    "symbol",
                    "file"
                }
            ]

            for result in exact_results:

                document = result[
                    "document"
                ]

                file_path = str(
                    document.get(
                        "file",
                        ""
                    )
                )

                if file_path in used_files:
                    continue

                used_files.add(
                    file_path
                )

                diversified.append(
                    result
                )

                if len(diversified) >= top_k:
                    break

            # --------------------------------------------------
            # Second pass:
            # one strong result per file.
            # --------------------------------------------------

            if len(diversified) < top_k:

                for result in filtered_results:

                    if result in diversified:
                        continue

                    document = result[
                        "document"
                    ]

                    file_path = str(
                        document.get(
                            "file",
                            ""
                        )
                    )

                    if file_path in used_files:
                        continue

                    used_files.add(
                        file_path
                    )

                    diversified.append(
                        result
                    )

                    if len(diversified) >= top_k:
                        break

            # --------------------------------------------------
            # Third pass:
            # fill remaining positions.
            # --------------------------------------------------

            if len(diversified) < top_k:

                for result in filtered_results:

                    if result in diversified:
                        continue

                    diversified.append(
                        result
                    )

                    if len(diversified) >= top_k:
                        break

            return diversified[
                :top_k
            ]

        return filtered_results[
            :top_k
        ]
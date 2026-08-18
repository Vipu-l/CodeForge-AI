import os
import re

from app.services.code_parser import parse_python_file
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import VectorStore


# ==================================================
# Supported source-code extensions
# ==================================================

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".php",
    ".rb",
}


# ==================================================
# Directories that should not be indexed
# ==================================================

IGNORED_DIRECTORIES = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
}


# ==================================================
# Files that should not be indexed
# ==================================================

IGNORED_FILE_PREFIXES = (
    "test_",
    "benchmark_",
)

IGNORED_FILE_SUFFIXES = (
    "_test.py",
    "_test.js",
    "_test.jsx",
    "_test.ts",
    "_test.tsx",
)


# ==================================================
# Generic chunk size
# ==================================================

MAX_GENERIC_CHUNK_LINES = 200


# ==================================================
# Standard chunk creation
# ==================================================

def create_chunk(
    file_path: str,
    chunk_type: str,
    name: str,
    start_line: int,
    end_line: int,
    code: str
) -> dict:
    """
    Create a standardized code chunk.

    Metadata is used by semantic retrieval and source display.
    """

    return {
        "file": file_path,
        "type": chunk_type,
        "name": name,
        "start_line": start_line,
        "end_line": end_line,
        "code": code,
    }


# ==================================================
# File filtering
# ==================================================

def should_ignore_file(filename: str) -> bool:
    """
    Return True for test and benchmark files.

    These files usually contain validation or experimental
    code rather than the application's main implementation.
    """

    filename_lower = filename.lower()

    if filename_lower.startswith(
        IGNORED_FILE_PREFIXES
    ):
        return True

    if filename_lower.endswith(
        IGNORED_FILE_SUFFIXES
    ):
        return True

    return False


# ==================================================
# JavaScript / React / TypeScript parser
# ==================================================

def parse_javascript_file(
    file_path: str
) -> list[dict]:
    """
    Lightweight parser for JavaScript, JSX,
    TypeScript and TSX files.

    No additional parser dependency is required.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        source = file.read()

    lines = source.splitlines()

    chunks = []

    # --------------------------------------------------
    # Function declarations
    # --------------------------------------------------

    function_pattern = re.compile(
        r"^\s*(?:export\s+)?"
        r"(?:async\s+)?function\s+"
        r"([A-Za-z_$][\w$]*)\s*\("
    )

    # --------------------------------------------------
    # Arrow functions
    # --------------------------------------------------

    arrow_pattern = re.compile(
        r"^\s*(?:const|let|var)\s+"
        r"([A-Za-z_$][\w$]*)\s*="
        r"\s*(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)"
        r"\s*=>"
    )

    # --------------------------------------------------
    # React components
    # --------------------------------------------------

    component_pattern = re.compile(
        r"^\s*(?:export\s+)?"
        r"(?:default\s+)?"
        r"(?:function\s+)?"
        r"([A-Z][A-Za-z0-9_$]*)\s*(?:=|\()"
    )

    function_starts = []

    for index, line in enumerate(
        lines,
        start=1
    ):

        function_match = function_pattern.match(
            line
        )

        arrow_match = arrow_pattern.match(
            line
        )

        component_match = component_pattern.match(
            line
        )

        if function_match:

            function_starts.append(
                (
                    index,
                    function_match.group(1),
                    "function"
                )
            )

        elif arrow_match:

            function_starts.append(
                (
                    index,
                    arrow_match.group(1),
                    "function"
                )
            )

        elif component_match:

            name = component_match.group(1)

            if name not in {
                "If",
                "For",
                "While",
                "Switch"
            }:

                function_starts.append(
                    (
                        index,
                        name,
                        "component"
                    )
                )

    # --------------------------------------------------
    # Extract function/component blocks
    # --------------------------------------------------

    for position, (
        start_line,
        name,
        chunk_type
    ) in enumerate(function_starts):

        end_line = len(lines)

        if position + 1 < len(function_starts):

            next_start = function_starts[
                position + 1
            ][0]

            end_line = next_start - 1

        brace_count = 0
        found_opening_brace = False
        calculated_end = start_line

        for line_number in range(
            start_line,
            len(lines) + 1
        ):

            current_line = lines[
                line_number - 1
            ]

            opening = current_line.count("{")
            closing = current_line.count("}")

            if opening > 0:

                found_opening_brace = True

            if found_opening_brace:

                brace_count += opening
                brace_count -= closing

                if brace_count <= 0:

                    calculated_end = line_number

                    break

        if calculated_end >= start_line:

            end_line = min(
                end_line,
                calculated_end
            )

        code = "\n".join(
            lines[
                start_line - 1:end_line
            ]
        )

        if code.strip():

            chunks.append(
                create_chunk(
                    file_path,
                    chunk_type,
                    name,
                    start_line,
                    end_line,
                    code
                )
            )

    # --------------------------------------------------
    # Group imports into ONE chunk
    # --------------------------------------------------

    import_lines = []

    for index, line in enumerate(
        lines,
        start=1
    ):

        stripped = line.strip()

        if (
            stripped.startswith("import ")
            or (
                stripped.startswith("export ")
                and " from " in stripped
            )
        ):

            import_lines.append(index)

    if import_lines:

        start_line = min(import_lines)
        end_line = max(import_lines)

        import_code = "\n".join(
            lines[
                start_line - 1:end_line
            ]
        )

        chunks.append(
            create_chunk(
                file_path,
                "imports",
                "imports",
                start_line,
                end_line,
                import_code
            )
        )

    # --------------------------------------------------
    # Fallback
    # --------------------------------------------------

    if not chunks and source.strip():

        chunks.append(
            create_chunk(
                file_path,
                "source_file",
                os.path.basename(file_path),
                1,
                len(lines),
                source
            )
        )

    return chunks


# ==================================================
# Generic source parser
# ==================================================

def parse_generic_file(
    file_path: str
) -> list[dict]:
    """
    Parse supported languages without a dedicated parser.

    Small files become one chunk.

    Large files are split into focused line-based chunks.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()

    if not content.strip():

        return []

    lines = content.splitlines()

    # --------------------------------------------------
    # Small file
    # --------------------------------------------------

    if len(lines) <= MAX_GENERIC_CHUNK_LINES:

        return [
            create_chunk(
                file_path,
                "source_file",
                os.path.basename(file_path),
                1,
                len(lines),
                content
            )
        ]

    # --------------------------------------------------
    # Large file
    # --------------------------------------------------

    chunks = []

    for start_index in range(
        0,
        len(lines),
        MAX_GENERIC_CHUNK_LINES
    ):

        end_index = min(
            start_index + MAX_GENERIC_CHUNK_LINES,
            len(lines)
        )

        chunk_lines = lines[
            start_index:end_index
        ]

        code = "\n".join(
            chunk_lines
        )

        if not code.strip():

            continue

        chunks.append(
            create_chunk(
                file_path,
                "source_chunk",
                (
                    f"{os.path.basename(file_path)}:"
                    f"{start_index + 1}-"
                    f"{end_index}"
                ),
                start_index + 1,
                end_index,
                code
            )
        )

    return chunks


# ==================================================
# Build semantic code index
# ==================================================

def build_code_index(
    repository_path: str
) -> VectorStore:
    """
    Build a semantic vector index for a repository.

    Pipeline:

        Repository
            ↓
        File discovery
            ↓
        File filtering
            ↓
        Language-aware parsing
            ↓
        Semantic chunks
            ↓
        Batch embeddings
            ↓
        VectorStore
    """

    store = VectorStore()

    all_chunks = []

    # --------------------------------------------------
    # Discover repository files
    # --------------------------------------------------

    for root, directories, files in os.walk(
        repository_path
    ):

        # Remove ignored directories in-place.
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in files:

            # --------------------------------------------------
            # Skip test and benchmark files
            # --------------------------------------------------

            if should_ignore_file(filename):

                continue

            # --------------------------------------------------
            # Check extension
            # --------------------------------------------------

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in SUPPORTED_EXTENSIONS:

                continue

            file_path = os.path.join(
                root,
                filename
            )

            try:

                # --------------------------------------------------
                # Python
                # --------------------------------------------------

                if extension == ".py":

                    chunks = parse_python_file(
                        file_path
                    )

                # --------------------------------------------------
                # JavaScript / React / TypeScript
                # --------------------------------------------------

                elif extension in {
                    ".js",
                    ".jsx",
                    ".ts",
                    ".tsx"
                }:

                    chunks = parse_javascript_file(
                        file_path
                    )

                # --------------------------------------------------
                # Other languages
                # --------------------------------------------------

                else:

                    chunks = parse_generic_file(
                        file_path
                    )

                all_chunks.extend(
                    chunks
                )

            except (
                SyntaxError,
                UnicodeDecodeError,
                OSError
            ):

                # One invalid/unreadable file must not
                # stop the entire repository indexing process.

                continue

    # --------------------------------------------------
    # No chunks
    # --------------------------------------------------

    if not all_chunks:

        return store

    # --------------------------------------------------
    # Prepare semantic embedding text
    # --------------------------------------------------

    embedding_texts = []

    for chunk in all_chunks:

        text = (
            f"Repository code chunk\n"
            f"File: {chunk['file']}\n"
            f"Type: {chunk['type']}\n"
            f"Name: {chunk['name']}\n"
            f"Lines: "
            f"{chunk['start_line']}-"
            f"{chunk['end_line']}\n"
            f"Code:\n"
            f"{chunk['code']}"
        )

        embedding_texts.append(
            text
        )

    # --------------------------------------------------
    # Generate embeddings in batches
    # --------------------------------------------------

    embeddings = generate_embeddings(
        embedding_texts,
        batch_size=32
    )

    # --------------------------------------------------
    # Store chunks + embeddings
    # --------------------------------------------------

    for chunk, embedding in zip(
        all_chunks,
        embeddings
    ):

        store.add(
            chunk,
            embedding
        )

    return store
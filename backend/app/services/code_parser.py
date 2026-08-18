import ast
import os


def _get_code(lines: list[str], start_line: int, end_line: int) -> str:
    """Return source code for the requested line range."""
    return "\n".join(
        lines[start_line - 1:end_line]
    )


def _create_chunk(
    file_path: str,
    chunk_type: str,
    name: str,
    start_line: int,
    end_line: int,
    code: str
) -> dict:
    """Create a standardized code chunk."""

    return {
        "file": file_path,
        "type": chunk_type,
        "name": name,
        "start_line": start_line,
        "end_line": end_line,
        "code": code,
    }


def parse_python_file(file_path: str) -> list[dict]:
    """
    Parse a Python file into useful semantic code chunks.

    Chunks produced:

    1. One module-summary chunk
    2. One grouped import chunk
    3. Top-level function chunks
    4. Class chunks
    5. Class method chunks

    Nested functions are intentionally not indexed separately because
    they usually provide little value compared with their parent function.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8-sig"
    ) as file:

        source_code = file.read()

    tree = ast.parse(source_code)

    lines = source_code.splitlines()

    chunks = []

    imports = []
    functions = []
    classes = []

    # --------------------------------------------------
    # Collect module-level information
    # --------------------------------------------------

    for node in tree.body:

        if isinstance(
            node,
            (ast.Import, ast.ImportFrom)
        ):
            imports.append(
                ast.unparse(node)
            )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):
            functions.append(
                node.name
            )

        elif isinstance(
            node,
            ast.ClassDef
        ):
            classes.append(
                node.name
            )

    # --------------------------------------------------
    # Module summary
    # --------------------------------------------------

    module_summary = [
        f"File: {file_path}"
    ]

    if imports:

        module_summary.append(
            "\nImports:\n"
            + "\n".join(
                f"- {item}"
                for item in imports
            )
        )

    if functions:

        module_summary.append(
            "\nFunctions:\n"
            + "\n".join(
                f"- {item}"
                for item in functions
            )
        )

    if classes:

        module_summary.append(
            "\nClasses:\n"
            + "\n".join(
                f"- {item}"
                for item in classes
            )
        )

    chunks.append(
        _create_chunk(
            file_path=file_path,
            chunk_type="module",
            name=os.path.basename(file_path),
            start_line=1,
            end_line=len(lines),
            code="\n".join(module_summary)
        )
    )

    # --------------------------------------------------
    # Group imports into ONE chunk
    # --------------------------------------------------

    if imports:

        import_nodes = [
            node
            for node in tree.body
            if isinstance(
                node,
                (ast.Import, ast.ImportFrom)
            )
        ]

        if import_nodes:

            start_line = min(
                node.lineno
                for node in import_nodes
            )

            end_line = max(
                node.end_lineno
                for node in import_nodes
            )

            import_code = "\n".join(
                ast.unparse(node)
                for node in import_nodes
            )

            chunks.append(
                _create_chunk(
                    file_path=file_path,
                    chunk_type="imports",
                    name="imports",
                    start_line=start_line,
                    end_line=end_line,
                    code=import_code
                )
            )

    # --------------------------------------------------
    # Top-level functions
    # --------------------------------------------------

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):

            code = _get_code(
                lines,
                node.lineno,
                node.end_lineno
            )

            chunks.append(
                _create_chunk(
                    file_path=file_path,
                    chunk_type="function",
                    name=node.name,
                    start_line=node.lineno,
                    end_line=node.end_lineno,
                    code=code
                )
            )

    # --------------------------------------------------
    # Classes and their methods
    # --------------------------------------------------

    for node in tree.body:

        if not isinstance(
            node,
            ast.ClassDef
        ):
            continue

        # ----------------------------------------------
        # Class chunk
        # ----------------------------------------------

        class_code = _get_code(
            lines,
            node.lineno,
            node.end_lineno
        )

        chunks.append(
            _create_chunk(
                file_path=file_path,
                chunk_type="class",
                name=node.name,
                start_line=node.lineno,
                end_line=node.end_lineno,
                code=class_code
            )
        )

        # ----------------------------------------------
        # Class methods
        # ----------------------------------------------

        for child in node.body:

            if not isinstance(
                child,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                continue

            method_code = _get_code(
                lines,
                child.lineno,
                child.end_lineno
            )

            chunks.append(
                _create_chunk(
                    file_path=file_path,
                    chunk_type="method",
                    name=f"{node.name}.{child.name}",
                    start_line=child.lineno,
                    end_line=child.end_lineno,
                    code=method_code
                )
            )

    # --------------------------------------------------
    # Fallback
    # --------------------------------------------------

    if not chunks and source_code.strip():

        chunks.append(
            _create_chunk(
                file_path=file_path,
                chunk_type="source_file",
                name=os.path.basename(file_path),
                start_line=1,
                end_line=len(lines),
                code=source_code
            )
        )

    return chunks
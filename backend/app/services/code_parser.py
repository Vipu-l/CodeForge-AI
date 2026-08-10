import ast


def parse_python_file(file_path: str) -> list[dict]:
    """
    Parse a Python file and extract meaningful code chunks.
    """

    with open(file_path, "r", encoding="utf-8-sig") as file:
        source_code = file.read()

    tree = ast.parse(source_code)

    lines = source_code.splitlines()
    chunks = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            code = "\n".join(
                lines[node.lineno - 1:node.end_lineno]
            )

            chunks.append({
                "file": file_path,
                "type": "function",
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "code": code
            })

        elif isinstance(node, ast.AsyncFunctionDef):
            code = "\n".join(
                lines[node.lineno - 1:node.end_lineno]
            )

            chunks.append({
                "type": "function",
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "code": code
            })

        elif isinstance(node, ast.ClassDef):
            code = "\n".join(
                lines[node.lineno - 1:node.end_lineno]
            )

            chunks.append({
                "file": file_path,
                "type": "class",
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "code": code
            })

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            chunks.append({
                "file": file_path,
                "type": "import",
                "name": ast.unparse(node),
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "code": ast.unparse(node)
            })

    return chunks
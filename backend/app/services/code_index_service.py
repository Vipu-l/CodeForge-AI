import os

from app.services.code_parser import parse_python_file
from app.services.embedding_service import generate_embedding
from app.services.vector_store import VectorStore


SUPPORTED_EXTENSIONS = {
    ".py"
}


IGNORED_DIRECTORIES = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules"
}


def build_code_index(repository_path: str):

    store = VectorStore()

    for root, directories, files in os.walk(
        repository_path
    ):

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in files:

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

                chunks = parse_python_file(
                    file_path
                )

                for chunk in chunks:

                    text = (
                        f"File: {file_path}\n"
                        f"Type: {chunk['type']}\n"
                        f"Name: {chunk['name']}\n"
                        f"Code:\n{chunk['code']}"
                    )

                    embedding = generate_embedding(
                        text
                    )

                    store.add(
                        chunk,
                        embedding
                    )

            except (
                SyntaxError,
                UnicodeDecodeError
            ):
                continue

    return store
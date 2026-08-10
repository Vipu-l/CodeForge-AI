import os

from git import Repo


BASE_REPOSITORY_PATH = "repositories"


IGNORED_DIRECTORIES = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build"
}


SOURCE_EXTENSIONS = {
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
    ".rb"
}


def clone_repository(repo_url: str, repository_name: str) -> str:
    """
    Clone a GitHub repository into the repositories directory.

    If the repository already exists locally, reuse it.
    """

    os.makedirs(BASE_REPOSITORY_PATH, exist_ok=True)

    repository_path = os.path.join(
        BASE_REPOSITORY_PATH,
        repository_name
    )

    # If the repository is already cloned,
    # reuse the existing copy.
    if os.path.exists(repository_path):
    repo = Repo(repository_path)
    repo.remotes.origin.pull()
    return repository_path

    Repo.clone_from(repo_url, repository_path)

    return repository_path


def get_repository_files(repository_path: str) -> list[str]:
    """
    Return all files in the repository while
    ignoring unnecessary directories.
    """

    files = []

    for root, directories, filenames in os.walk(repository_path):

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in filenames:
            full_path = os.path.join(root, filename)

            relative_path = os.path.relpath(
                full_path,
                repository_path
            )

            files.append(relative_path)

    return files


def get_source_files(files: list[str]) -> list[str]:
    """
    Filter repository files and return source-code files.
    """

    source_files = []

    for file in files:
        extension = os.path.splitext(file)[1].lower()

        if extension in SOURCE_EXTENSIONS:
            source_files.append(file)

    return source_files
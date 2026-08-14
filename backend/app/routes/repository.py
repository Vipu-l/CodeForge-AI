import os

from fastapi import APIRouter, HTTPException

from app.services.repository_service import (
    clone_repository,
    get_repository_files,
    get_source_files,
)
from app.services.code_index_service import build_code_index
from app.services.index_manager import save_index


router = APIRouter(
    prefix="/api/repositories",
    tags=["Repositories"],
)


@router.post("/analyze")
def analyze_repository(repo_url: str):

    try:
        repository_name = (
            repo_url.rstrip("/").split("/")[-1]
        )

        if repository_name.endswith(".git"):
            repository_name = repository_name[:-4]

        repository_path = clone_repository(
            repo_url,
            repository_name,
        )

        all_files = get_repository_files(
            repository_path
        )

        source_files = get_source_files(
            all_files
        )

        # Build semantic code index
        code_index = build_code_index(
            repository_path
        )

        # Store index for Ask AI
        save_index(
            repository_name,
            code_index
        )

        return {
            "repository": repository_name,
            "total_files": len(all_files),
            "source_files": len(source_files),
            "files": all_files,
            "source_code_files": source_files,
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/file")
def get_repository_file(
    repository: str,
    file_path: str,
):

    try:
        repository_path = os.path.join(
            "repositories",
            repository,
        )

        full_path = os.path.abspath(
            os.path.join(
                repository_path,
                file_path,
            )
        )

        repository_root = os.path.abspath(
            repository_path
        )

        # Prevent accessing files outside
        # the repository directory.
        if not full_path.startswith(
            repository_root + os.sep
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid file path.",
            )

        if not os.path.isfile(full_path):
            raise HTTPException(
                status_code=404,
                detail="File not found.",
            )

        with open(
            full_path,
            "r",
            encoding="utf-8",
        ) as file:
            content = file.read()

        return {
            "repository": repository,
            "file": file_path,
            "content": content,
        }

    except HTTPException:
        raise

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File is not a text file.",
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
from fastapi import APIRouter, HTTPException

from app.services.repository_service import (
    clone_repository,
    get_repository_files,
    get_source_files
)


router = APIRouter(
    prefix="/api/repositories",
    tags=["Repositories"]
)


@router.post("/analyze")
def analyze_repository(repo_url: str):

    try:
        repository_name = repo_url.rstrip("/").split("/")[-1]

        if repository_name.endswith(".git"):
            repository_name = repository_name[:-4]

        repository_path = clone_repository(
            repo_url,
            repository_name
        )

        all_files = get_repository_files(
            repository_path
        )

        source_files = get_source_files(
            all_files
        )

        return {
            "repository": repository_name,
            "total_files": len(all_files),
            "source_files": len(source_files),
            "files": all_files,
            "source_code_files": source_files
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
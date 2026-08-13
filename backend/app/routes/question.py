from fastapi import APIRouter, HTTPException

from app.services.index_manager import get_index
from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"]
)


@router.post("/ask")
def ask_question(
    question: str,
    repository: str
):

    try:

        search_index = get_index(
            repository
        )

        if search_index is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Repository has not been analyzed yet."
                )
            )

        result = answer_question(
            question,
            search_index
        )

        return result

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
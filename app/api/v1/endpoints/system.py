from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Checks whether the API is running and ready to accept requests.",
)
def health_check():
    return {"status": "ok"}

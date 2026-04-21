from fastapi import HTTPException


def raise_upstream_error(exc: Exception) -> None:
    """Raise a 502 Bad Gateway error wrapping the upstream exception."""
    raise HTTPException(status_code=502, detail=str(exc)) from exc

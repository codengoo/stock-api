from fastapi import APIRouter, Query

from app.core.config import DEFAULT_SOURCE, SUPPORTED_SOURCES, UPSTREAM_ERROR_DESCRIPTION
from app.core.exceptions import raise_upstream_error
from app.services.market_service import get_listing, get_company_overview

router = APIRouter()


@router.get(
    "/listing",
    tags=["Reference Data"],
    summary="Listed symbols",
    description=(
        "Returns the list of listed stock symbols for the selected source.\n\n"
        "Useful for syncing the symbol universe before calling price endpoints."
    ),
    response_description="Listed stock symbols.",
    responses={502: {"description": UPSTREAM_ERROR_DESCRIPTION}},
)
def listing(
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    try:
        data = get_listing(source)
        return {"source": source, "data": data}
    except Exception as exc:
        raise_upstream_error(exc)


@router.get(
    "/company/{symbol}",
    tags=["Reference Data"],
    summary="Company overview",
    description=(
        "Returns overview information for a listed company, such as company name, "
        "industry, exchange, and other basic fields provided by `vnstock`."
    ),
    response_description="Overview information for the requested company.",
    responses={502: {"description": UPSTREAM_ERROR_DESCRIPTION}},
)
def company_overview(
    symbol: str,
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    symbol = symbol.upper()
    try:
        data = get_company_overview(symbol, source)
        return {"symbol": symbol, "source": source, "data": data}
    except Exception as exc:
        raise_upstream_error(exc)

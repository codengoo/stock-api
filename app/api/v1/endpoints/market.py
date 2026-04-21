from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.config import DEFAULT_SOURCE, SUPPORTED_SOURCES, UPSTREAM_ERROR_DESCRIPTION
from app.core.exceptions import raise_upstream_error
from app.services.market_service import get_history, get_intraday, get_price_board

router = APIRouter()


@router.get(
    "/price-board",
    tags=["Market Data"],
    summary="Real-time price board",
    description=(
        "Returns a price board snapshot for a list of stock symbols.\n\n"
        "Use this endpoint to quickly inspect bid/ask prices, volume, and other "
        "market fields returned by `vnstock`."
    ),
    response_description="Price board records grouped by stock symbol.",
    responses={
        400: {"description": "Missing or invalid `symbols` parameter."},
        502: {"description": UPSTREAM_ERROR_DESCRIPTION},
    },
)
def get_price_board(
    symbols: str = Query(
        ...,
        description="Comma-separated list of stock symbols. Example: VCB,ACB,TCB",
        examples=["VCB,ACB,TCB"],
    ),
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not symbol_list:
        raise HTTPException(
            status_code=400,
            detail="The stock symbol list must not be empty.",
        )
    try:
        data = get_price_board(symbol_list, source)
        return {"symbols": symbol_list, "source": source, "data": data}
    except Exception as exc:
        raise_upstream_error(exc)


@router.get(
    "/quote/intraday/{symbol}",
    tags=["Market Data"],
    summary="Intraday matched-order data",
    description=(
        "Returns matched-order intraday trading data for a single stock symbol.\n\n"
        "This endpoint is useful for intraday flow analysis, tick monitoring, "
        "or syncing intraday records from `vnstock`."
    ),
    response_description="Intraday tick records for the requested symbol.",
    responses={502: {"description": UPSTREAM_ERROR_DESCRIPTION}},
)
def intraday(
    symbol: str,
    page_size: int = Query(
        100,
        ge=1,
        le=10000,
        description="Maximum number of records to return in one request.",
    ),
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    symbol = symbol.upper()
    try:
        data = get_intraday(symbol, source, page_size)
        return {"symbol": symbol, "page_size": page_size, "source": source, "data": data}
    except Exception as exc:
        raise_upstream_error(exc)


@router.get(
    "/quote/history/{symbol}",
    tags=["Market Data"],
    summary="Historical prices",
    description=(
        "Returns historical price data by day, week, or month.\n\n"
        "Parameter priority:\n"
        "1. If `length` is provided, return the latest `length` sessions.\n"
        "2. If both `start` and `end` are provided, return that date range.\n"
        "3. If only `start` is provided, `end` defaults to the current date.\n"
        "4. If nothing is provided, return the latest 90 sessions."
    ),
    response_description="Historical price records for the requested symbol.",
    responses={502: {"description": UPSTREAM_ERROR_DESCRIPTION}},
)
def history(
    symbol: str,
    start: Optional[str] = Query(
        None,
        description="Start date in YYYY-MM-DD format.",
        examples=["2026-01-01"],
    ),
    end: Optional[str] = Query(
        None,
        description="End date in YYYY-MM-DD format.",
        examples=["2026-04-01"],
    ),
    length: Optional[int] = Query(
        None,
        ge=1,
        description="Number of latest sessions. Takes priority over start/end.",
        examples=[90],
    ),
    interval: str = Query(
        "d",
        description="Data interval: d (day), w (week), m (month).",
        examples=["d"],
    ),
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    symbol = symbol.upper()
    try:
        data = get_history(symbol, source, start=start, end=end, length=length, interval=interval)
        return {"symbol": symbol, "interval": interval, "source": source, "data": data}
    except Exception as exc:
        raise_upstream_error(exc)

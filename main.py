from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

from vnstock import Company, Listing, Quote, Trading

DEFAULT_SOURCE = "KBS"
SUPPORTED_SOURCES = "KBS, VCI"
UPSTREAM_ERROR_DESCRIPTION = (
    "Failed to fetch data from vnstock or the upstream data provider."
)

APP_DESCRIPTION = """
API for querying Vietnamese stock market data using `vnstock`.

Interactive documentation:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

General conventions:
- Stock symbols are normalized to uppercase before querying.
- The default `source` is `KBS`.
- Upstream provider errors are returned as HTTP `502`.
"""

OPENAPI_TAGS = [
    {
        "name": "Market Data",
        "description": "Price board, intraday, and historical market data.",
    },
    {
        "name": "Reference Data",
        "description": "Listed symbols and company reference data.",
    },
    {
        "name": "System",
        "description": "System-level endpoints such as health checks.",
    },
]

app = FastAPI(
    title="Stock Alert API",
    description=APP_DESCRIPTION,
    version="1.1.0",
    openapi_tags=OPENAPI_TAGS,
)


def df_to_records(df: pd.DataFrame) -> list:
    """Convert DataFrame to a JSON-serialisable list of dicts."""
    if df is None or df.empty:
        return []

    datetime_columns = df.select_dtypes(
        include=["datetime64[ns]", "datetimetz"]
    ).columns
    for col in datetime_columns:
        df[col] = df[col].astype(str)

    return df.to_dict(orient="records")


def raise_upstream_error(exc: Exception) -> None:
    raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/", include_in_schema=False)
def index():
    return {
        "name": app.title,
        "version": app.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get(
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
        df = Trading(source=source).price_board(symbol_list)
        return {"symbols": symbol_list, "source": source, "data": df_to_records(df)}
    except Exception as exc:
        raise_upstream_error(exc)


@app.get(
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
def get_intraday(
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
        quote = Quote(symbol=symbol, source=source)
        df = quote.intraday(symbol=symbol, page_size=page_size, show_log=False)
        return {
            "symbol": symbol,
            "page_size": page_size,
            "source": source,
            "data": df_to_records(df),
        }
    except Exception as exc:
        raise_upstream_error(exc)


@app.get(
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
def get_history(
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
        quote = Quote(symbol=symbol, source=source)
        if length:
            df = quote.history(length=str(length), interval=interval)
        elif start and end:
            df = quote.history(start=start, end=end, interval=interval)
        elif start:
            today = pd.Timestamp.today().strftime("%Y-%m-%d")
            df = quote.history(start=start, end=today, interval=interval)
        else:
            df = quote.history(length="90", interval=interval)

        return {
            "symbol": symbol,
            "interval": interval,
            "source": source,
            "data": df_to_records(df),
        }
    except Exception as exc:
        raise_upstream_error(exc)


@app.get(
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
def get_listing(
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    try:
        df = Listing(source=source).all_symbols()
        return {"source": source, "data": df_to_records(df)}
    except Exception as exc:
        raise_upstream_error(exc)


@app.get(
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
def get_company_overview(
    symbol: str,
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    symbol = symbol.upper()
    try:
        company = Company(symbol=symbol, source=source)
        df = company.overview()
        return {"symbol": symbol, "source": source, "data": df_to_records(df)}
    except Exception as exc:
        raise_upstream_error(exc)


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Checks whether the API is running and ready to accept requests.",
)
def health_check():
    return {"status": "ok"}

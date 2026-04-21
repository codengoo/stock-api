from fastapi import APIRouter, HTTPException, Query

from app.core.config import DEFAULT_SOURCE, SUPPORTED_SOURCES, UPSTREAM_ERROR_DESCRIPTION
from app.schemas.analysis import ScreenerResponse, StockScore
from app.services.analysis_service import (
    compute_moving_averages,
    fetch_history,
    get_last_price,
    score_symbol,
)

router = APIRouter()


@router.get(
    "/suggest",
    response_model=ScreenerResponse,
    tags=["Screener"],
    summary="Daily Trend Screener",
    description=(
        "Scores each symbol based on simple trend-following rules using Daily Historical Data.\n\n"
        "**Scoring Mechanism:**\n"
        "- **+2 Points**: Price > MA20 > MA50 (Strong short-to-medium term uptrend)\n"
        "- **+1 Point**: Price > MA200 (Positive long-term bias)\n\n"
        "**Technical details:**\n"
        "- At least **260 trading sessions** are fetched per symbol to ensure MA200 can be calculated.\n"
        "- Symbols that lack sufficient historical data or fail to fetch are skipped and listed in the `skipped` array."
    ),
    response_description="Ranked list of stocks sorted by score (highest first), plus details about skipped symbols.",
    responses={
        400: {"description": "Missing or invalid `symbols` parameter."},
        502: {"description": UPSTREAM_ERROR_DESCRIPTION},
    },
)
def suggest(
    symbols: str = Query(
        ...,
        description="Comma-separated list of stock symbols to screen. Example: VCB,ACB,TCB",
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

    results: list[StockScore] = []
    skipped: list[str] = []

    for sym in symbol_list:
        try:
            df = fetch_history(symbol=sym, source=source, length=260)
            mas = compute_moving_averages(df, periods=[20, 50, 200])
            last_price = get_last_price(df)

            if last_price is None:
                skipped.append(sym)
                continue

            score, signals = score_symbol(
                last_price=last_price,
                ma20=mas.get("ma20"),
                ma50=mas.get("ma50"),
                ma200=mas.get("ma200"),
            )

            results.append(
                StockScore(
                    symbol=sym,
                    last_price=last_price,
                    ma20=mas.get("ma20"),
                    ma50=mas.get("ma50"),
                    ma200=mas.get("ma200"),
                    score=score,
                    signals=signals,
                )
            )
        except Exception:
            skipped.append(sym)

    results.sort(key=lambda s: s.score, reverse=True)

    return ScreenerResponse(total=len(results), suggestions=results)

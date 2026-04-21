from fastapi import APIRouter, Query

from app.core.config import DEFAULT_SOURCE, SUPPORTED_SOURCES, UPSTREAM_ERROR_DESCRIPTION
from app.core.exceptions import raise_upstream_error
from app.schemas.analysis import MAResponse
from app.services.analysis_service import (
    compute_moving_averages,
    fetch_history,
    get_last_price,
)

router = APIRouter()


@router.get(
    "/ma/{symbol}",
    response_model=MAResponse,
    tags=["Analysis"],
    summary="Daily Moving Averages (MA20/MA50)",
    description=(
        "Calculates the 20-session and 50-session simple moving averages (SMA) "
        "for a single stock symbol using daily closing prices.\n\n"
        "This endpoint fetches the latest 60 trading sessions to ensure both MA20 and MA50 "
        "are computed accurately. The result includes the last closed price for reference."
    ),
    response_description="MA20, MA50 and last closing price for the requested symbol.",
    responses={502: {"description": UPSTREAM_ERROR_DESCRIPTION}},
)
def moving_averages(
    symbol: str,
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    symbol = symbol.upper()
    try:
        df = fetch_history(symbol=symbol, source=source, length=60)
        mas = compute_moving_averages(df, periods=[20, 50])
        last_price = get_last_price(df)
        return MAResponse(
            symbol=symbol,
            last_price=last_price,
            ma20=mas.get("ma20"),
            ma50=mas.get("ma50"),
            source=source,
        )
    except Exception as exc:
        raise_upstream_error(exc)

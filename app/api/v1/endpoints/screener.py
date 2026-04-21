from fastapi import APIRouter, HTTPException, Query

from app.core.config import DEFAULT_SOURCE, SUPPORTED_SOURCES, UPSTREAM_ERROR_DESCRIPTION
from app.schemas.analysis import ScreenerResponse, StockScore
from app.services.analysis_service import (
    compute_moving_averages,
    fetch_all_symbols,
    fetch_history,
    get_last_price,
    score_symbol,
)

router = APIRouter()


@router.get(
    "/suggest",
    response_model=ScreenerResponse,
    tags=["Screener"],
    summary="Daily Trend Screener – Top N",
    description=(
        "Quét toàn bộ cổ phiếu niêm yết và trả về những cổ phiếu có điểm cao nhất "
        "dựa trên quy tắc theo xu hướng hàng ngày.\n\n"
        "**Cơ chế tính điểm:**\n"
        "- **+2 Điểm**: Giá > MA20 > MA50 (xu hướng tăng ngắn-trung hạn)\n"
        "- **+1 Điểm**: Giá > MA200 (xu hướng tăng dài hạn)\n\n"
        "**Chi tiết kỹ thuật:**\n"
        "- Lấy tối thiểu **260 phiên giao dịch** để tính MA200.\n"
        "- Các mã thiếu dữ liệu hoặc lỗi khi tải được bỏ qua và liệt kê trong mảng `skipped`."
    ),
    response_description="Top N cổ phiếu có điểm cao nhất (giảm dần), kèm danh sách mã bị bỏ qua.",
    responses={
        502: {"description": UPSTREAM_ERROR_DESCRIPTION},
    },
)
def suggest(
    top_n: int = Query(
        5,
        ge=1,
        le=50,
        description="Số lượng cổ phiếu điểm cao nhất cần trả về (mặc định: 5, tối đa: 50).",
    ),
    source: str = Query(
        DEFAULT_SOURCE,
        description=f"Data source. Common values: {SUPPORTED_SOURCES}.",
    ),
):
    try:
        symbol_list = fetch_all_symbols(source)
    except Exception as exc:
        from app.core.exceptions import raise_upstream_error
        raise_upstream_error(exc)

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
    top_results = results[:top_n]

    return ScreenerResponse(total=len(top_results), suggestions=top_results, skipped=skipped)

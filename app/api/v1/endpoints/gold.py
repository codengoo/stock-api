from fastapi import APIRouter

from app.core.exceptions import raise_upstream_error
from app.services.gold_service import (
    fetch_all_gold_prices,
    fetch_global_gold_price,
)

router = APIRouter()


@router.get(
    "/gold/local",
    tags=["Gold Prices"],
    summary="Domestic gold buy/sell prices",
    description=(
        "Scrapes current **buying** and **selling** gold prices for all supported "
        "organizations from [giavang.org](https://giavang.org/trong-nuoc/).\n\n"
        "Returns two price types per organization:\n"
        "- `gold_bar`: Giá vàng miếng (gold bullion)\n"
        "- `gold_ring`: Giá vàng nhẫn (gold ring)\n\n"
        "All organizations are fetched **in parallel**. "
        "Data is cached for **5 minutes**. "
        "Unit: `x1000đ/lượng` (multiply by 1,000 to get VND per lượng)."
    ),
    response_description="`{ organizations: [{ organization, org_slug, updated_at, gold_bar, gold_ring, unit }] }`",
    responses={
        502: {"description": "Failed to fetch or parse data from giavang.org."},
    },
)
async def gold_local():
    try:
        results = await fetch_all_gold_prices()
        return {"organizations": results}
    except Exception as exc:
        raise_upstream_error(exc)


@router.get(
    "/gold/global",
    tags=["Gold Prices"],
    summary="World gold price (XAU/USD)",
    description=(
        "Scrapes the current **world gold price** from "
        "[giavang.org/the-gioi](https://giavang.org/the-gioi/).\n\n"
        "Returns:\n"
        "- `price_usd_per_ounce`: Spot price in USD per troy ounce\n"
        "- `change_usd` / `change_pct`: 24-hour change (negative = decrease)\n"
        "- `price_vnd_per_ounce`: Converted price in VNĐ per ounce (Vietcombank rate)\n"
        "- `price_vnd_per_luong`: Converted price in VNĐ per lượng (tael)\n\n"
        "Data is cached for **5 minutes**."
    ),
    response_description=(
        "`{ updated_at, price_usd_per_ounce, change_usd, change_pct, "
        "price_vnd_per_ounce, price_vnd_per_luong, unit_usd, unit_vnd }`"
    ),
    responses={
        502: {"description": "Failed to fetch or parse data from giavang.org."},
    },
)
async def gold_global():
    try:
        return await fetch_global_gold_price()
    except Exception as exc:
        raise_upstream_error(exc)

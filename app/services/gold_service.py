import asyncio
import re
from time import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup

_LOCAL_BASE = "https://giavang.org/trong-nuoc"
_GLOBAL_URL = "https://giavang.org/the-gioi/"

SUPPORTED_ORGS: dict[str, str] = {
    "sjc": "SJC",
    "doji": "DOJI",
    "pnj": "PNJ",
    "bao-tin-minh-chau": "Bảo Tín Minh Châu",
    "bao-tin-manh-hai": "Bảo Tín Mạnh Hải",
    "phu-quy": "Phú Quý",
    "mi-hong": "Mi Hồng",
    "ngoc-tham": "Ngọc Thẩm",
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Simple in-memory TTL cache: key -> (timestamp, data)
_CACHE: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_vn_number(text: str) -> Optional[float]:
    """Parse Vietnamese thousand-separated number: '163.000' -> 163000.0"""
    s = text.strip().replace(".", "").replace(",", ".")
    try:
        val = float(s)
        return val if val > 0 else None
    except ValueError:
        return None


def _parse_int_vn(text: str) -> Optional[int]:
    """Parse Vietnamese integer: '121.940.925' -> 121940925"""
    s = text.strip().replace(".", "").replace(",", "")
    try:
        return int(s)
    except ValueError:
        return None


def _parse_usd(text: str) -> Optional[float]:
    """Parse USD comma-decimal: '4,624.58' -> 4624.58"""
    s = text.strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _extract_updated_at(page_text: str) -> Optional[str]:
    m = re.search(
        r"Cập nhật lúc\s+(\d{2}:\d{2}:\d{2}\s+\d{2}/\d{2}/\d{4})", page_text
    )
    return m.group(1).strip() if m else None


def _parse_price_row(row) -> dict:
    """Extract buy/sell prices from a div.row inside gold-price-box."""
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    for col in row.find_all("div", class_="col-6"):
        label_el = col.find("span", class_="gold-price-label")
        price_el = col.find("span", class_="gold-price")
        if not label_el or not price_el:
            continue
        # Remove nested <small> tag before reading price text
        for small in price_el.find_all("small"):
            small.decompose()
        price_text = price_el.get_text(strip=True)
        label_text = label_el.get_text(strip=True).lower()
        if "mua" in label_text:
            buy_price = _parse_vn_number(price_text)
        elif "bán" in label_text:
            sell_price = _parse_vn_number(price_text)
    return {"buy_price": buy_price, "sell_price": sell_price}


# ---------------------------------------------------------------------------
# Local gold prices
# ---------------------------------------------------------------------------

async def fetch_gold_prices(org_slug: str) -> dict:
    now = time()
    if org_slug in _CACHE:
        cached_time, cached_data = _CACHE[org_slug]
        if now - cached_time < _CACHE_TTL:
            return cached_data

    url = f"{_LOCAL_BASE}/{org_slug}/"
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(url, headers=_HEADERS)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    gold_bar: dict = {}
    gold_ring: dict = {}

    # One gold-price-box contains both sections separated by h2 headings
    box = soup.find("div", class_="gold-price-box")
    if box:
        for h2 in box.find_all("h2"):
            title = h2.get_text(strip=True)
            row = h2.find_next_sibling("div", class_="row")
            if not row:
                continue
            if "Miếng" in title:
                gold_bar = _parse_price_row(row)
            elif "Nhẫn" in title:
                gold_ring = _parse_price_row(row)

    updated_at = _extract_updated_at(soup.get_text(" ", strip=True))

    result = {
        "organization": SUPPORTED_ORGS.get(org_slug, org_slug.upper()),
        "org_slug": org_slug,
        "updated_at": updated_at,
        "gold_bar": gold_bar,
        "gold_ring": gold_ring,
        "unit": "x1000đ/lượng",
    }
    _CACHE[org_slug] = (now, result)
    return result


async def fetch_all_gold_prices() -> list[dict]:
    tasks = [fetch_gold_prices(slug) for slug in SUPPORTED_ORGS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if isinstance(r, dict)]


# ---------------------------------------------------------------------------
# Global gold price
# ---------------------------------------------------------------------------

async def fetch_global_gold_price() -> dict:
    cache_key = "__global__"
    now = time()
    if cache_key in _CACHE:
        cached_time, cached_data = _CACHE[cache_key]
        if now - cached_time < _CACHE_TTL:
            return cached_data

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(_GLOBAL_URL, headers=_HEADERS)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    page_text = soup.get_text(" ", strip=True)

    updated_at = _extract_updated_at(page_text)

    # Current price: "hôm nay là X USD"
    price_usd: Optional[float] = None
    m = re.search(r"hôm nay là\s+([\d,]+\.?\d*)\s*USD", page_text)
    if m:
        price_usd = _parse_usd(m.group(1))

    # Change: "tăng/giảm X% trong 24 giờ qua, tương ứng với tăng/giảm Y USD/Ounce"
    change_usd: Optional[float] = None
    change_pct: Optional[float] = None
    m = re.search(
        r"(tăng|giảm)\s+([\d,.]+)%\s+trong 24 giờ.*?tương ứng.*?(tăng|giảm)\s+([\d,.]+)\s*USD",
        page_text,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        direction = 1 if m.group(1).lower() == "tăng" else -1
        pct = _parse_usd(m.group(2))
        usd = _parse_usd(m.group(4))
        change_pct = round(pct * direction, 4) if pct is not None else None
        change_usd = round(usd * direction, 4) if usd is not None else None

    # VND per ounce: "1 Ounce = X VNĐ"
    vnd_per_ounce: Optional[int] = None
    m = re.search(r"1\s*Ounce\s*=\s*([\d.,]+)\s*VNĐ", page_text)
    if m:
        vnd_per_ounce = _parse_int_vn(m.group(1))

    # VND per lượng: "1 cây vàng ... giá là X VNĐ"
    vnd_per_luong: Optional[int] = None
    m = re.search(
        r"1\s*cây vàng.*?giá là\s*([\d.,]+)\s*VNĐ",
        page_text,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        vnd_per_luong = _parse_int_vn(m.group(1))

    result = {
        "updated_at": updated_at,
        "price_usd_per_ounce": price_usd,
        "change_usd": change_usd,
        "change_pct": change_pct,
        "price_vnd_per_ounce": vnd_per_ounce,
        "price_vnd_per_luong": vnd_per_luong,
        "unit_usd": "USD/ounce",
        "unit_vnd": "VNĐ",
    }
    _CACHE[cache_key] = (now, result)
    return result

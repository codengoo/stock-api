from typing import List, Optional

from pydantic import BaseModel


class MAResponse(BaseModel):
    """Response schema for moving average endpoint."""

    symbol: str
    last_price: Optional[float]
    ma20: Optional[float]
    ma50: Optional[float]
    source: str


class StockScore(BaseModel):
    """Scoring result for a single stock in the screener."""

    symbol: str
    last_price: Optional[float]
    ma20: Optional[float]
    ma50: Optional[float]
    ma200: Optional[float]
    score: int
    signals: List[str]


class ScreenerResponse(BaseModel):
    """Response schema for the screener/suggest endpoint."""

    total: int
    suggestions: List[StockScore]

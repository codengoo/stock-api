from typing import Optional

import pandas as pd
from vnstock import Quote


def fetch_history(symbol: str, source: str, length: int = 260) -> pd.DataFrame:
    """Fetch daily historical OHLCV data for a symbol.

    Args:
        length: Number of most-recent trading sessions to fetch.
                Use at least 260 when MA200 is needed.
    """
    quote = Quote(symbol=symbol, source=source)
    return quote.history(length=str(length), interval="d")


def compute_moving_averages(
    df: pd.DataFrame, periods: list
) -> dict:
    """Compute rolling simple moving averages for the given periods.

    Returns a dict with keys like ``ma20``, ``ma50``, ``ma200``.
    Values are ``None`` when there is insufficient data.
    """
    close = df["close"]
    result = {}
    for period in periods:
        last_value = close.rolling(window=period).mean().iloc[-1]
        result[f"ma{period}"] = (
            round(float(last_value), 2) if not pd.isna(last_value) else None
        )
    return result


def get_last_price(df: pd.DataFrame) -> Optional[float]:
    """Return the most-recent closing price, or ``None`` if unavailable."""
    if df is None or df.empty:
        return None
    return round(float(df["close"].iloc[-1]), 2)


def score_symbol(
    last_price: float,
    ma20: Optional[float],
    ma50: Optional[float],
    ma200: Optional[float],
) -> tuple:
    """Score a symbol based on trend-following rules.

    Scoring rules:
        +2  Giá > MA20 > MA50  (xu hướng tăng ngắn-trung hạn)
        +1  Giá > MA200        (xu hướng tăng dài hạn)

    Returns:
        (score, signals) where ``signals`` is a list of matched rule descriptions.
    """
    score = 0
    signals = []

    if ma20 is not None and ma50 is not None:
        if last_price > ma20 and ma20 > ma50:
            score += 2
            signals.append("Giá > MA20 > MA50")

    if ma200 is not None:
        if last_price > ma200:
            score += 1
            signals.append("Giá > MA200")

    return score, signals

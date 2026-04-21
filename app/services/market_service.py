import pandas as pd
from vnstock import Company, Listing, Quote, Trading


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


def get_price_board(symbol_list: list, source: str) -> list:
    df = Trading(source=source).price_board(symbol_list)
    return df_to_records(df)


def get_intraday(symbol: str, source: str, page_size: int) -> list:
    quote = Quote(symbol=symbol, source=source)
    df = quote.intraday(symbol=symbol, page_size=page_size, show_log=False)
    return df_to_records(df)


def get_history(
    symbol: str,
    source: str,
    start: str = None,
    end: str = None,
    length: int = None,
    interval: str = "d",
) -> list:
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
    return df_to_records(df)


def get_listing(source: str) -> list:
    df = Listing(source=source).all_symbols()
    return df_to_records(df)


def get_company_overview(symbol: str, source: str) -> list:
    company = Company(symbol=symbol, source=source)
    df = company.overview()
    return df_to_records(df)

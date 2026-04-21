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
        "name": "Analysis",
        "description": "Technical indicators such as moving averages (MA).",
    },
    {
        "name": "Screener",
        "description": "Stock screening and suggestion based on technical rules.",
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

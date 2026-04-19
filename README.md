# Stock Alert API

This API wraps `vnstock` into FastAPI endpoints for retrieving Vietnamese stock market data.

## Available Features

- Real-time price board for multiple symbols
- Intraday matched-order data for a single symbol
- Historical prices by day, week, or month
- Listed symbol directory
- Company overview data
- Health check

## Installation

```bash
pip install -r requirements.txt
```

## Run The Application

```bash
make run
```

By default, the API runs at:

- `http://127.0.0.1:8000`
- `http://localhost:8000`

Interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## General Conventions

- The default `source` is `KBS`
- Some endpoints may also support `VCI`, depending on `vnstock`
- Stock symbols are normalized to uppercase before querying
- Errors from `vnstock` or the upstream data provider are returned as HTTP `502`

## Endpoint Details

### 1. `GET /price-board`

Returns a real-time price board snapshot for multiple stock symbols.

Query parameters:

- `symbols` required: comma-separated list of stock symbols, for example `VCB,ACB,TCB`
- `source` optional: data source, default is `KBS`

Main response fields:

- `symbols`: normalized symbol list
- `source`: selected data source
- `data`: price board data returned by `vnstock`

Example:

```bash
curl "http://127.0.0.1:8000/price-board?symbols=VCB,ACB,TCB"
```

### 2. `GET /quote/intraday/{symbol}`

Returns intraday matched-order data for a single stock symbol.

Path parameters:

- `symbol`: stock symbol, for example `VCB`

Query parameters:

- `page_size` optional: maximum number of records, default `100`, maximum `10000`
- `source` optional: data source, default `KBS`

Main response fields:

- `symbol`: stock symbol
- `page_size`: requested record limit
- `source`: selected data source
- `data`: list of intraday ticks

Example:

```bash
curl "http://127.0.0.1:8000/quote/intraday/VCB?page_size=200"
```

### 3. `GET /quote/history/{symbol}`

Returns historical price data by day, week, or month.

Path parameters:

- `symbol`: stock symbol, for example `VCB`

Query parameters:

- `start` optional: start date in `YYYY-MM-DD` format
- `end` optional: end date in `YYYY-MM-DD` format
- `length` optional: latest number of sessions to return
- `interval` optional: `d`, `w`, `m`, default `d`
- `source` optional: data source, default `KBS`

Parameter priority:

1. If `length` is provided, the API returns the latest `length` sessions
2. If `start` and `end` are both provided, the API returns data in that date range
3. If only `start` is provided, `end` defaults to the current date
4. If nothing is provided, the API returns the latest `90` sessions

Main response fields:

- `symbol`: stock symbol
- `interval`: selected interval
- `source`: selected data source
- `data`: historical price records

Examples:

```bash
curl "http://127.0.0.1:8000/quote/history/VCB?start=2026-01-01&end=2026-04-01&interval=d"
curl "http://127.0.0.1:8000/quote/history/VCB?length=30&interval=w"
```

### 4. `GET /listing`

Returns the directory of listed stock symbols.

Query parameters:

- `source` optional: data source, default `KBS`

Main response fields:

- `source`: selected data source
- `data`: listed symbols

Example:

```bash
curl "http://127.0.0.1:8000/listing"
```

### 5. `GET /company/{symbol}`

Returns company overview data for a listed stock symbol.

Path parameters:

- `symbol`: stock symbol, for example `FPT`

Query parameters:

- `source` optional: data source, default `KBS`

Main response fields:

- `symbol`: stock symbol
- `source`: selected data source
- `data`: company overview data

Example:

```bash
curl "http://127.0.0.1:8000/company/FPT"
```

### 6. `GET /health`

Checks whether the API is running.

Response:

```json
{"status":"ok"}
```

## Stop The Application

If you started the API with:

```bash
make run
```

the normal way to stop it is pressing `Ctrl + C` in the terminal running `uvicorn`.

The repository also provides:

```bash
make stop
```

This command finds the process listening on port `8000` and stops it.

If the terminal was closed but the process is still holding port `8000`, use PowerShell:

```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object -First 1 -ExpandProperty OwningProcess) -Force
```

If you want to inspect the process before stopping it:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object -First 1 -ExpandProperty OwningProcess | Get-Process
```

## Notes

- The root path `/` returns quick links to `docs`, `redoc`, and `health`
- Endpoint documentation is also available directly in Swagger UI and ReDoc

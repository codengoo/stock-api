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

## Endpoint Details

### 1. Market Data

These endpoints provide real-time and historical market data using `vnstock`.

#### `GET /price-board`
**Summary**: Real-time price board snapshot for multiple symbols.

- **Query Parameters**:
    - `symbols` (required): Comma-separated list of stock symbols (e.g., `VCB,ACB,TCB`).
    - `source` (optional): Data source. Default: `KBS`. Supporting `VCI` for some symbols.

- **Example**:
    ```bash
    curl "http://localhost:8000/price-board?symbols=VCB,ACB,TCB&source=KBS"
    ```

#### `GET /quote/intraday/{symbol}`
**Summary**: Intraday matched-order (tick) data for a single symbol.

- **Path Parameters**:
    - `symbol`: Stock symbol (e.g., `VCB`).
- **Query Parameters**:
    - `page_size` (optional): Maximum records. Default `100`, Max `10000`.
    - `source` (optional): Data source. Default: `KBS`.

- **Example**:
    ```bash
    curl "http://localhost:8000/quote/intraday/VCB?page_size=200"
    ```

#### `GET /quote/history/{symbol}`
**Summary**: Historical price data (OHLCV).

- **Path Parameters**:
    - `symbol`: Stock symbol (e.g., `VCB`).
- **Query Parameters**:
    - `start` (optional): Start date (`YYYY-MM-DD`).
    - `end` (optional): End date (`YYYY-MM-DD`).
    - `length` (optional): Latest N sessions (takes priority over start/end).
    - `interval` (optional): `d` (day), `w` (week), `m` (month). Default: `d`.
    - `source` (optional): Data source. Default: `KBS`.

- **Example**:
    ```bash
    curl "http://localhost:8000/quote/history/VCB?length=30&interval=d"
    ```

---

### 2. Technical Analysis

#### `GET /analysis/ma/{symbol}`
**Summary**: Moving averages (MA20 and MA50) for a symbol.

- **Path Parameters**:
    - `symbol`: Stock symbol (e.g., `FPT`).
- **Query Parameters**:
    - `source` (optional): Data source. Default: `KBS`.

- **Response Fields**:
    - `symbol`: Requested symbol.
    - `last_price`: Latest closing price.
    - `ma20`: 20-day simple moving average.
    - `ma50`: 50-day simple moving average.

- **Example**:
    ```bash
    curl "http://localhost:8000/analysis/ma/FPT"
    ```

---

### 3. Screener

#### `GET /screener/suggest`
**Summary**: Scores stocks based on trend-following rules.

- **Query Parameters**:
    - `symbols` (required): Comma-separated list to screen (e.g., `VCB,ACB,TCB,FPT,MWG`).
    - `source` (optional): Data source. Default: `KBS`.

- **Scoring Rules**:
    - **+2**: Price > MA20 > MA50 (Strong uptrend).
    - **+1**: Price > MA200 (Long-term positive bias).

- **Example**:
    ```bash
    curl "http://localhost:8000/screener/suggest?symbols=VCB,ACB,TCB,FPT,MWG"
    ```

---

### 4. Reference Data

#### `GET /listing`
**Summary**: Returns all listed stock symbols.

- **Query Parameters**:
    - `source` (optional): Data source. Default: `KBS`.

- **Example**:
    ```bash
    curl "http://localhost:8000/listing"
    ```

#### `GET /company/{symbol}`
**Summary**: Company profile and overview.

- **Path Parameters**:
    - `symbol`: Stock symbol (e.g., `FPT`).

- **Example**:
    ```bash
    curl "http://localhost:8000/company/FPT"
    ```

---

### 5. System

#### `GET /health`
**Summary**: Simple health check.

- **Example**:
    ```bash
    curl "http://localhost:8000/health"
    ```

- **Response**: `{"status": "ok"}`

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

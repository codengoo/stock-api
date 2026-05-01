# Stock Alert API – Tài liệu API

**Base URL:** `http://<host>/api/v1`  
**Interactive docs:** `/docs` (Swagger UI) · `/redoc` (ReDoc)  
**Version:** 2.0.0

---

## Mục lục

1. [Giá Vàng – Trong Nước (`/gold/local`)](#1-giá-vàng-trong-nước)
2. [Giá Vàng – Thế Giới (`/gold/global`)](#2-giá-vàng-thế-giới)
3. [Bảng Giá Chứng Khoán (`/price-board`)](#3-bảng-giá-chứng-khoán)
4. [Dữ Liệu Intraday (`/quote/intraday/{symbol}`)](#4-dữ-liệu-intraday)
5. [Dữ Liệu Lịch Sử (`/quote/history/{symbol}`)](#5-dữ-liệu-lịch-sử)
6. [Danh Sách Cổ Phiếu (`/listing`)](#6-danh-sách-cổ-phiếu)
7. [Thông Tin Công Ty (`/company/{symbol}`)](#7-thông-tin-công-ty)
8. [Moving Averages (`/analysis/ma/{symbol}`)](#8-moving-averages)
9. [Screener Gợi Ý (`/screener/suggest`)](#9-screener-gợi-ý)
10. [Health Check (`/health`)](#10-health-check)
11. [Quy ước chung](#quy-ước-chung)

---

## 1. Giá Vàng Trong Nước

**`GET /gold/local`**

Cào và trả về giá vàng **mua vào** / **bán ra** hiện tại của tất cả tổ chức từ [giavang.org](https://giavang.org/trong-nuoc/).  
Trả về đồng thời **giá vàng miếng** và **giá vàng nhẫn** cho từng tổ chức.

> Dữ liệu được cache **5 phút** để tránh gọi quá nhiều lần lên site nguồn.

### Tham số

Không có tham số.

### Response

```json
{
  "organizations": [
    {
      "organization": "SJC",
      "org_slug": "sjc",
      "updated_at": "22:55:03 01/05/2026",
      "gold_bar": {
        "buy_price": 163000.0,
        "sell_price": 166000.0
      },
      "gold_ring": {
        "buy_price": 162500.0,
        "sell_price": 165500.0
      },
      "unit": "x1000đ/lượng"
    },
    ...
  ]
}
```

### Mô tả trường

| Trường | Kiểu | Mô tả |
|---|---|---|
| `organization` | string | Tên tổ chức (VD: `SJC`, `DOJI`, `PNJ`) |
| `org_slug` | string | Slug dùng trong URL nguồn (VD: `sjc`, `doji`) |
| `updated_at` | string | Thời điểm cập nhật trên trang nguồn |
| `gold_bar.buy_price` | float \| null | Giá vàng **miếng** mua vào |
| `gold_bar.sell_price` | float \| null | Giá vàng **miếng** bán ra |
| `gold_ring.buy_price` | float \| null | Giá vàng **nhẫn** mua vào |
| `gold_ring.sell_price` | float \| null | Giá vàng **nhẫn** bán ra |
| `unit` | string | Đơn vị: `x1000đ/lượng` (nhân ×1000 để ra VNĐ/lượng) |

### Tổ chức hỗ trợ

| `org_slug` | Tên tổ chức |
|---|---|
| `sjc` | SJC |
| `doji` | DOJI |
| `pnj` | PNJ |
| `bao-tin-minh-chau` | Bảo Tín Minh Châu |
| `bao-tin-manh-hai` | Bảo Tín Mạnh Hải |
| `phu-quy` | Phú Quý |
| `mi-hong` | Mi Hồng |
| `ngoc-tham` | Ngọc Thẩm |

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `502` | Không thể kết nối hoặc parse giavang.org |

---

## 2. Giá Vàng Thế Giới

**`GET /gold/global`**

Cào giá vàng quốc tế **XAU/USD** từ [giavang.org/the-gioi](https://giavang.org/the-gioi/), kèm quy đổi sang VNĐ (tỷ giá Vietcombank).

> Dữ liệu được cache **5 phút**.

### Tham số

Không có tham số.

### Response

```json
{
  "updated_at": "01:04:33 02/05/2026",
  "price_usd_per_ounce": 4624.58,
  "change_usd": 7.65,
  "change_pct": 0.17,
  "price_vnd_per_ounce": 121940925,
  "price_vnd_per_luong": 147018446,
  "unit_usd": "USD/ounce",
  "unit_vnd": "VNĐ"
}
```

### Mô tả trường

| Trường | Kiểu | Mô tả |
|---|---|---|
| `updated_at` | string | Thời điểm cập nhật trên trang nguồn |
| `price_usd_per_ounce` | float \| null | Giá vàng thế giới (USD/troy ounce) |
| `change_usd` | float \| null | Thay đổi 24h theo USD (âm = giảm) |
| `change_pct` | float \| null | Thay đổi 24h theo % (âm = giảm) |
| `price_vnd_per_ounce` | int \| null | Quy đổi sang VNĐ/ounce (tỷ giá Vietcombank) |
| `price_vnd_per_luong` | int \| null | Quy đổi sang VNĐ/lượng (1 lượng ≈ 0.829426 ounce) |
| `unit_usd` | string | `USD/ounce` |
| `unit_vnd` | string | `VNĐ` |

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `502` | Không thể kết nối hoặc parse giavang.org |

---

## 3. Bảng Giá Chứng Khoán

**`GET /price-board`**

Trả về snapshot bảng giá real-time cho một hoặc nhiều mã cổ phiếu. Dữ liệu từ `vnstock`.

### Tham số Query

| Tham số | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|
| `symbols` | ✅ | — | Danh sách mã cổ phiếu, phân cách bằng dấu phẩy. VD: `VCB,ACB,TCB` |
| `source` | ❌ | `KBS` | Nguồn dữ liệu. Hỗ trợ: `KBS`, `VCI` |

### Response

```json
{
  "symbols": ["VCB", "ACB"],
  "source": "KBS",
  "data": [
    {
      "symbol": "VCB",
      "bid": 85200,
      "ask": 85300,
      "last": 85200,
      "volume": 1234567,
      ...
    }
  ]
}
```

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `400` | `symbols` bị thiếu hoặc rỗng |
| `502` | Lỗi từ nhà cung cấp dữ liệu |

---

## 4. Dữ Liệu Intraday

**`GET /quote/intraday/{symbol}`**

Trả về dữ liệu lệnh khớp trong phiên (tick-by-tick) cho một mã cổ phiếu.

### Path Parameters

| Tham số | Mô tả |
|---|---|
| `symbol` | Mã cổ phiếu (không phân biệt chữ hoa/thường). VD: `VCB` |

### Tham số Query

| Tham số | Bắt buộc | Mặc định | Giới hạn | Mô tả |
|---|---|---|---|---|
| `page_size` | ❌ | `100` | 1–10000 | Số lượng bản ghi tối đa trả về |
| `source` | ❌ | `KBS` | — | Nguồn dữ liệu: `KBS`, `VCI` |

### Response

```json
{
  "symbol": "VCB",
  "page_size": 100,
  "source": "KBS",
  "data": [
    {
      "time": "14:30:00",
      "price": 85200,
      "volume": 500,
      "match_type": "ATO",
      ...
    }
  ]
}
```

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `502` | Lỗi từ nhà cung cấp dữ liệu |

---

## 5. Dữ Liệu Lịch Sử

**`GET /quote/history/{symbol}`**

Trả về dữ liệu giá lịch sử theo ngày/tuần/tháng.

### Path Parameters

| Tham số | Mô tả |
|---|---|
| `symbol` | Mã cổ phiếu. VD: `VCB` |

### Tham số Query

| Tham số | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|
| `length` | ❌ | — | Số phiên gần nhất. **Ưu tiên cao nhất** nếu có. VD: `90` |
| `start` | ❌ | — | Ngày bắt đầu định dạng `YYYY-MM-DD`. VD: `2026-01-01` |
| `end` | ❌ | Hôm nay | Ngày kết thúc định dạng `YYYY-MM-DD`. VD: `2026-04-30` |
| `interval` | ❌ | `d` | Khung thời gian: `d` (ngày), `w` (tuần), `m` (tháng) |
| `source` | ❌ | `KBS` | Nguồn dữ liệu: `KBS`, `VCI` |

**Ưu tiên tham số:**
1. `length` → Lấy N phiên gần nhất
2. `start` + `end` → Lấy theo khoảng ngày
3. `start` (không có `end`) → Từ `start` đến hôm nay
4. Không có gì → Lấy 90 phiên gần nhất

### Response

```json
{
  "symbol": "VCB",
  "source": "KBS",
  "data": [
    {
      "time": "2026-04-30",
      "open": 84000,
      "high": 85500,
      "low": 83800,
      "close": 85200,
      "volume": 2345678
    }
  ]
}
```

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `502` | Lỗi từ nhà cung cấp dữ liệu |

---

## 6. Danh Sách Cổ Phiếu

**`GET /listing`**

Trả về danh sách toàn bộ mã cổ phiếu đang niêm yết.

### Tham số Query

| Tham số | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|
| `source` | ❌ | `KBS` | Nguồn dữ liệu: `KBS`, `VCI` |

### Response

```json
{
  "source": "KBS",
  "data": [
    { "symbol": "VCB", "exchange": "HOSE", ... },
    { "symbol": "ACB", "exchange": "HOSE", ... }
  ]
}
```

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `502` | Lỗi từ nhà cung cấp dữ liệu |

---

## 7. Thông Tin Công Ty

**`GET /company/{symbol}`**

Trả về thông tin tổng quan về công ty: tên, ngành, sàn giao dịch, và các trường cơ bản khác.

### Path Parameters

| Tham số | Mô tả |
|---|---|
| `symbol` | Mã cổ phiếu. VD: `VCB` |

### Tham số Query

| Tham số | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|
| `source` | ❌ | `KBS` | Nguồn dữ liệu: `KBS`, `VCI` |

### Response

```json
{
  "symbol": "VCB",
  "source": "KBS",
  "data": {
    "company_name": "Ngân hàng TMCP Ngoại Thương Việt Nam",
    "exchange": "HOSE",
    "industry": "Banks",
    ...
  }
}
```

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `502` | Lỗi từ nhà cung cấp dữ liệu |

---

## 8. Moving Averages

**`GET /analysis/ma/{symbol}`**

Tính **MA20**, **MA50**, **MA200** (simple moving average) từ giá đóng cửa hàng ngày cho một mã cổ phiếu, kèm giá đóng cửa phiên gần nhất.

> Endpoint lấy 300 phiên gần nhất để đảm bảo đủ dữ liệu tính MA200.

### Path Parameters

| Tham số | Mô tả |
|---|---|
| `symbol` | Mã cổ phiếu. VD: `VCB` |

### Tham số Query

| Tham số | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|
| `source` | ❌ | `KBS` | Nguồn dữ liệu: `KBS`, `VCI` |

### Response

```json
{
  "symbol": "VCB",
  "last_price": 85200.0,
  "ma20": 84150.5,
  "ma50": 82300.0,
  "ma200": 79450.0
}
```

### Mô tả trường

| Trường | Kiểu | Mô tả |
|---|---|---|
| `symbol` | string | Mã cổ phiếu |
| `last_price` | float | Giá đóng cửa phiên gần nhất |
| `ma20` | float \| null | Trung bình động 20 phiên |
| `ma50` | float \| null | Trung bình động 50 phiên |
| `ma200` | float \| null | Trung bình động 200 phiên |

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `502` | Lỗi từ nhà cung cấp dữ liệu |

---

## 9. Screener Gợi Ý

**`GET /screener/suggest`**

Quét toàn bộ cổ phiếu niêm yết và trả về những mã có **điểm xu hướng tăng** cao nhất theo quy tắc:

| Điều kiện | Điểm |
|---|---|
| Giá đóng cửa > MA20 > MA50 | +2 |
| Giá đóng cửa > MA200 | +1 |

> Tổng điểm tối đa: **3 điểm**. Lấy tối thiểu 260 phiên để tính MA200.

### Tham số Query

| Tham số | Bắt buộc | Mặc định | Giới hạn | Mô tả |
|---|---|---|---|---|
| `top_n` | ❌ | `5` | 1–50 | Số lượng cổ phiếu trả về (điểm cao nhất, giảm dần) |
| `source` | ❌ | `KBS` | — | Nguồn dữ liệu: `KBS`, `VCI` |

### Response

```json
{
  "top_n": 5,
  "source": "KBS",
  "results": [
    {
      "symbol": "VCB",
      "last_price": 85200.0,
      "ma20": 84150.5,
      "ma50": 82300.0,
      "ma200": 79450.0,
      "score": 3
    }
  ],
  "skipped": ["XYZ", "ABC"]
}
```

### Mô tả trường

| Trường | Kiểu | Mô tả |
|---|---|---|
| `results` | array | Danh sách cổ phiếu có điểm cao nhất, sắp xếp giảm dần theo `score` |
| `results[].score` | int | Điểm xu hướng (0–3) |
| `results[].last_price` | float | Giá đóng cửa phiên gần nhất |
| `results[].ma20/ma50/ma200` | float | Giá trị moving average tương ứng |
| `skipped` | array | Các mã bị bỏ qua do thiếu dữ liệu hoặc lỗi tải |

### HTTP Errors

| Code | Ý nghĩa |
|---|---|
| `502` | Không thể lấy danh sách mã cổ phiếu từ nhà cung cấp |

---

## 10. Health Check

**`GET /health`**

Kiểm tra API có đang hoạt động không.

### Response

```json
{ "status": "ok" }
```

---

## Quy ước chung

### Data source

Tất cả endpoint liên quan đến chứng khoán đều nhận tham số `source`:

| Giá trị | Mô tả |
|---|---|
| `KBS` | KB Securities (mặc định) |
| `VCI` | Viet Capital Securities |

### Xử lý lỗi

| HTTP Code | Ý nghĩa |
|---|---|
| `400 Bad Request` | Tham số không hợp lệ hoặc bị thiếu |
| `502 Bad Gateway` | Lỗi từ nhà cung cấp dữ liệu upstream (vnstock / giavang.org) |

### Cache

Các endpoint cào dữ liệu web (giá vàng) sử dụng **in-memory TTL cache 5 phút** — nghĩa là trong 5 phút kể từ lần gọi đầu tiên, các lần gọi tiếp theo sẽ trả về dữ liệu đã được lưu thay vì gọi lại site nguồn.

### Đơn vị giá vàng

- `x1000đ/lượng`: Nhân giá trị với **1.000** để ra **VNĐ/lượng**.  
  Ví dụ: `163000` × 1.000 = **163.000.000 VNĐ/lượng** (163 triệu đồng).

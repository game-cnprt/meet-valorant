# 🎯 MeetValorant - Sổ Tay & Quản Lý Đồng Đội Valorant

> Ứng dụng web hiện đại, đậm chất **Cyber-Tactical Valorant UI** giúp bạn lưu trữ, phân loại, đánh giá và quản lý danh sách các đồng đội (teammates) và cạ cứng (duo buddies) đã từng sát cánh trong các trận đấu Valorant.

---

## 🌟 Tính Năng Nổi Bật

- ⚡ **Tích Hợp HenrikDev API (HenrikDev Valorant API)**:
  - Tra cứu tài khoản Riot ID chính chủ, lấy Rank MMR thực tế và avatar Card.
  - Xem danh sách 5 trận đấu xếp hạng/thường gần nhất (Map, Mode, KDA, Score).
  - Trích xuất TOÀN BỘ 10 người chơi trong mỗi trận đấu.
  - **1-Click Tự Động Lưu Tất Cả Đồng Đội**: Tự động lọc các đồng đội cùng team trong các trận vừa bắn và lưu vào sổ tay SQLite chỉ bằng một cú nhấp chuột.
- 🗂️ **Hồ sơ đồng đội đầy đủ**:
  - **Riot ID**: Tên game kèm Tagline (ví dụ: `TenZ#NA1`, `ViperQueen#VN1`).
  - **Bậc Rank**: Phân loại theo màu sắc chuẩn Valorant (từ *Sắt*, *Đồng*, *Bạc*, *Vàng*, *Bạch Kim*, *Kim Cương*, *Cao Thủ*, *Bất Tử* đến *Radiant*).
  - **Đặc vụ & Vai trò**: 4 Roles chính (*Duelist*, *Initiator*, *Controller*, *Sentinel*) cùng danh sách toàn bộ các đặc vụ (Jett, Omen, Sova, Chamber, Clove, Vyse,...).
  - **Đánh giá phối hợp**: Đánh giá thực chiến (*⭐ Gánh Team*, *🔥 Hợp Cạ Duo*, *🗣️ Callout Chuẩn*, *✨ Vui Vẻ / Chill*, *⚠️ Né Gấp*).
  - **Thống kê trận đấu**: Số trận đã bắn chung, tỉ lệ thắng (%) với thanh hiển thị trực quan.
  - **Thẻ phong cách chơi**: *Entry*, *Lurker*, *IGL*, *Lineup*, *OP God*, *Clutch God*, *Aim To*, *Giữ Flank*, hoặc tùy biến thẻ riêng.
  - **Discord / Liên hệ** & **Ghi chú cá nhân** về lối đánh, round clutch ấn tượng.
- ⭐ **Ghim Cạ Cứng (Duo Buddy)**: Đánh dấu sao những người bạn hợp cạ nhất để luôn ưu tiên hiển thị trên đầu danh sách khi tìm người leo rank.
- 🔍 **Tìm kiếm & Bộ lọc đa năng**:
  - Tìm kiếm tức thì theo Tên, Tag, Tên đặc vụ hoặc nội dung ghi chú.
  - Lọc theo từng Role, từng Bậc Rank, từng loại Đánh giá hoặc chế độ "Chỉ Cạ Cứng".
- 📊 **Thanh Thống Kê Tổng Quan**:
  - Đếm tổng số đồng đội đã lưu, số lượng cạ cứng.
  - Phân tích vai trò phổ biến nhất trong danh sách bạn bè.
  - Tỉ lệ người chơi gánh team.
- 🎨 **Giao Diện Đậm Chất Valorant**:
  - Giao diện Dark Theme cao cấp kết hợp sắc đỏ thương hiệu `#ff4655`, xanh ngọc Radiant `#00f5d4`, và vàng Gold.
  - Hiệu ứng vát góc chiến thuật (Tactical Cut), badge đặc vụ, animation mượt mà và responsive trên cả màn hình lớn lẫn thiết bị di động.
- 📦 **Nạp sẵn dữ liệu mẫu (Seeded Data)**: Tự động tạo sẵn danh sách đồng đội mẫu phong phú ngay lần chạy đầu tiên. Có nút **"Nạp Dữ Liệu Mẫu"** để khôi phục bất cứ lúc nào.

---

## 🛠️ Công Nghệ Sử Dụng

- **Backend**:
  - [Python 3](https://www.python.org/)
  - [FastAPI](https://fastapi.tiangolo.com/): Framework API tốc độ cao, hiện đại.
  - [HenrikDev API](https://api.henrikdev.xyz/): API lấy dữ liệu Valorant MMR & Matches thực tế.
  - [SQLite](https://www.sqlite.org/): Cơ sở dữ liệu nhẹ, lưu file `backend/valorant_teammates.db`.
  - [httpx](https://www.python-httpx.org/): Thư viện Async HTTP Client gọi HenrikDev API.
  - [Pydantic](https://docs.pydantic.dev/): Kiểm tra và xác thực dữ liệu đầu vào.
  - [Uvicorn](https://www.uvicorn.org/): ASGI web server.
- **Frontend**:
  - [Vue 3](https://vuejs.org/) (Composition API, `<script setup>`)
  - [Vite](https://vitejs.dev/): Công cụ build siêu nhanh.
  - **Vanilla CSS (Design Tokens)**: Tùy biến toàn bộ theo phong cách UI/HUD của Valorant.
  - Google Fonts: `Rajdhani` & `Inter`.

---

## 📂 Cấu Trúc Dự Án

```
MeetValorant/
├── backend/
│   ├── main.py                 # FastAPI endpoints & CORS
│   ├── riot_service.py         # HenrikDev API Integration (Account, Matches, Player extraction)
│   ├── database.py             # SQLite DB manager & CRUD operations
│   ├── data_helpers.py         # Helper phân loại Role từ Agent
│   ├── models.py               # Pydantic schemas xác thực dữ liệu
│   ├── requirements.txt        # Thư viện Python
│   ├── .env                    # Cấu hình HENRIKDEV_API_KEY
│   └── valorant_teammates.db   # File SQLite database
├── frontend/
│   ├── src/
│   │   ├── data/
│   │   │   └── valorantData.js # Dữ liệu Roles, Agents, Ranks, Ratings, Tags
│   │   ├── App.vue             # Giao diện chính (Header, Stats, Filters, Cards, Modals)
│   │   ├── main.js             # Vue entry point
│   │   └── style.css           # Hệ thống CSS Design System Valorant
│   ├── index.html              # HTML template với SEO và font chữ
│   ├── package.json            # Cấu hình dự án Node.js & dependencies
│   └── vite.config.js          # Cấu hình Vite & API reverse proxy
└── README.md                   # Tài liệu hướng dẫn sử dụng
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 1. Yêu Cầu Môi Trường
- **Python**: Phiên bản 3.9 trở lên (đã kiểm tra tương thích trên Python 3.14).
- **Node.js**: Phiên bản 18+ và **npm**.
- **HenrikDev API Key**: Đăng ký key miễn phí tại [HenrikDev Portal](https://api.henrikdev.xyz/).

---

### 2. Khởi Động Backend (Python FastAPI)

Mở terminal thứ nhất tại thư mục dự án:

```bash
cd backend
```

Tạo hoặc chỉnh sửa file `backend/.env` với nội dung:
```env
HENRIKDEV_API_KEY=HDEV-xxxx-xxxx-xxxx-xxxx
```

Cài đặt các gói phụ thuộc:
```bash
pip install -r requirements.txt
```

Khởi chạy máy chủ FastAPI với Uvicorn:
```bash
python -m uvicorn main:app --reload --port 8000
```

- Backend sẽ chạy tại: `http://localhost:8000`
- Trang tài liệu tương tác Swagger UI: `http://localhost:8000/docs`

---

### 3. Khởi Động Frontend (Vue 3 + Vite)

Mở terminal thứ hai tại thư mục dự án:

```bash
cd frontend
```

Cài đặt các gói phụ thuộc:
```bash
npm install
```

Khởi chạy máy chủ phát triển Vite:
```bash
npm run dev
```

- Mở trình duyệt và truy cập: `http://localhost:5173`

---

## 📡 Danh Sách RESTful API Endpoints

| Phương thức | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/teammates` | Lấy danh sách đồng đội (Lọc theo `q`, `role`, `rank_tier`, `rating_type`, `is_favorite`) |
| `POST` | `/api/teammates` | Thêm mới một đồng đội |
| `GET` | `/api/teammates/{id}` | Lấy chi tiết thông tin một đồng đội |
| `PUT` | `/api/teammates/{id}` | Cập nhật thông tin đồng đội |
| `DELETE` | `/api/teammates/{id}` | Xóa đồng đội khỏi sổ tay |
| `POST` | `/api/teammates/{id}/toggle-favorite` | Bật/tắt trạng thái Cạ Cứng (Favorite) |
| `GET` | `/api/stats` | Lấy số liệu thống kê tổng hợp |
| `GET` | `/api/henrik/account/{name}/{tag}` | Tra cứu thông tin Riot Account & Rank thực tế từ HenrikDev API |
| `GET` | `/api/henrik/recent-matches/{name}/{tag}` | Lấy danh sách trận đấu gần đây & TOÀN BỘ 10 người chơi mỗi trận |
| `POST` | `/api/henrik/import-teammates/{name}/{tag}` | **1-Click Tự Động Lưu Tất Cả Đồng Đội** từ lịch sử trận đấu vào SQLite |
| `POST` | `/api/seed` | Nạp lại bộ dữ liệu mẫu ban đầu |

---

## 🎮 Hướng Dẫn Sử Dụng Nhanh

1. **Tìm kiếm bạn chơi**: Nhập tên game hoặc tag (ví dụ: `TenZ`, `Viper`) vào thanh tìm kiếm.
2. **Lọc theo vị trí**: Bấm các nút Role (*Duelist*, *Controller*,...) để tìm người chơi theo đội hình cần bổ sung.
3. **Thêm đồng đội mới**:
   - Nhấn nút **`+ Thêm Đồng Đội Mới`** màu đỏ ở góc phải trên.
   - Nhập Riot ID, chọn Đặc vụ tủ, Rank hiện tại, Đánh giá phối hợp và các thẻ phong cách.
   - Tích chọn **"Đánh dấu là Cạ Cứng"** nếu đây là bạn thân thường xuyên duo.
   - Bấm **"Lưu Đồng Đội"**.
4. **Đánh dấu Cạ Cứng**: Bấm trực tiếp vào biểu tượng ngôi sao `☆` trên mỗi thẻ người chơi để ghim hoặc bỏ ghim.

Chúc bạn có những trận đấu Valorant thăng hoa và leo rank vù vù cùng những người đồng đội ăn ý! 🚀

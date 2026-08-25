# Hệ thống thu thập thông tin học sinh / phụ huynh

Ứng dụng Streamlit đơn giản, gồm 2 trang:

1. **Trang công khai (Học sinh / Phụ huynh)** — không cần đăng nhập.
   Link: `https://<địa-chỉ-app-của-bạn>/`
2. **Trang quản trị (Nhà trường)** — cần đăng nhập.
   Link: `https://<địa-chỉ-app-của-bạn>/?admin=1`

## Cài đặt & chạy thử trên máy

```bash
pip install -r requirements.txt
streamlit run app.py
```

Sau đó mở:
- `http://localhost:8501` → trang phụ huynh
- `http://localhost:8501/?admin=1` → trang nhà trường

## Tài khoản nhà trường (mặc định)

- Tài khoản: `nhatruong`
- Mật khẩu: `123456`

**Quan trọng — đổi mật khẩu trước khi dùng thật:**
Tạo file `.streamlit/secrets.toml` với nội dung:

```toml
admin_username = "ten_dang_nhap_cua_ban"
admin_password = "mat_khau_manh"
admin_recovery_code = "ma_khoi_phuc_bi_mat"
```

`admin_recovery_code` dùng cho chức năng **"Quên mật khẩu?"** ở trang đăng nhập —
chỉ người quản trị kỹ thuật mới nên biết mã này. Nếu không đặt trong
`secrets.toml`, hệ thống dùng mã mặc định `NAMTHAISON-RESET` (nên đổi ngay).

## Đổi / khôi phục mật khẩu ngay trong ứng dụng

- **Đã đăng nhập:** vào trang quản trị → mở mục "🔑 Đổi mật khẩu đăng nhập",
  nhập mật khẩu hiện tại và mật khẩu mới.
- **Quên mật khẩu:** ở trang đăng nhập, mở mục "Quên mật khẩu?", nhập mã khôi
  phục (`admin_recovery_code`) và đặt mật khẩu mới.

Mật khẩu sau khi đổi được lưu (dạng đã băm, không lưu chữ rõ) trong chính
`data/school.db`, ghi đè lên mật khẩu mặc định trong `secrets.toml`. Nếu
deploy trên nền tảng có "ephemeral storage", mật khẩu đã đổi có thể mất khi
container khởi động lại — khi đó hệ thống sẽ quay về dùng mật khẩu trong
`secrets.toml`.

## Đổi tên trường

Mở file `public_form.py`, sửa dòng:
```python
SCHOOL_NAME = "TRƯỜNG TIỂU HỌC ABC"
```

## Cấu trúc thư mục

```
school_form_app/
├── app.py            # Điểm khởi chạy, điều hướng 2 trang
├── public_form.py     # Trang biểu mẫu công khai
├── admin_page.py       # Trang quản trị nhà trường
├── db.py                # Xử lý cơ sở dữ liệu SQLite
├── requirements.txt
├── data/
│   ├── school.db       # Cơ sở dữ liệu (tự tạo khi chạy)
│   └── uploads/         # Tệp đính kèm phụ huynh gửi lên
└── README.md
```

## Triển khai lên Streamlit Community Cloud (miễn phí)

1. Đưa toàn bộ thư mục này lên một repository GitHub.
2. Vào https://share.streamlit.io → New app → chọn repo, chọn `app.py`.
3. Trong phần **Settings → Secrets**, thêm:
   ```toml
   admin_username = "..."
   admin_password = "..."
   ```
4. Gửi link chính (không có `?admin=1`) cho phụ huynh.
   Chỉ nhà trường mới dùng link có `?admin=1`.

## Lưu trữ bền vững với Google Sheets (chống mất dữ liệu khi container restart)

**Vấn đề:** Streamlit Community Cloud dùng "ephemeral storage" — file
`data/school.db` (SQLite) chỉ tồn tại trong phiên chạy hiện tại. Khi app
"ngủ" do không ai truy cập, khi bạn deploy lại code, hoặc container tự khởi
động lại vì bất kỳ lý do gì, toàn bộ dữ liệu học sinh đã điền trước đó sẽ
biến mất.

**Giải pháp đã tích hợp sẵn (file `gsheets.py`):** mỗi khi có phiếu mới được
gửi / sửa / xóa, hệ thống tự động ghi thay đổi đó lên một Google Sheet. Khi
app khởi động lại mà SQLite đang trống (vừa bị reset), hệ thống tự tải lại
toàn bộ dữ liệu từ Google Sheet vào SQLite — nhờ vậy trang quản trị luôn thấy
đủ hồ sơ cũ, không còn bị "0 hồ sơ" oan uổng. Nếu chưa cấu hình bước dưới
đây, ứng dụng vẫn chạy bình thường như cũ (chỉ là không có lớp lưu bền vững).

### Bước 1 — Tạo Google Sheet

Tạo một Google Sheet trống bất kỳ (tên gì cũng được), giữ lại đường link của
nó, ví dụ: `https://docs.google.com/spreadsheets/d/1AbC.../edit`.

### Bước 2 — Tạo Service Account trên Google Cloud

1. Vào https://console.cloud.google.com → tạo project mới (hoặc dùng project có sẵn).
2. Bật 2 API: **Google Sheets API** và **Google Drive API**.
3. Vào **IAM & Admin → Service Accounts → Create Service Account**, đặt tên
   tuỳ ý, không cần cấp quyền project-level, bấm Done.
4. Mở service account vừa tạo → tab **Keys → Add Key → Create new key → JSON**.
   File JSON sẽ tự tải về máy — đây là thông tin bí mật, không chia sẻ công khai.
5. Mở file JSON đó, copy giá trị `client_email` (dạng
   `ten-nao-do@ten-project.iam.gserviceaccount.com`).

### Bước 3 — Chia sẻ quyền chỉnh sửa Sheet cho Service Account

Mở lại Google Sheet ở Bước 1 → bấm **Share** → dán địa chỉ `client_email` ở
trên vào, chọn quyền **Editor** → Share.

### Bước 4 — Khai báo secrets

Trong **Settings → Secrets** của Streamlit Community Cloud (hoặc file
`.streamlit/secrets.toml` khi chạy máy cá nhân), thêm:

```toml
gsheet_url = "https://docs.google.com/spreadsheets/d/1AbC.../edit"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "ten-nao-do@ten-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

Toàn bộ các dòng trong khối `[gcp_service_account]` copy trực tiếp từ file
JSON đã tải ở Bước 2 (đổi tên field cho khớp key TOML ở trên, giữ nguyên giá
trị). Lưu ý riêng `private_key`: giữ nguyên các ký tự `\n` bên trong dấu
ngoặc kép, không tự ý xuống dòng thật.

Sau khi lưu secrets, redeploy/reload app. Lần gửi phiếu tiếp theo sẽ tự động
xuất hiện một worksheet tên `records` trong Google Sheet, chứa toàn bộ dữ
liệu và tự cập nhật liên tục từ đó về sau.

## Ghi chú

- Google Sheets đóng vai trò lưu trữ bền vững cho **hồ sơ học sinh**. Mật
  khẩu quản trị đã đổi (lưu trong `settings` của SQLite) hiện **chưa** được
  đồng bộ — nếu container restart mà bạn đã từng đổi mật khẩu, hệ thống sẽ
  quay về mật khẩu mặc định trong `secrets.toml`.
- Nếu chưa/không muốn cấu hình Google Sheets, vẫn nên định kỳ bấm "Xuất
  Excel" để sao lưu thủ công.
- Trang phụ huynh không hiển thị dữ liệu của người khác — đúng như yêu cầu.

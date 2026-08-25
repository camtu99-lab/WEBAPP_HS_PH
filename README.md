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

## Ghi chú

- Dữ liệu lưu trong file SQLite `data/school.db`. Nếu deploy trên nền tảng có
  "ephemeral storage" (dữ liệu mất khi khởi động lại container), nên định kỳ
  bấm "Xuất Excel" để sao lưu, hoặc chuyển sang cơ sở dữ liệu ngoài
  (ví dụ: PostgreSQL/Supabase) khi cần lưu trữ lâu dài, quy mô lớn.
- Trang phụ huynh không hiển thị dữ liệu của người khác — đúng như yêu cầu.

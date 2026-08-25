"""
db.py - Quản lý cơ sở dữ liệu SQLite cho hệ thống thu thập thông tin học sinh/phụ huynh.
Trường THCS và THPT Nam Thái Sơn.
"""
import sqlite3
import os
import datetime
import hashlib
import secrets
import pandas as pd
import gsheets

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "school.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data", "uploads")
# File Excel tổng hợp chung - tự động cập nhật mỗi khi có học sinh gửi phiếu
MASTER_EXCEL_PATH = os.path.join(os.path.dirname(__file__), "data", "DANH_SACH_TONG_HOP.xlsx")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Danh sách lớp cố định để chọn (tránh gõ sai)
CLASS_LIST = [
    "6A1", "6A2", "6A3", "6A4",
    "7A1", "7A2", "7A3", "7A4",
    "8A1", "8A2", "8A3", "8A4",
    "9A1", "9A2", "9A3", "9A4",
    "10A1", "10A2", "10A3",
    "11A1", "11A2", "11A3",
    "12A1", "12A2", "12A3",
]

EXPECTED_COLUMNS = [
    "id",
    "hoten_hs", "ngaysinh", "gioitinh", "lop", "namhoc", "dantoc",
    "diachi_hs", "sdt_hs", "email_hs",
    "hoten_cha", "ngaysinh_cha", "sdt_cha", "email_cha", "nghenghiep_cha", "noilamviec_cha",
    "hoten_me", "ngaysinh_me", "sdt_me", "email_me", "nghenghiep_me", "noilamviec_me",
    "hoten_giamho", "quanhe_giamho", "sdt_giamho", "email_giamho", "diachi_giamho",
    "trang_thai", "created_at", "updated_at",
]

COLUMN_LABELS_VI = {
    "id": "Mã hồ sơ",
    "hoten_hs": "Họ tên học sinh", "ngaysinh": "Ngày sinh HS", "gioitinh": "Giới tính",
    "lop": "Lớp", "namhoc": "Năm học", "dantoc": "Dân tộc",
    "diachi_hs": "Địa chỉ hiện tại", "sdt_hs": "SĐT học sinh", "email_hs": "Email học sinh",
    "hoten_cha": "Họ tên cha", "ngaysinh_cha": "Ngày sinh cha", "sdt_cha": "SĐT cha",
    "email_cha": "Email cha", "nghenghiep_cha": "Nghề nghiệp cha", "noilamviec_cha": "Nơi làm việc cha",
    "hoten_me": "Họ tên mẹ", "ngaysinh_me": "Ngày sinh mẹ", "sdt_me": "SĐT mẹ",
    "email_me": "Email mẹ", "nghenghiep_me": "Nghề nghiệp mẹ", "noilamviec_me": "Nơi làm việc mẹ",
    "hoten_giamho": "Họ tên người giám hộ/liên hệ khác", "quanhe_giamho": "Quan hệ với học sinh",
    "sdt_giamho": "SĐT người giám hộ", "email_giamho": "Email người giám hộ",
    "diachi_giamho": "Địa chỉ người giám hộ",
    "trang_thai": "Trạng thái", "created_at": "Ngày gửi", "updated_at": "Cập nhật lần cuối",
}


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _table_matches_schema(conn) -> bool:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(records)")
    cols = [r[1] for r in cur.fetchall()]
    if not cols:
        return False
    return set(cols) == set(EXPECTED_COLUMNS)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records'")
    exists = cur.fetchone() is not None

    if exists and not _table_matches_schema(conn):
        # Cấu trúc form đã thay đổi (thêm/bớt trường) -> tạo lại bảng theo cấu trúc mới.
        # Lưu ý: dữ liệu cũ theo cấu trúc trước đó sẽ không tương thích, nên bảng cũ bị xóa.
        cur.execute("DROP TABLE IF EXISTS records")
        conn.commit()
        exists = False

    if not exists:
        cur.execute("""
            CREATE TABLE records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hoten_hs TEXT NOT NULL,
                ngaysinh TEXT,
                gioitinh TEXT,
                lop TEXT NOT NULL,
                namhoc TEXT,
                dantoc TEXT,
                diachi_hs TEXT,
                sdt_hs TEXT,
                email_hs TEXT,
                hoten_cha TEXT,
                ngaysinh_cha TEXT,
                sdt_cha TEXT,
                email_cha TEXT,
                nghenghiep_cha TEXT,
                noilamviec_cha TEXT,
                hoten_me TEXT,
                ngaysinh_me TEXT,
                sdt_me TEXT,
                email_me TEXT,
                nghenghiep_me TEXT,
                noilamviec_me TEXT,
                hoten_giamho TEXT,
                quanhe_giamho TEXT,
                sdt_giamho TEXT,
                email_giamho TEXT,
                diachi_giamho TEXT,
                trang_thai TEXT DEFAULT 'Mới',
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.commit()
    conn.close()
    _restore_from_gsheet_if_empty()
    sync_master_excel()


def _restore_from_gsheet_if_empty():
    """Nếu bảng SQLite đang trống (ví dụ do Streamlit Cloud vừa khởi động lại
    container và xóa mất file school.db cũ), tải lại toàn bộ hồ sơ đã lưu
    trên Google Sheet để khôi phục - tránh hiện '0 hồ sơ' oan uổng dù dữ liệu
    thật ra vẫn còn trên Google Sheet."""
    if not gsheets.is_configured():
        return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM records")
    count = cur.fetchone()[0]
    if count > 0:
        conn.close()
        return

    rows = gsheets.fetch_all_rows(EXPECTED_COLUMNS)
    if not rows:
        conn.close()
        return

    for row in rows:
        try:
            row_id = int(row.get("id"))
        except (TypeError, ValueError):
            continue
        values = [row.get(c, "") for c in EXPECTED_COLUMNS]
        placeholders = ",".join(["?"] * len(EXPECTED_COLUMNS))
        columns_sql = ",".join(EXPECTED_COLUMNS)
        cur.execute(
            f"INSERT OR REPLACE INTO records ({columns_sql}) VALUES ({placeholders})",
            values,
        )
    conn.commit()
    conn.close()


def sync_master_excel():
    """Ghi lại toàn bộ dữ liệu hiện có ra file Excel tổng hợp chung.
    Được gọi tự động sau mỗi lần thêm / sửa / xóa để file luôn cập nhật mới nhất."""
    df = get_all_records()
    export_df = df.rename(columns=COLUMN_LABELS_VI)
    try:
        export_df.to_excel(MASTER_EXCEL_PATH, index=False, sheet_name="DanhSach", engine="openpyxl")
    except Exception:
        # Không để lỗi ghi file làm hỏng luồng thêm/sửa/xóa dữ liệu chính (SQLite)
        pass


def add_record(data: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fields = [c for c in EXPECTED_COLUMNS if c not in ("id", "trang_thai", "created_at", "updated_at")]
    placeholders = ",".join(["?"] * (len(fields) + 3))
    columns_sql = ",".join(fields + ["trang_thai", "created_at", "updated_at"])
    values = [data.get(f, "") for f in fields] + ["Mới", now, now]
    cur.execute(f"INSERT INTO records ({columns_sql}) VALUES ({placeholders})", values)
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    sync_master_excel()
    gsheets.upsert_row(get_record(new_id), EXPECTED_COLUMNS)
    return new_id


def get_all_records() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM records ORDER BY id DESC", conn)
    conn.close()
    return df


def get_record(record_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM records WHERE id=?", (record_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_record(record_id: int, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fields = [c for c in EXPECTED_COLUMNS if c not in ("id", "created_at", "updated_at")]
    set_sql = ",".join([f"{f}=?" for f in fields]) + ", updated_at=?"
    values = [data.get(f, "") for f in fields] + [now, record_id]
    cur.execute(f"UPDATE records SET {set_sql} WHERE id=?", values)
    conn.commit()
    conn.close()
    sync_master_excel()
    gsheets.upsert_row(get_record(record_id), EXPECTED_COLUMNS)


def delete_record(record_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    sync_master_excel()
    gsheets.delete_row(record_id, EXPECTED_COLUMNS)


def get_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM records")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM records WHERE trang_thai='Mới'")
    moi = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM records WHERE trang_thai='Đã xử lý'")
    daxuly = cur.fetchone()[0]
    conn.close()
    return {"total": total, "moi": moi, "daxuly": daxuly}


def get_class_list():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT lop FROM records ORDER BY lop")
    rows = [r[0] for r in cur.fetchall() if r[0]]
    conn.close()
    return rows


# ---------------- Cài đặt chung (settings) & mật khẩu đăng nhập ----------------

def get_setting(key: str, default=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(key: str, value: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


def hash_password(password: str, salt: str = None) -> str:
    """Băm mật khẩu bằng PBKDF2-HMAC-SHA256. Trả về chuỗi 'salt$hash' (dạng hex)."""
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    ).hex()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """So khớp mật khẩu người dùng nhập với chuỗi đã băm lưu trong settings."""
    try:
        salt, _ = stored_hash.split("$", 1)
    except (ValueError, AttributeError):
        return False
    return hash_password(password, salt) == stored_hash

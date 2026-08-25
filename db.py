"""
db.py - Quản lý cơ sở dữ liệu SQLite cho hệ thống thu thập thông tin học sinh/phụ huynh.
Trường THCS và THPT Nam Thái Sơn.
"""
import sqlite3
import os
import datetime
import pandas as pd

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
    sync_master_excel()


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


def delete_record(record_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    sync_master_excel()


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

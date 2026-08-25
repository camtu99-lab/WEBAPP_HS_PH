"""
db.py - Quản lý cơ sở dữ liệu SQLite cho hệ thống thu thập thông tin học sinh/phụ huynh.
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


def sync_master_excel():
    """Ghi lại toàn bộ dữ liệu hiện có ra file Excel tổng hợp chung.
    Được gọi tự động sau mỗi lần thêm / sửa / xóa để file luôn cập nhật mới nhất."""
    df = get_all_records()
    export_df = df.rename(columns={
        "id": "Mã hồ sơ", "hoten_hs": "Họ tên học sinh", "ngaysinh": "Ngày sinh",
        "gioitinh": "Giới tính", "lop": "Lớp", "diachi_hs": "Địa chỉ học sinh",
        "hoten_ph": "Họ tên phụ huynh", "quanhe": "Quan hệ", "sdt": "Số điện thoại",
        "email": "Email", "diachi_ph": "Địa chỉ phụ huynh",
        "noidung": "Nội dung trao đổi", "trang_thai": "Trạng thái",
        "created_at": "Ngày gửi", "updated_at": "Cập nhật lần cuối",
    })
    export_df = export_df.drop(columns=["tep_dinhkem"], errors="ignore")
    try:
        export_df.to_excel(MASTER_EXCEL_PATH, index=False, sheet_name="DanhSach", engine="openpyxl")
    except Exception:
        # Không để lỗi ghi file làm hỏng luồng thêm/sửa/xóa dữ liệu chính (SQLite)
        pass


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hoten_hs TEXT NOT NULL,
            ngaysinh TEXT,
            gioitinh TEXT,
            lop TEXT NOT NULL,
            diachi_hs TEXT,
            hoten_ph TEXT NOT NULL,
            quanhe TEXT,
            sdt TEXT NOT NULL,
            email TEXT,
            diachi_ph TEXT,
            noidung TEXT,
            tep_dinhkem TEXT,
            trang_thai TEXT DEFAULT 'Mới',
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    sync_master_excel()


def add_record(data: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO records
        (hoten_hs, ngaysinh, gioitinh, lop, diachi_hs,
         hoten_ph, quanhe, sdt, email, diachi_ph,
         noidung, tep_dinhkem, trang_thai, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("hoten_hs"), data.get("ngaysinh"), data.get("gioitinh"),
        data.get("lop"), data.get("diachi_hs"),
        data.get("hoten_ph"), data.get("quanhe"), data.get("sdt"),
        data.get("email"), data.get("diachi_ph"),
        data.get("noidung"), data.get("tep_dinhkem"),
        "Mới", now, now
    ))
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
    cur.execute("""
        UPDATE records SET
            hoten_hs=?, ngaysinh=?, gioitinh=?, lop=?, diachi_hs=?,
            hoten_ph=?, quanhe=?, sdt=?, email=?, diachi_ph=?,
            noidung=?, trang_thai=?, updated_at=?
        WHERE id=?
    """, (
        data.get("hoten_hs"), data.get("ngaysinh"), data.get("gioitinh"),
        data.get("lop"), data.get("diachi_hs"),
        data.get("hoten_ph"), data.get("quanhe"), data.get("sdt"),
        data.get("email"), data.get("diachi_ph"),
        data.get("noidung"), data.get("trang_thai"),
        now, record_id
    ))
    conn.commit()
    conn.close()
    sync_master_excel()


def delete_record(record_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT tep_dinhkem FROM records WHERE id=?", (record_id,))
    row = cur.fetchone()
    if row and row["tep_dinhkem"]:
        fpath = os.path.join(UPLOAD_DIR, row["tep_dinhkem"])
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except OSError:
                pass
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

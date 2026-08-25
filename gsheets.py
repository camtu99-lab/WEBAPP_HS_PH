"""
gsheets.py - Đồng bộ với Google Sheets để dữ liệu KHÔNG bị mất khi Streamlit
Community Cloud khởi động lại container (SQLite lưu trên đĩa cục bộ sẽ bị xóa
mỗi khi container restart - đây là nguyên nhân "mất dữ liệu cũ" khi thoát app).

Cách hoạt động:
- Mỗi khi thêm / sửa / xóa hồ sơ trong SQLite (db.py), hàm tương ứng ở đây
  cũng được gọi để ghi thay đổi đó lên Google Sheet ngay lập tức.
- Khi ứng dụng khởi động (init_db trong db.py) và bảng SQLite đang trống
  (vừa bị reset do container restart), dữ liệu sẽ được TẢI NGƯỢC LẠI từ
  Google Sheet vào SQLite, để trang quản trị vẫn thấy đầy đủ hồ sơ cũ.
- Nếu chưa cấu hình Google Sheets (chưa có secrets), toàn bộ hàm ở đây sẽ tự
  bỏ qua (no-op) - ứng dụng vẫn chạy bình thường với SQLite như trước, chỉ là
  không có lớp lưu trữ bền vững.

Cách cấu hình: xem hướng dẫn trong README.md, mục "Lưu trữ bền vững với
Google Sheets".
"""
import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
    _GSPREAD_AVAILABLE = True
except ImportError:
    _GSPREAD_AVAILABLE = False

WORKSHEET_NAME = "records"

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_cache = {}


def is_configured() -> bool:
    """True nếu đã cài thư viện gspread và đã khai báo secrets cần thiết."""
    if not _GSPREAD_AVAILABLE:
        return False
    try:
        has_creds = "gcp_service_account" in st.secrets
        has_sheet = ("gsheet_id" in st.secrets) or ("gsheet_url" in st.secrets)
        return has_creds and has_sheet
    except Exception:
        return False


def _get_client():
    if "client" in _cache:
        return _cache["client"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=_SCOPES)
    client = gspread.authorize(creds)
    _cache["client"] = client
    return client


def _get_worksheet():
    """Mở Google Sheet (workbook), tạo worksheet 'records' nếu chưa có."""
    if "worksheet" in _cache:
        return _cache["worksheet"]
    client = _get_client()
    if "gsheet_id" in st.secrets:
        sh = client.open_by_key(st.secrets["gsheet_id"])
    else:
        sh = client.open_by_url(st.secrets["gsheet_url"])
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=2000, cols=30)
    _cache["worksheet"] = ws
    return ws


def ensure_header(columns: list):
    """Đảm bảo dòng đầu tiên của sheet là danh sách cột đúng thứ tự."""
    if not is_configured():
        return
    try:
        ws = _get_worksheet()
        first_row = ws.row_values(1)
        if first_row != columns:
            ws.update("A1", [columns])
    except Exception:
        pass  # Không để lỗi kết nối Google Sheets làm hỏng luồng chính


def fetch_all_rows(columns: list):
    """Tải toàn bộ dữ liệu hiện có từ Google Sheet, trả về list[dict]."""
    if not is_configured():
        return []
    try:
        ws = _get_worksheet()
        rows = ws.get_all_records(expected_headers=columns)
        return rows
    except Exception:
        return []


def upsert_row(record: dict, columns: list):
    """Ghi một hồ sơ lên Google Sheet: cập nhật nếu 'id' đã tồn tại, thêm mới nếu chưa."""
    if not is_configured():
        return
    try:
        ws = _get_worksheet()
        ensure_header(columns)
        id_col = columns.index("id") + 1
        cell = None
        try:
            cell = ws.find(str(record["id"]), in_column=id_col)
        except Exception:
            cell = None
        row_values = [str(record.get(c, "") if record.get(c) is not None else "") for c in columns]
        if cell:
            ws.update(f"A{cell.row}", [row_values])
        else:
            ws.append_row(row_values, value_input_option="USER_ENTERED")
    except Exception:
        pass  # Lỗi mạng/quyền truy cập không được làm gián đoạn thao tác chính trên SQLite


def delete_row(record_id, columns: list):
    """Xóa dòng tương ứng với id đó trên Google Sheet."""
    if not is_configured():
        return
    try:
        ws = _get_worksheet()
        id_col = columns.index("id") + 1
        cell = ws.find(str(record_id), in_column=id_col)
        if cell:
            ws.delete_rows(cell.row)
    except Exception:
        pass

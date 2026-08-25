"""
admin_page.py - Trang quản trị dành cho nhà trường.
Đăng nhập -> Xem danh sách -> Tìm kiếm -> Quản lý -> Xuất Excel.
"""
import streamlit as st
import pandas as pd
import io
import os
import db

# ---- Tài khoản nhà trường (đơn giản, có thể đổi trong Settings -> Secrets khi deploy) ----
ADMIN_USERNAME = st.secrets.get("admin_username", "nhatruong") if hasattr(st, "secrets") else "nhatruong"
ADMIN_PASSWORD = st.secrets.get("admin_password", "123456") if hasattr(st, "secrets") else "123456"

try:
    ADMIN_USERNAME = st.secrets["admin_username"]
    ADMIN_PASSWORD = st.secrets["admin_password"]
except Exception:
    ADMIN_USERNAME = "nhatruong"
    ADMIN_PASSWORD = "123456"

COLUMN_LABELS = {
    "hoten_hs": "Học sinh",
    "lop": "Lớp",
    "hoten_ph": "Phụ huynh",
    "sdt": "Số điện thoại",
    "trang_thai": "Trạng thái",
}


def render_login():
    st.markdown("""
        <style>
        .main .block-container {max-width: 420px; padding-top: 4rem;}
        div.stButton > button {
            width: 100%; height: 3em; font-size: 1.1em; font-weight: 700;
            border-radius: 8px; background-color: #1a73e8; color: white; border: none;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🔐 Đăng nhập Nhà trường</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Tài khoản")
        password = st.text_input("Mật khẩu", type="password")
        ok = st.form_submit_button("Đăng nhập")
        if ok:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu.")


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    export_df = df.rename(columns={
        "hoten_hs": "Họ tên học sinh", "ngaysinh": "Ngày sinh", "gioitinh": "Giới tính",
        "lop": "Lớp", "diachi_hs": "Địa chỉ học sinh",
        "hoten_ph": "Họ tên phụ huynh", "quanhe": "Quan hệ", "sdt": "Số điện thoại",
        "email": "Email", "diachi_ph": "Địa chỉ phụ huynh",
        "noidung": "Nội dung trao đổi", "trang_thai": "Trạng thái",
        "created_at": "Ngày gửi", "updated_at": "Cập nhật lần cuối", "id": "Mã hồ sơ"
    })
    export_df = export_df.drop(columns=["tep_dinhkem"], errors="ignore")
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="DanhSach")
    return output.getvalue()


def render_detail_dialog(record_id: int):
    record = db.get_record(record_id)
    if not record:
        st.warning("Hồ sơ không tồn tại (có thể đã bị xóa).")
        return

    st.markdown("#### 📄 Chi tiết hồ sơ")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Học sinh**")
        st.write(f"Họ tên: {record['hoten_hs']}")
        st.write(f"Ngày sinh: {record['ngaysinh'] or '-'}")
        st.write(f"Giới tính: {record['gioitinh'] or '-'}")
        st.write(f"Lớp: {record['lop']}")
        st.write(f"Địa chỉ: {record['diachi_hs'] or '-'}")
    with c2:
        st.markdown("**Phụ huynh**")
        st.write(f"Họ tên: {record['hoten_ph']}")
        st.write(f"Quan hệ: {record['quanhe'] or '-'}")
        st.write(f"SĐT: {record['sdt']}")
        st.write(f"Email: {record['email'] or '-'}")
        st.write(f"Địa chỉ: {record['diachi_ph'] or '-'}")

    st.markdown("**Nội dung cần trao đổi**")
    st.write(record["noidung"] or "(Không có)")

    if record["tep_dinhkem"]:
        fpath = os.path.join(db.UPLOAD_DIR, record["tep_dinhkem"])
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                st.download_button("📎 Tải tệp đính kèm", f, file_name=record["tep_dinhkem"])

    st.caption(f"Gửi lúc: {record['created_at']} | Cập nhật: {record['updated_at']}")

    st.markdown("---")
    st.markdown("#### ✏️ Chỉnh sửa")
    with st.form(f"edit_form_{record_id}"):
        e1, e2 = st.columns(2)
        with e1:
            hoten_hs = st.text_input("Họ tên học sinh", value=record["hoten_hs"])
            ngaysinh = st.text_input("Ngày sinh (dd/mm/yyyy)", value=record["ngaysinh"] or "")
            gioitinh = st.selectbox("Giới tính", ["", "Nam", "Nữ", "Khác"],
                                     index=["", "Nam", "Nữ", "Khác"].index(record["gioitinh"]) if record["gioitinh"] in ["", "Nam", "Nữ", "Khác"] else 0)
            lop = st.text_input("Lớp", value=record["lop"])
            diachi_hs = st.text_input("Địa chỉ học sinh", value=record["diachi_hs"] or "")
        with e2:
            hoten_ph = st.text_input("Họ tên phụ huynh", value=record["hoten_ph"])
            quanhe = st.text_input("Quan hệ", value=record["quanhe"] or "")
            sdt = st.text_input("Số điện thoại", value=record["sdt"])
            email = st.text_input("Email", value=record["email"] or "")
            diachi_ph = st.text_input("Địa chỉ phụ huynh", value=record["diachi_ph"] or "")

        noidung = st.text_area("Nội dung cần trao đổi", value=record["noidung"] or "")
        trang_thai = st.selectbox("Trạng thái", ["Mới", "Đã xử lý"],
                                   index=0 if record["trang_thai"] == "Mới" else 1)

        col_save, col_del = st.columns(2)
        with col_save:
            save = st.form_submit_button("💾 Lưu thay đổi", use_container_width=True)
        with col_del:
            delete = st.form_submit_button("🗑️ Xóa hồ sơ", use_container_width=True)

        if save:
            db.update_record(record_id, {
                "hoten_hs": hoten_hs, "ngaysinh": ngaysinh, "gioitinh": gioitinh,
                "lop": lop, "diachi_hs": diachi_hs,
                "hoten_ph": hoten_ph, "quanhe": quanhe, "sdt": sdt,
                "email": email, "diachi_ph": diachi_ph,
                "noidung": noidung, "trang_thai": trang_thai,
            })
            st.success("Đã lưu thay đổi.")
            st.session_state.viewing_id = None
            st.rerun()

        if delete:
            db.delete_record(record_id)
            st.success("Đã xóa hồ sơ.")
            st.session_state.viewing_id = None
            st.rerun()

    if st.button("← Đóng"):
        st.session_state.viewing_id = None
        st.rerun()


def render_admin_dashboard():
    st.markdown("""
        <style>
        div.stButton > button {border-radius: 6px;}
        </style>
    """, unsafe_allow_html=True)

    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown("## 📋 QUẢN LÝ THÔNG TIN HỌC SINH")
    with top_r:
        if st.button("Đăng xuất"):
            st.session_state.admin_logged_in = False
            st.rerun()

    # ---- File Excel tổng hợp chung: tự động cập nhật mỗi khi có phiếu mới ----
    if os.path.exists(db.MASTER_EXCEL_PATH):
        with open(db.MASTER_EXCEL_PATH, "rb") as f:
            st.download_button(
                "📊 TẢI FILE EXCEL TỔNG HỢP (tự động cập nhật mới nhất)",
                data=f.read(),
                file_name="DANH_SACH_TONG_HOP.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        st.caption("File này tự động cập nhật ngay khi có học sinh gửi phiếu mới, "
                    "hoặc khi nhà trường sửa/xóa hồ sơ — không cần thao tác gì thêm.")

    # Nếu đang xem chi tiết 1 hồ sơ
    if st.session_state.get("viewing_id"):
        render_detail_dialog(st.session_state.viewing_id)
        return

    stats = db.get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng số hồ sơ", stats["total"])
    c2.metric("Hồ sơ mới", stats["moi"])
    c3.metric("Đã xử lý", stats["daxuly"])

    st.markdown("---")

    df = db.get_all_records()

    # ---- Tìm kiếm & lọc ----
    fc1, fc2, fc3 = st.columns([3, 2, 2])
    with fc1:
        keyword = st.text_input("🔍 Tìm kiếm (tên học sinh, phụ huynh, SĐT)")
    with fc2:
        classes = ["Tất cả"] + db.get_class_list()
        selected_class = st.selectbox("Lọc theo lớp", classes)
    with fc3:
        status_filter = st.selectbox("Lọc theo trạng thái", ["Tất cả", "Mới", "Đã xử lý"])

    filtered = df.copy()
    if keyword:
        kw = keyword.strip().lower()
        filtered = filtered[
            filtered["hoten_hs"].str.lower().str.contains(kw, na=False) |
            filtered["hoten_ph"].str.lower().str.contains(kw, na=False) |
            filtered["sdt"].astype(str).str.contains(kw, na=False)
        ]
    if selected_class != "Tất cả":
        filtered = filtered[filtered["lop"] == selected_class]
    if status_filter != "Tất cả":
        filtered = filtered[filtered["trang_thai"] == status_filter]

    # ---- Nút xuất Excel theo kết quả đang lọc/tìm kiếm ----
    exp_col1, exp_col2 = st.columns([1, 5])
    with exp_col1:
        excel_bytes = to_excel_bytes(filtered if len(filtered) else df.iloc[0:0])
        st.download_button(
            "⬇️ Xuất Excel (theo bộ lọc hiện tại)",
            data=excel_bytes,
            file_name="danh_sach_da_loc.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.markdown(f"**Kết quả: {len(filtered)} hồ sơ**")

    if len(filtered) == 0:
        st.info("Không có hồ sơ nào phù hợp.")
        return

    # ---- Bảng danh sách ----
    header = st.columns([2, 1, 2, 2, 1.3, 1])
    header[0].markdown("**Học sinh**")
    header[1].markdown("**Lớp**")
    header[2].markdown("**Phụ huynh**")
    header[3].markdown("**Số điện thoại**")
    header[4].markdown("**Trạng thái**")
    header[5].markdown("**Thao tác**")
    st.markdown("<hr style='margin:0.2em 0;'>", unsafe_allow_html=True)

    for _, row in filtered.iterrows():
        cols = st.columns([2, 1, 2, 2, 1.3, 1])
        cols[0].write(row["hoten_hs"])
        cols[1].write(row["lop"])
        cols[2].write(row["hoten_ph"])
        cols[3].write(row["sdt"])
        badge = "🟢 Đã xử lý" if row["trang_thai"] == "Đã xử lý" else "🟡 Mới"
        cols[4].write(badge)
        if cols[5].button("Xem", key=f"view_{row['id']}"):
            st.session_state.viewing_id = int(row["id"])
            st.rerun()


def render_admin_page():
    if not st.session_state.get("admin_logged_in"):
        render_login()
    else:
        render_admin_dashboard()

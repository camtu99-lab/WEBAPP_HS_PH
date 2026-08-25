"""
admin_page.py - Trang quản trị dành cho nhà trường.
Đăng nhập -> Xem danh sách -> Tìm kiếm -> Quản lý -> Xuất Excel.
"""
import streamlit as st
import pandas as pd
import io
import os
import db
import theme

try:
    ADMIN_USERNAME = st.secrets["admin_username"]
    ADMIN_PASSWORD = st.secrets["admin_password"]
except Exception:
    ADMIN_USERNAME = "nhatruong"
    ADMIN_PASSWORD = "123456"

# Mã khôi phục dùng cho chức năng "Quên mật khẩu" (nên đặt trong secrets.toml khi dùng thật)
try:
    ADMIN_RECOVERY_CODE = st.secrets["admin_recovery_code"]
except Exception:
    ADMIN_RECOVERY_CODE = "NAMTHAISON-RESET"

GIOITINH_OPTIONS = ["", "Nam", "Nữ", "Khác"]


def _check_password(password: str) -> bool:
    """Kiểm tra mật khẩu: ưu tiên mật khẩu đã đổi (lưu hash trong DB),
    nếu chưa từng đổi thì dùng mật khẩu mặc định/secrets.toml."""
    stored_hash = db.get_setting("admin_password_hash")
    if stored_hash:
        return db.verify_password(password, stored_hash)
    return password == ADMIN_PASSWORD


def render_login():
    # ---- Nền gradient, illustration giáo dục nổi nhẹ, glassmorphism cho form ----
    theme.inject_theme(decor=True)

    st.markdown("""
        <style>
        .main .block-container {max-width: 420px; padding-top: 4rem;}
        div.stButton > button, div.stFormSubmitButton > button {
            width: 100%; height: 3em; font-size: 1.1em; font-weight: 700;
            border-radius: 14px;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<h2 class='edu-gradient-title' style='text-align:center;'>🔐 Đăng nhập Nhà trường</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Tài khoản")
        password = st.text_input("Mật khẩu", type="password")
        ok = st.form_submit_button("Đăng nhập")
        if ok:
            if username == ADMIN_USERNAME and _check_password(password):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu.")

    with st.expander("Quên mật khẩu?"):
        st.caption(
            "Nhập mã khôi phục (do người quản trị kỹ thuật của trường cung cấp) "
            "để đặt lại mật khẩu đăng nhập."
        )
        with st.form("forgot_password_form"):
            recovery_code = st.text_input("Mã khôi phục", type="password")
            new_password = st.text_input("Mật khẩu mới", type="password")
            confirm_password = st.text_input("Nhập lại mật khẩu mới", type="password")
            reset_ok = st.form_submit_button("Đặt lại mật khẩu")
            if reset_ok:
                if recovery_code != ADMIN_RECOVERY_CODE:
                    st.error("Mã khôi phục không đúng.")
                elif not new_password or len(new_password) < 6:
                    st.error("Mật khẩu mới phải có ít nhất 6 ký tự.")
                elif new_password != confirm_password:
                    st.error("Mật khẩu nhập lại không khớp.")
                else:
                    db.set_setting("admin_password_hash", db.hash_password(new_password))
                    st.success("Đã đặt lại mật khẩu thành công. Vui lòng đăng nhập lại với mật khẩu mới.")


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    export_df = df.rename(columns=db.COLUMN_LABELS_VI)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="DanhSach")
    return output.getvalue()


def _text(label, value, key=None):
    return st.text_input(label, value=value or "", key=key)


def render_detail_dialog(record_id: int):
    record = db.get_record(record_id)
    if not record:
        st.warning("Hồ sơ không tồn tại (có thể đã bị xóa).")
        return

    st.markdown("#### 📄 Chi tiết hồ sơ")

    st.markdown("**📘 Học sinh**")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"Họ tên: {record['hoten_hs']}")
        st.write(f"Ngày sinh: {record['ngaysinh'] or '-'}")
        st.write(f"Giới tính: {record['gioitinh'] or '-'}")
        st.write(f"Lớp: {record['lop']}")
        st.write(f"Năm học: {record['namhoc'] or '-'}")
    with c2:
        st.write(f"Dân tộc: {record['dantoc'] or '-'}")
        st.write(f"Địa chỉ: {record['diachi_hs'] or '-'}")
        st.write(f"SĐT học sinh: {record['sdt_hs'] or '-'}")
        st.write(f"Email học sinh: {record['email_hs'] or '-'}")

    st.markdown("**👨 Cha**")
    c3, c4 = st.columns(2)
    with c3:
        st.write(f"Họ tên: {record['hoten_cha'] or '-'}")
        st.write(f"Ngày sinh: {record['ngaysinh_cha'] or '-'}")
        st.write(f"SĐT: {record['sdt_cha'] or '-'}")
    with c4:
        st.write(f"Email: {record['email_cha'] or '-'}")
        st.write(f"Nghề nghiệp: {record['nghenghiep_cha'] or '-'}")
        st.write(f"Nơi làm việc: {record['noilamviec_cha'] or '-'}")

    st.markdown("**👩 Mẹ**")
    c5, c6 = st.columns(2)
    with c5:
        st.write(f"Họ tên: {record['hoten_me'] or '-'}")
        st.write(f"Ngày sinh: {record['ngaysinh_me'] or '-'}")
        st.write(f"SĐT: {record['sdt_me'] or '-'}")
    with c6:
        st.write(f"Email: {record['email_me'] or '-'}")
        st.write(f"Nghề nghiệp: {record['nghenghiep_me'] or '-'}")
        st.write(f"Nơi làm việc: {record['noilamviec_me'] or '-'}")

    st.markdown("**👪 Người giám hộ / liên hệ khác**")
    c7, c8 = st.columns(2)
    with c7:
        st.write(f"Họ tên: {record['hoten_giamho'] or '-'}")
        st.write(f"Quan hệ: {record['quanhe_giamho'] or '-'}")
    with c8:
        st.write(f"SĐT: {record['sdt_giamho'] or '-'}")
        st.write(f"Email: {record['email_giamho'] or '-'}")
    st.write(f"Địa chỉ: {record['diachi_giamho'] or '-'}")

    st.caption(f"Gửi lúc: {record['created_at']} | Cập nhật: {record['updated_at']}")

    st.markdown("---")
    st.markdown("#### ✏️ Chỉnh sửa")
    with st.form(f"edit_form_{record_id}"):
        st.markdown("**📘 Học sinh**")
        e1, e2 = st.columns(2)
        with e1:
            hoten_hs = _text("Họ tên học sinh", record["hoten_hs"])
            ngaysinh = _text("Ngày sinh HS (dd/mm/yyyy)", record["ngaysinh"])
            gi_idx = GIOITINH_OPTIONS.index(record["gioitinh"]) if record["gioitinh"] in GIOITINH_OPTIONS else 0
            gioitinh = st.selectbox("Giới tính", GIOITINH_OPTIONS, index=gi_idx)
            lop_options = db.CLASS_LIST if record["lop"] in db.CLASS_LIST else db.CLASS_LIST + [record["lop"]]
            lop = st.selectbox("Lớp", lop_options, index=lop_options.index(record["lop"]) if record["lop"] in lop_options else 0)
            namhoc = _text("Năm học", record["namhoc"])
        with e2:
            dantoc = _text("Dân tộc", record["dantoc"])
            diachi_hs = _text("Địa chỉ hiện tại", record["diachi_hs"])
            sdt_hs = _text("SĐT học sinh", record["sdt_hs"])
            email_hs = _text("Email học sinh", record["email_hs"])

        st.markdown("**👨 Cha**")
        e3, e4 = st.columns(2)
        with e3:
            hoten_cha = _text("Họ tên cha", record["hoten_cha"])
            ngaysinh_cha = _text("Ngày sinh cha", record["ngaysinh_cha"])
            sdt_cha = _text("SĐT cha", record["sdt_cha"])
        with e4:
            email_cha = _text("Email cha", record["email_cha"])
            nghenghiep_cha = _text("Nghề nghiệp cha", record["nghenghiep_cha"])
            noilamviec_cha = _text("Nơi làm việc cha", record["noilamviec_cha"])

        st.markdown("**👩 Mẹ**")
        e5, e6 = st.columns(2)
        with e5:
            hoten_me = _text("Họ tên mẹ", record["hoten_me"])
            ngaysinh_me = _text("Ngày sinh mẹ", record["ngaysinh_me"])
            sdt_me = _text("SĐT mẹ", record["sdt_me"])
        with e6:
            email_me = _text("Email mẹ", record["email_me"])
            nghenghiep_me = _text("Nghề nghiệp mẹ", record["nghenghiep_me"])
            noilamviec_me = _text("Nơi làm việc mẹ", record["noilamviec_me"])

        st.markdown("**👪 Người giám hộ / liên hệ khác**")
        e7, e8 = st.columns(2)
        with e7:
            hoten_giamho = _text("Họ tên", record["hoten_giamho"])
            quanhe_giamho = _text("Quan hệ với học sinh", record["quanhe_giamho"])
        with e8:
            sdt_giamho = _text("SĐT", record["sdt_giamho"])
            email_giamho = _text("Email", record["email_giamho"])
        diachi_giamho = _text("Địa chỉ", record["diachi_giamho"])

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
                "lop": lop, "namhoc": namhoc, "dantoc": dantoc,
                "diachi_hs": diachi_hs, "sdt_hs": sdt_hs, "email_hs": email_hs,
                "hoten_cha": hoten_cha, "ngaysinh_cha": ngaysinh_cha, "sdt_cha": sdt_cha,
                "email_cha": email_cha, "nghenghiep_cha": nghenghiep_cha, "noilamviec_cha": noilamviec_cha,
                "hoten_me": hoten_me, "ngaysinh_me": ngaysinh_me, "sdt_me": sdt_me,
                "email_me": email_me, "nghenghiep_me": nghenghiep_me, "noilamviec_me": noilamviec_me,
                "hoten_giamho": hoten_giamho, "quanhe_giamho": quanhe_giamho,
                "sdt_giamho": sdt_giamho, "email_giamho": email_giamho, "diachi_giamho": diachi_giamho,
                "trang_thai": trang_thai,
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
    # ---- Nền gradient đồng bộ, không có illustration nổi để không rối mắt khi thao tác dữ liệu ----
    theme.inject_theme(decor=False)
    st.markdown("<style>div.stButton > button {border-radius: 10px;}</style>", unsafe_allow_html=True)

    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown("## 📋 QUẢN LÝ THÔNG TIN HỌC SINH")
    with top_r:
        if st.button("Đăng xuất"):
            st.session_state.admin_logged_in = False
            st.rerun()

    with st.expander("🔑 Đổi mật khẩu đăng nhập"):
        with st.form("change_password_form"):
            current_password = st.text_input("Mật khẩu hiện tại", type="password")
            new_password = st.text_input("Mật khẩu mới", type="password")
            confirm_password = st.text_input("Nhập lại mật khẩu mới", type="password")
            change_ok = st.form_submit_button("Cập nhật mật khẩu")
            if change_ok:
                if not _check_password(current_password):
                    st.error("Mật khẩu hiện tại không đúng.")
                elif not new_password or len(new_password) < 6:
                    st.error("Mật khẩu mới phải có ít nhất 6 ký tự.")
                elif new_password != confirm_password:
                    st.error("Mật khẩu nhập lại không khớp.")
                else:
                    db.set_setting("admin_password_hash", db.hash_password(new_password))
                    st.success("Đã đổi mật khẩu thành công. Lần đăng nhập sau hãy dùng mật khẩu mới.")

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

    fc1, fc2, fc3 = st.columns([3, 2, 2])
    with fc1:
        keyword = st.text_input("🔍 Tìm kiếm (tên học sinh, cha, mẹ, SĐT)")
    with fc2:
        classes = ["Tất cả"] + db.get_class_list()
        selected_class = st.selectbox("Lọc theo lớp", classes)
    with fc3:
        status_filter = st.selectbox("Lọc theo trạng thái", ["Tất cả", "Mới", "Đã xử lý"])

    filtered = df.copy()
    if keyword and len(filtered):
        kw = keyword.strip().lower()
        filtered = filtered[
            filtered["hoten_hs"].fillna("").str.lower().str.contains(kw) |
            filtered["hoten_cha"].fillna("").str.lower().str.contains(kw) |
            filtered["hoten_me"].fillna("").str.lower().str.contains(kw) |
            filtered["sdt_hs"].fillna("").astype(str).str.contains(kw) |
            filtered["sdt_cha"].fillna("").astype(str).str.contains(kw) |
            filtered["sdt_me"].fillna("").astype(str).str.contains(kw)
        ]
    if selected_class != "Tất cả":
        filtered = filtered[filtered["lop"] == selected_class]
    if status_filter != "Tất cả":
        filtered = filtered[filtered["trang_thai"] == status_filter]

    exp_col1, _ = st.columns([1, 5])
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

    header = st.columns([2, 1, 2, 2, 1.3, 1])
    header[0].markdown("**Học sinh**")
    header[1].markdown("**Lớp**")
    header[2].markdown("**Phụ huynh**")
    header[3].markdown("**Số điện thoại**")
    header[4].markdown("**Trạng thái**")
    header[5].markdown("**Thao tác**")
    st.markdown("<hr style='margin:0.2em 0;'>", unsafe_allow_html=True)

    for _, row in filtered.iterrows():
        # Ưu tiên hiển thị: Cha -> Mẹ -> Người giám hộ
        ph_name = row["hoten_cha"] or row["hoten_me"] or row["hoten_giamho"] or "-"
        ph_sdt = row["sdt_cha"] or row["sdt_me"] or row["sdt_giamho"] or "-"

        cols = st.columns([2, 1, 2, 2, 1.3, 1])
        cols[0].write(row["hoten_hs"])
        cols[1].write(row["lop"])
        cols[2].write(ph_name)
        cols[3].write(ph_sdt)
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

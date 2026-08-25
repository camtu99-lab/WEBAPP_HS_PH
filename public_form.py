"""
public_form.py - Trang biểu mẫu công khai: học sinh/phụ huynh điền thông tin.
Không cần đăng nhập, không cần tài khoản. Chỉ: Mở link -> Điền -> Gửi -> Xong.
"""
import streamlit as st
import uuid
import os
import db

SCHOOL_NAME = "TRƯỜNG TIỂU HỌC ABC"  # Đổi tên trường tại đây


def render_public_form():
    # ---- CSS: chữ to, nút rõ, thân thiện người lớn tuổi ----
    st.markdown("""
        <style>
        .main .block-container {max-width: 720px; padding-top: 2rem;}
        h1, h2, h3 {font-family: 'Segoe UI', sans-serif;}
        div.stButton > button {
            width: 100%;
            height: 3.2em;
            font-size: 1.3em;
            font-weight: 700;
            border-radius: 10px;
            background-color: #1a73e8;
            color: white;
            border: none;
        }
        div.stButton > button:hover {background-color: #1558b0; color: white;}
        label, .stTextInput, .stSelectbox, .stTextArea {font-size: 1.05em !important;}
        .section-title {
            background-color: #f0f4fb;
            padding: 0.6em 1em;
            border-left: 5px solid #1a73e8;
            border-radius: 6px;
            margin-top: 1.2em;
            margin-bottom: 0.8em;
            font-size: 1.2em;
            font-weight: 700;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---- Nếu vừa gửi thành công ----
    if st.session_state.get("submitted"):
        st.markdown("<div style='text-align:center; margin-top:3em;'>", unsafe_allow_html=True)
        st.markdown("## ✅ GỬI THÀNH CÔNG")
        st.markdown("### Thông tin của bạn đã được gửi đến nhà trường.")
        st.markdown("Cảm ơn quý phụ huynh / học sinh!")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Gửi thêm một phiếu khác"):
            st.session_state.submitted = False
            st.rerun()
        return

    # ---- Tiêu đề ----
    st.markdown(f"<h2 style='text-align:center;'>{SCHOOL_NAME}</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>PHIẾU CUNG CẤP THÔNG TIN</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; font-size:1.1em; color:#555;'>"
        "Mời học sinh/phụ huynh điền đầy đủ thông tin bên dưới.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    with st.form("public_form", clear_on_submit=False):
        # ---- Thông tin học sinh ----
        st.markdown("<div class='section-title'>📘 THÔNG TIN HỌC SINH</div>", unsafe_allow_html=True)
        hoten_hs = st.text_input("Họ và tên học sinh *")
        col1, col2 = st.columns(2)
        with col1:
            ngaysinh = st.date_input("Ngày sinh *", value=None, format="DD/MM/YYYY")
        with col2:
            gioitinh = st.selectbox("Giới tính", ["", "Nam", "Nữ", "Khác"])
        lop = st.text_input("Lớp *", placeholder="Ví dụ: 3A")
        diachi_hs = st.text_input("Địa chỉ")

        # ---- Thông tin phụ huynh ----
        st.markdown("<div class='section-title'>👪 THÔNG TIN PHỤ HUYNH</div>", unsafe_allow_html=True)
        hoten_ph = st.text_input("Họ và tên phụ huynh *")
        quanhe = st.text_input("Quan hệ với học sinh", placeholder="Ví dụ: Bố, Mẹ, Ông, Bà...")
        sdt = st.text_input("Số điện thoại *")
        email = st.text_input("Email")
        diachi_ph = st.text_input("Địa chỉ phụ huynh (nếu khác học sinh)")

        # ---- Thông tin khác ----
        st.markdown("<div class='section-title'>📝 THÔNG TIN KHÁC</div>", unsafe_allow_html=True)
        noidung = st.text_area("Nội dung cần trao đổi", height=100)
        tep = st.file_uploader("Tệp/hình ảnh đính kèm (nếu cần)",
                                type=["jpg", "jpeg", "png", "pdf", "doc", "docx"])

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("GỬI THÔNG TIN")

        if submitted:
            errors = []
            if not hoten_hs.strip():
                errors.append("Vui lòng nhập Họ và tên học sinh.")
            if not lop.strip():
                errors.append("Vui lòng nhập Lớp.")
            if not hoten_ph.strip():
                errors.append("Vui lòng nhập Họ và tên phụ huynh.")
            if not sdt.strip():
                errors.append("Vui lòng nhập Số điện thoại.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Lưu tệp đính kèm nếu có
                tep_filename = None
                if tep is not None:
                    ext = os.path.splitext(tep.name)[1]
                    tep_filename = f"{uuid.uuid4().hex}{ext}"
                    save_path = os.path.join(db.UPLOAD_DIR, tep_filename)
                    with open(save_path, "wb") as f:
                        f.write(tep.getbuffer())

                data = {
                    "hoten_hs": hoten_hs.strip(),
                    "ngaysinh": ngaysinh.strftime("%d/%m/%Y") if ngaysinh else "",
                    "gioitinh": gioitinh,
                    "lop": lop.strip(),
                    "diachi_hs": diachi_hs.strip(),
                    "hoten_ph": hoten_ph.strip(),
                    "quanhe": quanhe.strip(),
                    "sdt": sdt.strip(),
                    "email": email.strip(),
                    "diachi_ph": diachi_ph.strip(),
                    "noidung": noidung.strip(),
                    "tep_dinhkem": tep_filename,
                }
                db.add_record(data)
                st.session_state.submitted = True
                st.rerun()

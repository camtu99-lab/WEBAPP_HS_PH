"""
public_form.py - Trang biểu mẫu công khai: học sinh/phụ huynh điền thông tin.
Không cần đăng nhập, không cần tài khoản. Chỉ: Mở link -> Điền -> Gửi -> Xong.
TẤT CẢ các trường đều bắt buộc - nếu thiếu bất kỳ trường nào sẽ không cho gửi.
"""
import streamlit as st
import datetime
import db
import theme

SCHOOL_NAME = "TRƯỜNG THCS VÀ THPT NAM THÁI SƠN"

# Vài năm học để chọn (điều chỉnh nếu cần)
_current_year = datetime.date.today().year
NAMHOC_OPTIONS = [f"{y}-{y+1}" for y in range(_current_year - 1, _current_year + 2)]


def render_public_form():
    # ---- Nền gradient, illustration giáo dục nổi nhẹ, glassmorphism cho form ----
    theme.inject_theme(decor=True)

    # ---- CSS bố cục riêng của trang: chữ to, nút rõ, thân thiện người lớn tuổi ----
    st.markdown("""
        <style>
        .main .block-container {max-width: 720px; padding-top: 2rem;}
        h1, h2, h3 {font-family: 'Segoe UI', sans-serif;}
        div.stButton > button, div.stFormSubmitButton > button {
            width: 100%;
            height: 3.2em;
            font-size: 1.3em;
            font-weight: 700;
            border-radius: 14px;
        }
        label, .stTextInput, .stSelectbox, .stTextArea {font-size: 1.05em !important;}
        .section-title {
            padding: 0.6em 1em;
            border-radius: 10px;
            margin-top: 1.2em;
            margin-bottom: 0.8em;
            font-size: 1.2em;
            font-weight: 700;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---- Nếu vừa gửi thành công ----
    if st.session_state.get("submitted"):
        st.markdown(
            "<div class='edu-glass-card' style='text-align:center; margin-top:3em;'>",
            unsafe_allow_html=True
        )
        st.markdown("## ✅ GỬI THÀNH CÔNG")
        st.markdown("### Thông tin của bạn đã được gửi đến nhà trường.")
        st.markdown("Cảm ơn quý phụ huynh / học sinh!")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Gửi thêm một phiếu khác"):
            st.session_state.submitted = False
            st.rerun()
        return

    # ---- Tiêu đề ----
    st.markdown(f"<h2 class='edu-gradient-title' style='text-align:center;'>{SCHOOL_NAME}</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>PHIẾU CUNG CẤP THÔNG TIN</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; font-size:1.1em; color:#555;'>"
        "Mời học sinh/phụ huynh điền đầy đủ thông tin bên dưới. "
        "<b>Tất cả các mục đều bắt buộc (*), vui lòng không để trống.</b></p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    with st.form("public_form", clear_on_submit=False):
        # ============ THÔNG TIN HỌC SINH ============
        st.markdown("<div class='section-title'>📘 THÔNG TIN HỌC SINH</div>", unsafe_allow_html=True)
        hoten_hs = st.text_input("Họ và tên *")
        c1, c2 = st.columns(2)
        with c1:
            ngaysinh = st.date_input("Ngày sinh *", value=None, format="DD/MM/YYYY",
                                      min_value=datetime.date(1990, 1, 1),
                                      max_value=datetime.date.today())
        with c2:
            gioitinh = st.selectbox("Giới tính *", ["", "Nam", "Nữ", "Khác"])
        c3, c4 = st.columns(2)
        with c3:
            lop = st.selectbox("Lớp *", [""] + db.CLASS_LIST)
        with c4:
            namhoc = st.selectbox("Năm học *", [""] + NAMHOC_OPTIONS)
        dantoc = st.text_input("Dân tộc *")
        diachi_hs = st.text_input("Địa chỉ hiện tại *")
        c5, c6 = st.columns(2)
        with c5:
            sdt_hs = st.text_input("Số điện thoại học sinh *")
        with c6:
            email_hs = st.text_input("Email học sinh")

        # ============ THÔNG TIN CHA ============
        st.markdown("<div class='section-title'>👨 THÔNG TIN CHA</div>", unsafe_allow_html=True)
        hoten_cha = st.text_input("Họ và tên cha *")
        c7, c8 = st.columns(2)
        with c7:
            ngaysinh_cha = st.text_input("Ngày sinh cha (dd/mm/yyyy)", key="ns_cha")
        with c8:
            sdt_cha = st.text_input("Số điện thoại cha *")
        c9, c10 = st.columns(2)
        with c9:
            email_cha = st.text_input("Email cha")
        with c10:
            nghenghiep_cha = st.text_input("Nghề nghiệp cha *")
        noilamviec_cha = st.text_input("Nơi làm việc cha *")

        # ============ THÔNG TIN MẸ ============
        st.markdown("<div class='section-title'>👩 THÔNG TIN MẸ</div>", unsafe_allow_html=True)
        hoten_me = st.text_input("Họ và tên mẹ *")
        c11, c12 = st.columns(2)
        with c11:
            ngaysinh_me = st.text_input("Ngày sinh mẹ (dd/mm/yyyy)", key="ns_me")
        with c12:
            sdt_me = st.text_input("Số điện thoại mẹ *")
        c13, c14 = st.columns(2)
        with c13:
            email_me = st.text_input("Email mẹ")
        with c14:
            nghenghiep_me = st.text_input("Nghề nghiệp mẹ *")
        noilamviec_me = st.text_input("Nơi làm việc mẹ *")

        # ============ NGƯỜI GIÁM HỘ / LIÊN HỆ KHÁC ============
        st.markdown("<div class='section-title'>👪 NGƯỜI GIÁM HỘ / LIÊN HỆ KHÁC</div>", unsafe_allow_html=True)
        hoten_giamho = st.text_input("Họ và tên (người giám hộ/liên hệ khác) *")
        quanhe_giamho = st.text_input("Quan hệ với học sinh *")
        c15, c16 = st.columns(2)
        with c15:
            sdt_giamho = st.text_input("Số điện thoại (giám hộ) *")
        with c16:
            email_giamho = st.text_input("Email (giám hộ)")
        diachi_giamho = st.text_input("Địa chỉ (giám hộ) *")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("GỬI THÔNG TIN")

        if submitted:
            # Kiểm tra TẤT CẢ các trường - thiếu bất kỳ trường nào cũng không cho gửi
            fields_to_check = [
                ("Họ và tên học sinh", hoten_hs),
                ("Ngày sinh học sinh", ngaysinh),
                ("Giới tính", gioitinh),
                ("Lớp", lop),
                ("Năm học", namhoc),
                ("Dân tộc", dantoc),
                ("Địa chỉ hiện tại", diachi_hs),
                ("Số điện thoại học sinh", sdt_hs),
                ("Họ và tên cha", hoten_cha),
                ("Số điện thoại cha", sdt_cha),
                ("Nghề nghiệp cha", nghenghiep_cha),
                ("Nơi làm việc cha", noilamviec_cha),
                ("Họ và tên mẹ", hoten_me),
                ("Số điện thoại mẹ", sdt_me),
                ("Nghề nghiệp mẹ", nghenghiep_me),
                ("Nơi làm việc mẹ", noilamviec_me),
                ("Họ và tên người giám hộ/liên hệ khác", hoten_giamho),
                ("Quan hệ với học sinh (giám hộ)", quanhe_giamho),
                ("Số điện thoại giám hộ", sdt_giamho),
                ("Địa chỉ giám hộ", diachi_giamho),
            ]

            errors = []
            for label, value in fields_to_check:
                if value is None:
                    errors.append(f"Vui lòng nhập/chọn: {label}")
                elif isinstance(value, str) and not value.strip():
                    errors.append(f"Vui lòng nhập/chọn: {label}")

            if errors:
                st.error(f"⚠️ Còn thiếu {len(errors)} thông tin bắt buộc. Vui lòng điền đầy đủ tất cả các mục trước khi gửi:")
                for e in errors:
                    st.error(e)
            else:
                data = {
                    "hoten_hs": hoten_hs.strip(),
                    "ngaysinh": ngaysinh.strftime("%d/%m/%Y") if ngaysinh else "",
                    "gioitinh": gioitinh,
                    "lop": lop,
                    "namhoc": namhoc,
                    "dantoc": dantoc.strip(),
                    "diachi_hs": diachi_hs.strip(),
                    "sdt_hs": sdt_hs.strip(),
                    "email_hs": email_hs.strip(),
                    "hoten_cha": hoten_cha.strip(),
                    "ngaysinh_cha": ngaysinh_cha.strip(),
                    "sdt_cha": sdt_cha.strip(),
                    "email_cha": email_cha.strip(),
                    "nghenghiep_cha": nghenghiep_cha.strip(),
                    "noilamviec_cha": noilamviec_cha.strip(),
                    "hoten_me": hoten_me.strip(),
                    "ngaysinh_me": ngaysinh_me.strip(),
                    "sdt_me": sdt_me.strip(),
                    "email_me": email_me.strip(),
                    "nghenghiep_me": nghenghiep_me.strip(),
                    "noilamviec_me": noilamviec_me.strip(),
                    "hoten_giamho": hoten_giamho.strip(),
                    "quanhe_giamho": quanhe_giamho.strip(),
                    "sdt_giamho": sdt_giamho.strip(),
                    "email_giamho": email_giamho.strip(),
                    "diachi_giamho": diachi_giamho.strip(),
                }
                db.add_record(data)
                st.session_state.submitted = True
                st.rerun()

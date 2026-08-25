"""
app.py - Điểm khởi chạy chính.

- Link công khai (không cần tham số): dành cho học sinh/phụ huynh điền phiếu.
  Ví dụ: https://your-app-url.streamlit.app/

- Link quản trị (thêm ?admin=1): dành cho nhà trường đăng nhập & quản lý.
  Ví dụ: https://your-app-url.streamlit.app/?admin=1
"""
import streamlit as st
import db
from public_form import render_public_form
from admin_page import render_admin_page

st.set_page_config(
    page_title="Phiếu cung cấp thông tin học sinh",
    page_icon="🏫",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Ẩn menu/sidebar mặc định của Streamlit để giao diện gọn gàng, không có menu thừa
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarCollapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

db.init_db()

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "viewing_id" not in st.session_state:
    st.session_state.viewing_id = None

# Điều hướng đơn giản dựa trên query param, không có menu điều hướng hiển thị
is_admin_route = st.query_params.get("admin") is not None

if is_admin_route:
    render_admin_page()
else:
    render_public_form()

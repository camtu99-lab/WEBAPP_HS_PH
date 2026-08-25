"""
theme.py - Giao diện dùng chung: nền gradient xanh dương - tím pastel - trắng,
blob ánh sáng mềm, illustration giáo dục nổi nhẹ (sách, bút, mũ tốt nghiệp,
trường học), hiệu ứng glassmorphism cho form.

CHỈ xử lý phần NỀN / TRANG TRÍ. Không chứa bất kỳ logic nghiệp vụ nào —
public_form.py, admin_page.py giữ nguyên toàn bộ nội dung, form và chức năng,
chỉ gọi inject_theme() để áp giao diện.
"""
import streamlit as st

_BASE_CSS = """
<style>
/* ============ NỀN: gradient xanh dương - tím pastel - trắng, glow trôi nhẹ ============ */
[data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background:
        radial-gradient(750px circle at 6% 10%,   rgba(90,140,255,0.50), transparent 62%),
        radial-gradient(650px circle at 95% 6%,    rgba(170,110,255,0.46), transparent 62%),
        radial-gradient(800px circle at 90% 95%,   rgba(110,150,255,0.44), transparent 62%),
        radial-gradient(650px circle at 4% 92%,    rgba(180,120,255,0.42), transparent 62%),
        radial-gradient(900px circle at 50% 45%,   rgba(150,150,255,0.18), transparent 70%),
        linear-gradient(135deg, #e2ecff 0%, #ece0ff 45%, #f7f9ff 100%);
    background-attachment: fixed;
    background-size: 200% 200%, 200% 200%, 200% 200%, 200% 200%, 160% 160%, 100% 100%;
    animation: bg-drift 20s ease-in-out infinite alternate;
}
@keyframes bg-drift {
    0%   { background-position: 0% 0%, 100% 0%, 100% 100%, 0% 100%, 50% 50%, 0 0; }
    100% { background-position: 6% 6%, 94% 4%, 94% 94%, 6% 94%, 55% 45%, 0 0; }
}
[data-testid="stHeader"] { background: transparent; }

/* Dải sóng cong mềm mại ở đầu và cuối trang, tạo chiều sâu cho nền */
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    left: 0; right: 0;
    height: 220px;
    pointer-events: none;
    z-index: 0;
    opacity: 0.55;
    background-repeat: no-repeat;
    background-size: 100% 100%;
}
[data-testid="stAppViewContainer"]::before {
    top: 0;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 220' preserveAspectRatio='none'><path d='M0,80 C 300,180 500,0 800,60 C 1100,120 1250,20 1440,90 L1440,0 L0,0 Z' fill='%234f7cff' fill-opacity='0.16'/><path d='M0,120 C 320,40 620,190 900,110 C 1150,40 1300,140 1440,100 L1440,0 L0,0 Z' fill='%238a63f0' fill-opacity='0.12'/></svg>");
}
[data-testid="stAppViewContainer"]::after {
    bottom: 0;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 220' preserveAspectRatio='none'><path d='M0,140 C 300,40 500,220 800,160 C 1100,100 1250,200 1440,130 L1440,220 L0,220 Z' fill='%234f7cff' fill-opacity='0.16'/><path d='M0,100 C 320,190 620,20 900,100 C 1150,180 1300,60 1440,120 L1440,220 L0,220 Z' fill='%238a63f0' fill-opacity='0.12'/></svg>");
}

/* ============ Illustration giáo dục nổi nhẹ - tự ẩn trên di động ============ */
.edu-decor { position: fixed; z-index: 0; pointer-events: none; opacity: 0.26; }
.edu-decor svg { display: block; filter: drop-shadow(0 6px 12px rgba(90,100,190,0.22)); }
.edu-decor-book   { top: 8%;   left: 3%;  width: 74px; animation: edu-float 7s ease-in-out infinite; }
.edu-decor-pencil { top: 66%;  left: 4%;  width: 64px; animation: edu-float 8s ease-in-out infinite 0.6s; }
.edu-decor-cap    { top: 9%;   right: 4%; width: 78px; animation: edu-float 7.5s ease-in-out infinite 0.3s; }
.edu-decor-school { bottom: 6%; right: 5%; width: 94px; animation: edu-float 9s ease-in-out infinite 0.9s; }
@keyframes edu-float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50%      { transform: translateY(-14px) rotate(3deg); }
}
@media (max-width: 768px) {
    .edu-decor { display: none; }
}

/* Nội dung chính luôn nổi trên lớp trang trí */
.main .block-container { position: relative; z-index: 1; }

/* ============ Glassmorphism cho form / thẻ nội dung - nổi bật rõ trên nền đậm hơn ============ */
div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.86) !important;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-radius: 22px !important;
    border: 1px solid rgba(255, 255, 255, 0.75);
    box-shadow: 0 16px 40px rgba(80, 90, 190, 0.22), 0 2px 8px rgba(80, 90, 190, 0.10);
    padding: 1.8em 1.6em;
}

.edu-glass-card {
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-radius: 22px;
    border: 1px solid rgba(255, 255, 255, 0.7);
    box-shadow: 0 16px 38px rgba(80, 90, 190, 0.22);
    padding: 2em 1.6em;
}

/* ============ Nút bấm: gradient xanh dương - tím, bo mềm ============ */
div.stButton > button, div.stFormSubmitButton > button {
    background: linear-gradient(135deg, #4f7cff 0%, #8a63f0 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(94, 100, 220, 0.28);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #3f6cf0 0%, #7a53e0 100%) !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(94, 100, 220, 0.34);
}

/* ============ Khung nhóm nội dung (section-title) đồng bộ tông màu ============ */
.section-title {
    background: linear-gradient(90deg, #dbe7ff 0%, #ecdfff 100%) !important;
    border-left: 5px solid #7c6df2 !important;
    box-shadow: 0 2px 10px rgba(124, 109, 242, 0.14);
}

/* Tiêu đề chữ gradient nhẹ, sang trọng */
.edu-gradient-title {
    background: linear-gradient(90deg, #3f6cf0, #8a5cf0);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

/* Ô nhập liệu / lựa chọn: bo góc mềm cho hợp tông kính mờ */
.stTextInput input, .stTextArea textarea,
.stSelectbox > div > div, .stDateInput input {
    border-radius: 10px !important;
}

/* Thẻ số liệu (metric) ở trang quản trị: kính mờ nhẹ */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 14px;
    padding: 0.6em 0.8em;
    box-shadow: 0 4px 14px rgba(80, 90, 190, 0.14);
}
</style>
"""

# SVG illustration giáo dục tối giản (sách, bút, mũ tốt nghiệp, trường học)
_DECOR_HTML = """
<div class="edu-decor edu-decor-book">
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
<path d="M6 12c8-4 16-4 26 0v38c-10-4-18-4-26 0V12z" fill="#4f7cff"/>
<path d="M58 12c-8-4-16-4-26 0v38c10-4 18-4 26 0V12z" fill="#8a63f0"/>
</svg>
</div>
<div class="edu-decor edu-decor-pencil">
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
<rect x="8" y="26" width="40" height="12" rx="3" transform="rotate(-25 8 26)" fill="#4f7cff"/>
<path d="M44 12l10 10-8 8-10-10 8-8z" fill="#8a63f0"/>
<path d="M6 46l6 6 8-4-10-10-4 8z" fill="#ffd166"/>
</svg>
</div>
<div class="edu-decor edu-decor-cap">
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
<path d="M32 10L4 24l28 14 28-14L32 10z" fill="#4f7cff"/>
<path d="M16 30v14c0 4 7.2 8 16 8s16-4 16-8V30l-16 8-16-8z" fill="#8a63f0"/>
<circle cx="58" cy="26" r="2.5" fill="#4f7cff"/>
<path d="M58 26v12" stroke="#4f7cff" stroke-width="2"/>
</svg>
</div>
<div class="edu-decor edu-decor-school">
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
<rect x="10" y="26" width="44" height="30" rx="2" fill="#8a63f0"/>
<path d="M32 8l24 18H8L32 8z" fill="#4f7cff"/>
<rect x="28" y="38" width="8" height="18" fill="#ffffff"/>
<rect x="16" y="34" width="6" height="6" fill="#ffffff"/>
<rect x="42" y="34" width="6" height="6" fill="#ffffff"/>
</svg>
</div>
"""


def inject_theme(decor: bool = True):
    """Chèn CSS nền gradient + hiệu ứng trang trí cho trang hiện tại.

    decor=True  -> hiện thêm illustration giáo dục nổi nhẹ (dùng cho trang
                    công khai / đăng nhập).
    decor=False -> chỉ nền gradient + kính mờ, không có illustration nổi,
                    dùng cho màn hình thao tác dữ liệu (bảng, bộ lọc) để
                    tránh rối mắt.
    """
    st.markdown(_BASE_CSS, unsafe_allow_html=True)
    if decor:
        st.markdown(_DECOR_HTML, unsafe_allow_html=True)

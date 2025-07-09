import streamlit as st

from utils.pages import home, gallery, sub_page_1, sub_page_2, sub_page_3, sub_page_4, sub_page_5

# 초기 세션 상태 셋업
st.set_page_config(layout="wide")
st.session_state.setdefault("page", "home")
st.session_state.setdefault("step", 1)  # 광고 생성 단계

# 사이드바 UI 구성
st.markdown("""
    <style>
    .sidebar-container {
        padding: 1rem;
        background-color: #f9f9fb;
        border-radius: 8px;
        margin-top: 1rem;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
    }

    .sidebar-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #333;
    }

    .custom-sidebar-button {
        display: block;
        padding: 10px 16px;
        margin: 6px 0;
        border-radius: 8px;
        text-decoration: none;
        color: #333;
        background-color: #f0f0f0;
        font-weight: normal;
        transition: all 0.2s ease;
    }

    .custom-sidebar-button:hover {
        background-color: #e6f0ff;
        font-weight: 600;
    }

    .custom-sidebar-button.selected {
        background-color: #4A8CF1;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

menu_items = {
    "🏠 홈": "home",
    "🖼️ 갤러리": "gallery",
    "🛠️ 광고 생성": "generate_ad"
}

with st.sidebar:
    st.markdown("<div class='sidebar-title'>📂 메뉴</div>", unsafe_allow_html=True)

    for label, route in menu_items.items():
        is_selected = st.session_state["page"] == route
        button_class = "custom-sidebar-button selected" if is_selected else "custom-sidebar-button"
        if st.markdown(f"<a class='{button_class}' href='#{route}'>{label}</a>", unsafe_allow_html=True):
            if st.session_state["page"] != route:
                st.session_state["page"] = route
                if route == "generate_ad":
                    st.session_state["step"] = 1
                st.rerun()

# 페이지 렌더링
if st.session_state["page"] == "home":
    home.render()
elif st.session_state["page"] == "gallery":
    gallery.render()
elif st.session_state["page"] == "generate_ad":
    step = st.session_state.get("step", 1)
    if step == 1:
        sub_page_1.render()
    elif step == 2:
        sub_page_2.render()
    elif step == 3:
        sub_page_3.render()
    elif step == 4:
        sub_page_4.render()
    elif step == 5:
        sub_page_5.render()

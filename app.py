import streamlit as st
from streamlit_option_menu import option_menu

from utils.pages import home, gallery, sub_page_1, sub_page_2, sub_page_3, sub_page_4, sub_page_5

# 초기 세션 상태 셋업
st.set_page_config(layout="wide")
st.session_state.setdefault("page", "home")
st.session_state.setdefault("step", 1)  # 광고 생성 단계

# 사이드바 메뉴 - streamlit-option-menu 활용
with st.sidebar:
    selected = option_menu(
        menu_title="메뉴",
        options=["홈", "갤러리", "광고 생성"],
        icons=["house", "image", "tools"],
        menu_icon="cast",
        default_index=["홈", "갤러리", "광고 생성"].index(
            next((label for label, page in {
                "홈": "home",
                "갤러리": "gallery",
                "광고 생성": "generate_ad"
            }.items() if page == st.session_state["page"]), "홈")
        ),
        styles={
            "container": {"padding": "10px"},
            "icon": {"color": "#4A8CF1", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#e6f0ff",
                "border-radius": "8px",
            },
            "nav-link-selected": {
                "background-color": "#4A8CF1",
                "color": "white",
                "font-weight": "bold",
                "border-radius": "8px",
            },
            "menu-title": {"font-size": "22px", "font-weight": "bold"},
        },
    )

# 선택된 메뉴에 따라 내부 페이지 상태 변경 및 step 초기화
label_to_page = {
    "홈": "home",
    "갤러리": "gallery",
    "광고 생성": "generate_ad"
}

selected_page = label_to_page[selected]

if st.session_state["page"] != selected_page:
    st.session_state["page"] = selected_page
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

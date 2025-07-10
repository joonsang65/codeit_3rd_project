# 페이지 렌더 함수 import
from utils.pages import home, gallery, CSS
from utils.pages.subpages import sub_page_1, sub_page_2, sub_page_3, sub_page_4, sub_page_5
import streamlit as st
from streamlit_option_menu import option_menu

#######################################################################################################

# 초기 설정 및 세션 변수 선언
st.set_page_config(layout="wide")
st.session_state.setdefault("page", "home")
st.session_state.setdefault("step", 1)
st.session_state.setdefault("platform", None)

# 메뉴 라벨과 내부 페이지명 매핑
label_to_page = {
    "홈": "home",
    "갤러리": "gallery",
    "광고 생성": "generate_ad"
}

#######################################################################################################

# 사이드바 메뉴
with st.sidebar:
    selected = option_menu(
        menu_title="메뉴",
        options=["홈", "갤러리", "광고 생성"],
        icons=["house", "image", "tools"],
        menu_icon="cast",
        # 현재 페이지에 맞춰 기본 선택 인덱스 지정
        default_index=["홈", "갤러리", "광고 생성"].index(
            next((label for label, page in label_to_page.items() if page == st.session_state["page"]), "홈")
        ),
        styles= CSS.app_sidebar_CSS,
    )

    selected_page = label_to_page[selected]

    #######################################################################################################

    # '광고 생성' 메뉴 선택 시 플랫폼 선택 UI 표시 및 처리
    if selected == "광고 생성":
        st.markdown("### 플랫폼을 선택해주세요")
        platform_options = ["플랫폼을 선택하세요", "인스타그램", "블로그", "포스터"]

        platform_selection = st.selectbox(
            "플랫폼 선택",
            platform_options,
            index=0  # 기본값: 선택 유도용 플레이스홀더
        )

        # 실제 플랫폼을 선택했을 때 세션 상태 갱신 및 페이지 전환
        if platform_selection != "플랫폼을 선택하세요":
            if platform_selection != st.session_state.get("platform"):
                st.session_state["platform"] = platform_selection  
                st.session_state["page"] = "generate_ad"
                st.session_state["step"] = 1
                st.rerun()

    # '홈' 혹은 '갤러리' 선택 시 페이지 전환 및 플랫폼 초기화
    elif st.session_state["page"] != selected_page:
        st.session_state["page"] = selected_page
        st.session_state["step"] = 1
        st.session_state["platform"] = None
        st.rerun()

#######################################################################################################

# 페이지 렌더링 분기

# 홈 페이지 렌더링
if st.session_state["page"] == "home":
    home.render()

# 갤러리 페이지 렌더링
elif st.session_state["page"] == "gallery":
    gallery.render()

# 광고 생성 페이지 렌더링
elif st.session_state["page"] == "generate_ad":
    step = st.session_state.get("step", 1)
    platform = st.session_state.get("platform", None)

    if platform is None:
        st.warning("플랫폼을 선택해주세요.")
        st.stop()

    # 서브페이지 렌더링
    if step == 1:
        sub_page_1.render(platform=platform)
    elif step == 2:
        sub_page_2.render(platform=platform)
    elif step == 3:
        sub_page_3.render(platform=platform)
    elif step == 4:
        sub_page_4.render(platform=platform)
    elif step == 5:
        sub_page_5.render(platform=platform)

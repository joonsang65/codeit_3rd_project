import streamlit as st
from pathlib import Path


def render():
    ###########################################################################################
    # 세션 상태 초기화
    st.session_state.setdefault("page", "sub_page_3")

    ###########################################################################################
    # 제목
    st.title("3️⃣텍스트 생성")
    st.markdown("---")

    ###########################################################################################
    # 5. 이전 / 다음 버튼
    prev_col, _, next_col = st.columns([1, 1, 1])

    with prev_col:
        if st.button("⬅ 이전"):
            st.session_state["page"] = "sub_page_2"
            st.rerun()

    with next_col:
        if st.button("➡ 다음"):
            st.session_state["page"] = "sub_page_4"
            st.rerun()

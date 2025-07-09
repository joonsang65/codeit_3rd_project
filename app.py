import streamlit as st
from utils import gallery
from utils.pages import sub_page_1, sub_page_2, sub_page_3, sub_page_4, sub_page_5

# config 설정  -> 여기서 한 번만 해야 함
st.set_page_config(layout="wide")

# 초기 페이지 상태 설정도 여기서만
st.session_state.setdefault("page", "sub_page_1")

# 페이지 라우팅
if st.session_state["page"] == "sub_page_1":
    sub_page_1.render()
elif st.session_state["page"] == "sub_page_2":
    sub_page_2.render()
elif st.session_state["page"] == "sub_page_3":
    sub_page_3.render()
elif st.session_state["page"] == "sub_page_4":
    sub_page_4.render()
elif st.session_state["page"] == "sub_page_5":
    sub_page_5.render()
else:
    st.error(f"알 수 없는 페이지: {st.session_state['page']}")
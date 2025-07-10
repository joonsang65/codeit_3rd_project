import streamlit as st


def render(platform):
    ###########################################################################################
    # 세션 상태 초기화
    st.session_state.setdefault("page", "sub_page_3")

    ###########################################################################################
    # 제목
    st.title("5️⃣ 폴더 트리 (이 페이지는 삭제 예정)")
    st.markdown("---")
    st.subheader('''폴더 구조
    📦streamlit_base
    ┣ 📂.streamlit
    ┃ ┗ 📜config.toml
    ┣ 📂utils
    ┃ ┣ 📂images
    ┃ ┃ ┣ 📜combine.png
    ┃ ┃ ┣ 📜composed.png
    ┃ ┃ ┣ 📜ex_back.png
    ┃ ┃ ┣ 📜ex_raccoon_raw.png
    ┃ ┃ ┣ 📜ex_raccoon_RB.png
    ┃ ┃ ┣ 📜final_composed_20250709_061248.png
    ┃ ┃ ┣ 📜output.png
    ┃ ┃ ┗ 📜text_preview.png
    ┃ ┣ 📂pages
    ┃ ┃ ┣ 📜sub_page_1.py
    ┃ ┃ ┣ 📜sub_page_2.py
    ┃ ┃ ┣ 📜sub_page_3.py
    ┃ ┃ ┣ 📜sub_page_4.py
    ┃ ┃ ┣ 📜sub_page_5.py
    ┃ ┃ ┗ 📜__init__.py
    ┃ ┣ 📜fonts.py
    ┃ ┣ 📜functions.py
    ┃ ┣ 📜gallery.py
    ┃ ┣ 📜home.py
    ┃ ┗ 📜__init__.py
    ┣ 📜.dockerignore
    ┣ 📜app.py
    ┣ 📜docker-compose.yml
    ┣ 📜Dockerfile
    ┣ 📜requirements.txt
    ┗ 📜__init__.py''')

    st.markdown("---")

    _, col_btns, _ = st.columns([1, 1, 1])
    with col_btns:
        prev_col, next_col = st.columns(2)
        with prev_col:
            if st.button("⬅ 이전"):
                st.session_state["page"] = "sub_page_4"
                st.rerun()
        with next_col:
            if st.button("처음으로"):
                st.session_state["page"] = "sub_page_1"
                st.rerun()
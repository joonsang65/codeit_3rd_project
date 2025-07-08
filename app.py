import streamlit as st
from fonts import FONTS
from downloader import download_font
from generate import render_text_image

def main():
    st.title("텍스트 이미지 생성기")
    st.markdown("텍스트를 입력하고 원하는 폰트를 선택해 이미지를 생성하세요!")

    # 입력 받기
    col1, col2 = st.columns(2)
    with col1:
        text = st.text_input("이미지에 넣을 텍스트를 입력하세요", value="안녕하세요!")
        font_name = st.selectbox("사용할 폰트를 선택하세요", options=list(FONTS.keys()))
    
    with col2:
        size = st.slider("글자 크기를 선택하세요", min_value=50, max_value=200, value=125, step=1)
        text_color = st.color_picker("텍스트 색상을 선택하세요", "#000000")
        stroke_color = st.color_picker("테두리 색상을 선택하세요", "#FFFFFF")
        stroke_width = st.slider("테두리 굵기를 선택하세요", min_value=0, max_value=10, value=0, step=1)
        output_filename = st.text_input("저장할 파일명 (예: output.png)", value="output.png")

    # 상태 유지 변수
    if "generated_img" not in st.session_state:
        st.session_state.generated_img = None

    if st.button("이미지 생성하기"):
        font_url = FONTS[font_name]
        font_path = download_font(font_name, font_url)

        img, fmt = render_text_image(
            text=text,
            font_path=font_path,
            font_size=size,
            text_color=text_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            background_size=(size * (len(text) + 1), size * 2)
        )
        try:
            st.session_state.generated_img = img  # 이미지 저장
            st.image(img, caption="미리보기", use_container_width=True)
            st.success("이미지 미리보기 생성 완료")

        except Exception as e:
            st.error(f"오류 발생: {e}")        
            st.session_state.generated_img = None

    # 저장 버튼: 이미지가 있는 경우에만 표시
    if st.session_state.generated_img is not None:
        if st.button("이미지 저장하기"):
            try:
                img = st.session_state.generated_img
                if (output_filename.split(".")[1]).upper() in {"JPEG", "ICO", "PPM", "HEIF"}:
                # 얘네는 투명도 조절이 불가능해서 RGB로 변환해줘야 함    
                    img = img.convert("RGB")
                img.save(output_filename)
                st.success(f"이미지 저장 완료: {output_filename}")
            except Exception as e:
                st.error(f"저장 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
import streamlit as st
from fonts import PIL_COMPATIBLE_FONTS
from downloader import download_font
from generate import render_text_image

def main():
    st.title("🖋️ 텍스트 이미지 생성기")
    st.markdown("텍스트를 입력하고 원하는 폰트를 선택해 이미지를 생성하세요!")

    # 입력 받기
    text = st.text_input("👉 이미지에 넣을 텍스트를 입력하세요", value="안녕하세요!")
    font_name = st.selectbox("👉 사용할 폰트를 선택하세요", options=list(PIL_COMPATIBLE_FONTS.keys()))
    size = st.slider("👉 글자 크기를 선택하세요", min_value=10, max_value=200, value=64, step=2)
    output_filename = st.text_input("👉 저장할 파일명 (예: output.png)", value="output.png")
    align = st.radio("👉 텍스트 정렬", options=["center", "left", "right"], index=0)

    # 버튼 클릭 시 처리
    if st.button("🎨 이미지 생성하기"):
        try:
            font_url = PIL_COMPATIBLE_FONTS[font_name]
            font_path = download_font(font_name, font_url)

            output_path = render_text_image(
                text=text,
                font_path=font_path,
                font_size=size,
                output_path=output_filename,
                align=align
            )

            st.success(f"✅ 이미지 생성 완료: {output_path}")
            st.image(output_path)

        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
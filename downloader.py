def download_font(font_name, font_url, save_dir="downloaded_fonts"):
    import os
    import requests

    os.makedirs(save_dir, exist_ok=True)
    ext = ".otf"
    save_path = os.path.join(save_dir, f"{font_name}{ext}")

    if os.path.exists(save_path):
        print(f"📂 이미 존재하는 폰트 사용: {save_path}")
        return save_path

    print(f"⬇️ 폰트 다운로드 중: {font_name}")
    response = requests.get(font_url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"✅ 다운로드 완료: {save_path}")
        return save_path
    else:
        print(f"❌ 다운로드 실패 - 상태 코드: {response.status_code}")
        print(f"❌ 응답 내용 일부:\n{response.text[:300]}")
        raise RuntimeError(f"❌ 다운로드 실패: {font_url}")
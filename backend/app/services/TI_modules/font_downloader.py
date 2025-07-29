import os
import requests
from typing import Optional
from services.TI_modules.TI_config import settings

class FontDownloader:
    def __init__(self):
        self.save_dir = settings.font_download_dir
        os.makedirs(self.save_dir, exist_ok=True)
    
    def download_font(self, font_name: str, font_url: str) -> Optional[str]:
        """
        폰트를 다운로드하고 저장 경로를 반환합니다.
        
        Args:
            font_name: 폰트 이름
            font_url: 폰트 다운로드 URL
            
        Returns:
            폰트 파일 경로 또는 None (실패 시)
        """
        try:
            # 확장자 결정
            ext = ".otf" if font_url.endswith(".otf") else ".ttf"
            save_path = os.path.join(self.save_dir, f"{font_name}{ext}")
            
            # 이미 존재하는 경우 기존 파일 사용
            if os.path.exists(save_path):
                print(f"이미 존재하는 폰트 사용: {save_path}")
                return save_path
            
            print(f"폰트 다운로드 중: {font_name}")
            response = requests.get(font_url, timeout=30)
            
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print(f"다운로드 완료: {save_path}")
                return save_path
            else:
                print(f"다운로드 실패 - 상태 코드: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"폰트 다운로드 중 오류 발생: {str(e)}")
            return None
    
    def get_font_path(self, font_name: str, font_url: str) -> Optional[str]:
        """
        폰트 경로를 반환합니다. URL인 경우 다운로드하고, 로컬 파일인 경우 경로를 확인합니다.
        
        Args:
            font_name: 폰트 이름
            font_url: 폰트 URL 또는 로컬 경로
            
        Returns:
            폰트 파일 경로 또는 None
        """
        if font_url.startswith("http"):
            return self.download_font(font_name, font_url)
        else:
            # 로컬 파일인 경우
            if os.path.exists(font_url):
                return font_url
            else:
                print(f"로컬 폰트 파일을 찾을 수 없습니다: {font_url}")
                return None

# 전역 인스턴스
font_downloader = FontDownloader()
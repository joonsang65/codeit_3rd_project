from pydantic_settings import BaseSettings

class ImageGenSettings(BaseSettings):
    app_name: str = "Text Image Generator"
    debug: bool = False
    font_download_dir: str = "./app/services/TI_modules/downloaded_fonts"
    max_font_size: int = 100
    min_font_size: int = 10
    max_background_size: int = 2048
    
    class Config:
        env_file = ".env"
        extra = "allow"
        env_prefix = "IMAGEGEN_"

settings = ImageGenSettings()

# 폰트 정의
FONTS = {
"본고딕_BOLD" : "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/KR/SourceHanSansKR-Bold.otf",
"본고딕_EXTRALIGHT" : "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/KR/SourceHanSansKR-ExtraLight.otf",
"본고딕_HEAVY" : "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/KR/SourceHanSansKR-ExtraLight.otf",
"본고딕_LIGHT" : "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/KR/SourceHanSansKR-Light.otf",
"본고딕_MEDIUM" : "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/KR/SourceHanSansKR-Medium.otf",
"본고딕_NORMAL" : "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/KR/SourceHanSansKR-Normal.otf",
"본고딕_REGULAR" : "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/KR/SourceHanSansKR-Regular.otf",
"BagelFatOne-Regular": "imageGen_Text/downloaded_fonts/BagelFatOne-Regular.ttf",
"나눔손글씨 고딕 아니고 고딩": "imageGen_Text/downloaded_fonts/나눔손글씨 고딕 아니고 고딩.ttf",
"나눔손글씨 갈맷글": "/imageGen_Text/downloaded_fonts/나눔손글씨 갈맷글.ttf",
"나눔손글씨 강인한 위로": "imageGen_Text/downloaded_fonts/나눔손글씨 강인한 위로.ttf",
"파셜산스": "imageGen_Text/downloaded_fonts/PartialSansKR-Regular.otf",
"날씨" : "imageGen_Text/downloaded_fonts/ClimateCrisisKR-2019.otf",
"베이글" : "imageGen_Text/downloaded_fonts/BagelFatOne-Regular.ttf",
"쿠키런 블랙" : "imageGen_Text/downloaded_fonts/CookieRun Black.otf",
"쿠키런 볼드" : "imageGen_Text/downloaded_fonts/CookieRun Bold.otf",
"쿠키런 레귤러" : "imageGen_Text/downloaded_fonts/CookieRun Regular.otf",
}

# 확장자 → 포맷 매핑
EXT_TO_FORMAT = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".bmp": "BMP",
    ".gif": "GIF",
    ".tif": "TIFF",
    ".tiff": "TIFF",
    ".webp": "WEBP",
    ".ico": "ICO",
    ".ppm": "PPM",
    ".pbm": "PPM",
    ".pgm": "PPM",
    ".pnm": "PPM",
    ".heif": "HEIF",
    ".heic": "HEIC",
}
import logging
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO, log_to_file: Optional[str] = None) -> logging.Logger:
    """
    모듈별 로거를 설정합니다.

    Args:
        name (str): 로거 이름
        level (int): 로그 레벨
        log_to_file (str, optional): 로그를 파일로 저장할 경로

    Returns:
        Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

        if log_to_file:
            file_handler = logging.FileHandler(log_to_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)

    return logger
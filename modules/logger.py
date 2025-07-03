import logging

def setup_logger(name, level=logging.DEBUG):
    """
    지정된 이름과 로그 레벨로 로거를 설정합니다.

    Args:
        name (str): 로거 이름. (__name__)
        level (int): 로깅 레벨 (기본값: logging.DEBUG).

    Returns:
        logging.Logger: 설정된 로거 인스턴스.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s", 
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

    return logger
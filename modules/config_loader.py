import yaml
from typing import Any, Dict


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    """
    YAML 구성 파일을 로드하여 딕셔너리로 반환합니다.

    Args:
        path (str): YAML 파일 경로

    Returns:
        dict: 구성 데이터
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] 설정 파일을 찾을 수 없습니다: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"[ERROR] YAML 파싱 오류: {e}")

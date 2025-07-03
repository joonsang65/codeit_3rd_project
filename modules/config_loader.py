import yaml

def load_config(path="config.yaml"):
    """
    config.yaml을 불러옵니다.

    Args:
        - path: config.yaml의 경로
    """
    with open(path, "r") as f:
        return yaml.safe_load(f)
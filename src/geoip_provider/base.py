class BaseProvider:
    def __init__(self, config: str):
        pass

    def annotate(self, ip: str) -> dict:
        return {}

    def get_labels(self) -> list:
        return []

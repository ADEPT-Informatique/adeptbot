from . import BaseRequest

class BanRequest(BaseRequest):
    def __init__(self, reason: str, duration: int) -> None:
        self.reason = reason
        self.duration = duration

class BanResponse():
    pass

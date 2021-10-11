from . import BaseRequest

class MuteRequest(BaseRequest):
    def __init__(self, reason: str, duration: int) -> None:
        self.reason = reason
        self.duration = duration

class BanResponse():
    pass

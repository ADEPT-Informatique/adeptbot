from data import BaseRequest

class BanRequest(BaseRequest):
    def __init__(self, member_id: int, guild_id: int, reason: str, duration: int) -> None:
        self.member_id = member_id
        self.guild_id = guild_id
        self.reason = reason
        self.duration = duration

class BanResponse():
    pass
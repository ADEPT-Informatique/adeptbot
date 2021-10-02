from models.mute import MuteRequest
from .base_client import BaseClient
import discord

class MuteService(BaseClient):
    MUTE_URL = "/discord/mute"

    def __init__(self, loop=None) -> None:
        super().__init__(loop=loop)
        self.MUTE_URL = self._get_api_url(self.MUTE_URL)
    
    async def mute(self, member: discord.Member, reason: str, duration: int):
        mute_request = MuteRequest(member.id, member.guild.id, reason, duration)

        return await self.post(self.MUTE_URL, mute_request)

    async def unmute(self, member: discord.Member, reason: str):
        return await self.delete(self.MUTE_URL, user_id=member.id, reason=reason)

    async def fetch_temp_mutes(self):
        return await self.get(self.MUTE_URL)
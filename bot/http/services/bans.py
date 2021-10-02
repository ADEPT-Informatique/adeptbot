from models.ban import BanRequest
from . import BaseClient
import discord

class BanService(BaseClient):
    BAN_URL = "/discord/ban"

    def __init__(self, loop=None) -> None:
        super().__init__(loop=loop)
        self.BAN_URL = self._get_api_url(self.BAN_URL)
    
    async def ban(self, member: discord.Member, reason: str, duration: int):
        ban_request = BanRequest(member.id, member.guild.id, reason, duration)

        return await self.post(self.BAN_URL, ban_request)

    async def unban(self, member: discord.Member, reason: str):
        return await self.delete(self.BAN_URL + f"/{member.id}", reason=reason)

    async def fetch_temp_bans(self, guild: discord.Guild):
        return await self.get(self.BAN_URL, guild_id=guild.id)
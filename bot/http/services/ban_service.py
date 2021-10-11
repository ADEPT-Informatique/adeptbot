import discord

from . import BaseClient
from ..models import BanRequest


class BanService(BaseClient):
    BAN_URL = "/discord/ban"

    def __init__(self, loop=None) -> None:
        super().__init__(loop=loop)
        self.BAN_URL = self._get_api_url(self.BAN_URL)

    async def ban(self, member: discord.Member, reason: str, duration: int):
        ban_request = BanRequest(reason, duration)

        return await self.post(self.BAN_URL + f"/{member.id}", ban_request)

    async def unban(self, member: discord.Member, reason: str):
        return await self.delete(self.BAN_URL + f"/{member.id}", reason=reason)

    async def fetch_temp_bans(self, guild: discord.Guild):
        return await self.get(self.BAN_URL, guild_id=guild.id)

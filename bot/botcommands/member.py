import util
from discord.ext import commands

from run import AdeptClient


class MemberCog(commands.Cog):
    def __init__(self, client: AdeptClient) -> None:
        super().__init__()
        self.client = client

    @commands.command()
    async def setup(self, ctx):
        result = await self.client.walk_through_welcome(ctx.author)
        await util.process_welcome_result(ctx.author, result)

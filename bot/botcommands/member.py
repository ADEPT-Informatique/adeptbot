from discord.ext import commands
from discord.ext.commands.context import Context

from bot import util, welcome


class MemberCog(commands.Cog):
    @commands.command()
    async def setup(self, ctx: Context):
        await ctx.reply("Nous vous avons envoyé un message en privé avec les instructions!")
        result = await welcome.walk_through_welcome(ctx.author)
        await welcome.process_welcome_result(ctx.author, result)

    async def cog_command_error(self, ctx: Context, error):
        raise error
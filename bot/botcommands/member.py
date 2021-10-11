import traceback
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandInvokeError

from bot import welcome, util


class MemberCog(commands.Cog):
    @commands.command()
    async def setup(self, ctx: Context):
        await ctx.reply("Nous vous avons envoyé un message en privé avec les instructions!")
        result = await welcome.walk_through_welcome(ctx.author)
        await welcome.process_welcome_result(ctx.author, result)

    async def cog_command_error(self, ctx: Context, error):
        if isinstance(error, CommandInvokeError):
            error = error.original
        
        if isinstance(error, welcome.NoReplyException):
            await util.exception(error.channel, error.message)
            return # We don't want to print the traceback
        
        if ctx is not None:
            await util.exception(ctx.channel, error)
            return
        
        traceback.print_exc()

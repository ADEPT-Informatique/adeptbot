import disnake
import traceback
from disnake.ext import commands

import configs
from bot import welcome, util


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        await ctx.reply("Nous vous avons envoyé un message en privé avec les instructions!")
        result = await welcome.walk_through_welcome(ctx.author)
        await welcome.process_welcome_result(ctx.author, result)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        await self.bot.say(configs.WELCOME_CHANNEL, configs.WELCOME_SERVER.format(name=member.mention))
        result = await welcome.walk_through_welcome(member)

        await welcome.process_welcome_result(member, result)

    @commands.Cog.listener()
    async def on_error(self, event, *args):

        if isinstance(event, commands.CommandInvokeError):
            error = event.original
            if isinstance(error, welcome.NoReplyException):
                await util.exception(error.channel, error.message)

            elif isinstance(error, disnake.Forbidden):
                await util.logger.error("Can't apply roles to the user", error)
            else:
                # We suppress the other errors, might be check errors but they are not important
                # It should mostly be the case of the user trying to use the bot in DMs
                pass

        traceback.print_exc()

import disnake
from disnake.ext import commands

import configs
from bot import util, welcome


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
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
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, util.AdeptBotError):
            await util.say(error.channel, error.message)
        else:
            await ctx.reply("Une erreur inconnue est survenue. Veuillez réessayer plus tard.")
            raise error

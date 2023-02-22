"""Welcome management cog."""

import discord
from discord.ext import commands

import configs
from bot import util, welcome


class WelcomeCog(commands.Cog):
    """This class contains the events related to welcome."""

    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """Setup the member."""
        author: discord.Member = ctx.author
        message = await ctx.reply("Nous vous avons envoyé un message en privé avec les instructions!")
        try:
            result = await welcome.walk_through_welcome(author)
            await welcome.process_welcome_result(author, result)
        except discord.Forbidden as error:
            await message.delete()
            raise error

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """This event is called when a member joins the server."""
        await util.say(configs.WELCOME_CHANNEL, configs.WELCOME_SERVER.format(name=member.mention))
        result = await welcome.walk_through_welcome(member)
        await welcome.process_welcome_result(member, result)

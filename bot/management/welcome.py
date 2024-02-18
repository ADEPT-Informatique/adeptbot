"""Welcome management cog."""

import discord
from discord.ext import commands

import configs
from bot import util, welcome
from bot.db.services import UserService
from bot.db.models import AdeptMember


class WelcomeCog(commands.Cog):
    """This class contains the events related to welcome."""

    def __init__(self) -> None:
        self.user_service = UserService()

    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """Setup the member."""
        author = ctx.author
        message = await ctx.reply("Nous vous avons envoyé un message en privé avec les instructions!")
        try:
            result = await welcome.walk_through_welcome(author)
            if not result:
                return

            self.user_service.update_one({"_id": result._id}, result.__getstate__(), upsert=True)
            await welcome.process_welcome_result(author, result)
        except discord.Forbidden as error:
            await message.delete()
            raise error

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """This event is called when a member joins the server."""
        adept_member = await self.user_service.find_by_id(member.id)
        if adept_member:
            return await welcome.process_welcome_result(member, adept_member)

        await util.say(configs.WELCOME_CHANNEL, configs.WELCOME_SERVER.format(name=member.mention))
        result = await welcome.walk_through_welcome(member)
        if not result:
            return

        self.user_service.update_one({"_id": result._id}, result.__getstate__(), upsert=True)
        await welcome.process_welcome_result(member, result)

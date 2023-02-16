"""This module contains the StrikesCog class."""

import discord
from discord.ext import commands

import configs
from bot import tasks, users
from bot.db.services.configs_service import ConfigsService
from bot.util import display_time


class StrikesCog(commands.Cog):
    """This class contains the events related to strikes."""

    def __init__(self) -> None:
        self.__configs_service = ConfigsService()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        This event is called when a message is sent to detect spam.

        A member will be muted if he sends more than 3 messages in less than 0.5 seconds.
        """
        if (message.author.bot or isinstance(message.channel, discord.DMChannel)):
            return

        member = message.author
        user: users.User = await users.get_user(member)
        if user is None:
            user = await users.create_user(member, message.created_at.timestamp())

        guild = message.guild
        trust_role = guild.get_role(configs.TRUST_ROLE)
        if (message.created_at.timestamp() - user.last_message_timestamp) < 0.5 and \
                member.roles[-1].position < trust_role.position:
            user.strikes += 1

            spam_configs = self.__configs_service.find_or_create_spam_configs()
            if user.strikes % spam_configs.repetition == 0:
                times = user.strikes / spam_configs.repetition

                mute_time = spam_configs.mute_time * times
                await tasks.create_mute_task(member, mute_time)

                readable_time = display_time(mute_time)
                await message.channel.send(
                    f"{member.mention} est maintenant muet pour {readable_time} en raison du spam!"
                )

        user.last_message_timestamp = message.created_at.timestamp()

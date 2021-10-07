import asyncio
import discord
import traceback
from discord.ext import commands
from typing import Union

import configs
from bot import tasks, util
from bot.botcommands import member, moderation
from bot.welcome import NoReplyException


class AdeptClient(commands.Bot):
    def __init__(self, prefix):
        intents = discord.Intents.default()
        intents.members = True
        loop = asyncio.get_event_loop()
        super().__init__(prefix, loop=loop, intents=intents)
        self.loop = loop

        self.add_cog(member.MemberCog())
        self.add_cog(moderation.ModerationCog(self))

    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.abc.PrivateChannel):
            return

        message.content = message.content.replace(f"<@!{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@!{self.user.id}>") else message.content
        message.content = message.content.replace(f"<@{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@{self.user.id}>") else message.content

        if message.content.startswith(configs.PREFIX):
            await self.process_commands(message)

    async def on_ready(self):
        util._load(self)
        util.logger.info("\nLogged in with account @%s ID:%s \n-------",
                        self.user.name, self.user.id)

        await self.change_presence(activity=discord.Activity(name="for bad boys!", type=discord.ActivityType.watching))
        tasks._load_tasks(self)

    async def on_member_join(self, member: discord.Member):
        await self.say(configs.WELCOME_CHANNEL, configs.WELCOME_SERVER.format(name=member.mention))
        result = await util.walk_through_welcome(member)

        await util.process_welcome_result(member, result)


    async def on_error(self, event, *args):
        if isinstance(event, NoReplyException):
            await util.exception(event.channel, event.message)
            return # We don't want to print the traceback
        
        traceback.print_exc()

    async def say(self, channel: Union[discord.TextChannel, str], *args, **kwargs):
        if type(channel) is str:
            # channel_id/server_id
            channel_id, server_id = channel.split("/")
            channel = self.get_guild(int(server_id)).get_channel(int(channel_id))
        try:
            return await channel.send(*args, **kwargs)
        except discord.Forbidden as send_error:
            util.logger.warning(send_error)


if __name__ == "__main__":
    util.logger.info("Starting the bot!")
    client = AdeptClient(prefix=configs.PREFIX)
    client.run(configs.TOKEN)

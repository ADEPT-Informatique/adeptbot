import traceback
import discord
from discord.ext import commands
import sys
import asyncio
import re

import configs
from bot import util, tasks
from bot.botcommands import moderation

bot_prefix = "!"

class AdeptClient(commands.Bot):
    def __init__(self, token, prefix):
        intents = discord.Intents.default()
        intents.members = True
        loop = asyncio.get_event_loop()
        super().__init__(prefix, loop=loop, intents=intents)
        self.loop = loop
        
        self.add_cog(moderation.Moderation(self))

        self.run(token)

    async def on_message(self, message):
        if isinstance(message.channel, discord.abc.PrivateChannel):
            return

        mentions_self_regex = f"<@.?{self.user.id}>"
        if re.match("^"+mentions_self_regex, message.content):
            message.content = re.sub(mentions_self_regex + "\s*", bot_prefix, message.content)
        
        if message.content.startswith(bot_prefix):
            await self.process_commands(message)

    async def on_ready(self):
        util._load(self)

        # Bot logs
        channel_id, server_id = configs.bot_logs.split("/")
        configs.bot_logs = self.get_guild(int(server_id)).get_channel(int(channel_id))
        
        # Moderation Logs
        channel_id, server_id = configs.mod_logs.split("/")
        configs.mod_logs = self.get_guild(int(server_id)).get_channel(int(channel_id))

        await self.say(configs.bot_logs, "Bot started!")
        util.logger.info("\nLogged in with account @%s ID:%s \n-------",
                        self.user.name, self.user.id)

        await self.change_presence(activity=discord.Activity(name="for bad boys!", type=discord.ActivityType.watching))
        tasks._load_tasks(self)

    async def on_member_join(self, member: discord.Member):
        await member.create_dm()
        await member.send

    async def on_error(self, event, *args,  **kwargs):
        traceback.print_exc()

    async def say(self, channel, *args, **kwargs):
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
    client = AdeptClient(configs.bot_token, prefix=bot_prefix)
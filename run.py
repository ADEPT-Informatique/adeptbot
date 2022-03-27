import asyncio
import sys
import disnake
import traceback
from disnake.ext import commands

import configs
from bot import tasks, util
from bot.botcommands import MemberCog, ModerationCog
from bot.interactions import TicketOpeningInteraction, TicketCloseInteraction


class AdeptClient(commands.Bot):
    def __init__(self, prefix):
        intents = disnake.Intents.all()
        loop = asyncio.get_event_loop_policy().new_event_loop()
        super().__init__(prefix, loop=loop, intents=intents, case_insensitive=True)

        self.add_cog(MemberCog(self))
        self.add_cog(ModerationCog(self))
        self.persistent_views_loaded = False

    async def on_ready(self):
        util._load(self)
        util.logger.info(f"\nLogged in with account @{self.user.name} ID:{self.user.id} \n------------------------------------\n")
        
        if not self.persistent_views_loaded:
            self.add_view(TicketOpeningInteraction())
            self.add_view(TicketCloseInteraction())
            self.persistent_views_loaded = True

        await self.change_presence(activity=disnake.Activity(name="for bad boys!", type=disnake.ActivityType.watching))
        tasks._load_tasks(self)

    async def on_message(self, message: disnake.Message):
        if (message.author.bot):
            return

        message.content = message.content.replace(f"<@!{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@!{self.user.id}>") else message.content
        message.content = message.content.replace(f"<@{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@{self.user.id}>") else message.content

        if message.content.startswith(configs.PREFIX):
            await self.process_commands(message)

    async def say(self, channel: disnake.TextChannel | str, *args, **kwargs):
        if type(channel) is str:
            # channel_id/server_id
            channel_id, server_id = channel.split("/")
            channel = self.get_guild(int(server_id)).get_channel(int(channel_id))
        try:
            return await channel.send(*args, **kwargs)
        except disnake.Forbidden as send_error:
            util.logger.warning(send_error)

    async def on_error(self, _: str, *args) -> None:
        error = sys.exc_info()[1]
        
        await self.handle_error(error)

    async def handle_error(self, error, ctx: commands.Context = None):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, util.AdeptBotError):
            await util.say(error.channel, error.message)
        else:
            if ctx is not None:
                await util.say(ctx.channel, ":bangbang: **Une erreur est survenue**")
            
            util.logger.error(f"Une erreur inconnue est survenue.\n```{traceback.format_exc()}```")


if __name__ == "__main__":
    util.logger.info("Starting the bot!")
    client = AdeptClient(prefix=configs.PREFIX)
    client.run(configs.TOKEN)

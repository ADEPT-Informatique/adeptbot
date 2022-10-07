import sys

import discord
from discord.ext import commands
from discord.ext.commands.errors import (BadArgument, CommandInvokeError,
                                         CommandNotFound, MissingAnyRole,
                                         MissingRequiredArgument,
                                         NoPrivateMessage, UserNotFound)

import configs
from bot import tasks, util
from bot.botcommands import BotConfigsCog, MemberCog, ModerationCog
from bot.interactions import TicketCloseInteraction, TicketOpeningInteraction
from bot.interactions.errors import NoReplyException
from bot.management import LoggingCog, StrikesCog, WelcomeCog


class AdeptClient(commands.Bot):
    def __init__(self, prefix, intents):
        super().__init__(prefix, intents=intents, case_insensitive=True)

    async def on_ready(self):
        util.logger.info(f"\nLogged in with account @{self.user.name} ID:{self.user.id} \n------------------------------------\n")

        await self.change_presence(activity=discord.Activity(name="for bad boys!", type=discord.ActivityType.watching))
        tasks._load_tasks()

    async def setup_hook(self) -> None:
        # Register cogs
        await self.add_cog(BotConfigsCog())
        await self.add_cog(LoggingCog())
        await self.add_cog(MemberCog())
        await self.add_cog(ModerationCog())
        await self.add_cog(StrikesCog())
        await self.add_cog(WelcomeCog())

        # Register persistent views
        self.add_view(TicketOpeningInteraction())
        self.add_view(TicketCloseInteraction())

        # Inject itself to the util module
        util._load(self)

    async def on_message(self, message: discord.Message):
        if (message.author.bot):
            return

        message.content = message.content.replace(f"<@!{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@!{self.user.id}>") else message.content
        message.content = message.content.replace(f"<@{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@{self.user.id}>") else message.content

        if message.content.startswith(configs.PREFIX):
            await self.process_commands(message)

    async def say(self, channel: discord.abc.Messageable | str, *args, **kwargs):
        if type(channel) is str:
            # channel_id/server_id
            channel_id, server_id = channel.split("/")
            channel = self.get_guild(int(server_id)).get_channel(int(channel_id))
        try:
            return await channel.send(*args, **kwargs)
        except discord.Forbidden as send_error:
            util.logger.warning(send_error)
    
    async def on_error(self, _, *args):
        ctx: commands.Context = args[0] if len(args) == 1 else None
        error = sys.exc_info()[1]

        if ctx:
            await self.on_command_error(ctx, error) # Sketchy but works flawlessly (:
            return
        
        util.logger.error(error)

    async def on_command_error(self, ctx: commands.Context, exception: commands.errors.CommandError) -> None:
        if isinstance(exception, CommandInvokeError):
            exception = exception.original

        if isinstance(ctx, CommandNotFound):
            return

        elif isinstance(exception, NoPrivateMessage):
            await ctx.send("Cette commande ne peut pas être utilisée en message privé.")
            return

        elif isinstance(exception, UserNotFound):
            await ctx.send("Utilisateur introuvable.")
            return

        elif isinstance(exception, MissingAnyRole):
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
            return

        elif isinstance(exception, MissingRequiredArgument):
            await ctx.send(f"Argument manquant: {exception.param.name}")
            return

        elif isinstance(exception, BadArgument):
            await ctx.send(f"Argument invalide: {exception.param.name}")
            return

        elif isinstance(exception, NoReplyException):
            await exception.channel.send(exception.message)
            return

        elif isinstance(exception, util.AdeptBotException):
            await ctx.send(exception.message)
            return

        return await super().on_command_error(ctx, exception)


if __name__ == "__main__":
    util.logger.info("Starting the bot!")
    
    intents = discord.Intents.all()
    client = AdeptClient(configs.PREFIX, intents)

    client.run(configs.TOKEN)

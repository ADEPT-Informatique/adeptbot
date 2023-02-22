"""Main file of the bot."""

import sys
import traceback

import discord
from discord.ext import commands
from discord.ext.commands.errors import (
    BadArgument,
    CommandInvokeError,
    CommandNotFound,
    MissingAnyRole,
    MissingRequiredArgument,
    NoPrivateMessage,
    UserNotFound,
)

import configs
from bot import tasks, util
from bot.botcommands import BotConfigsCog, MemberCog, ModerationCog
from bot.interactions import TicketCloseInteraction, TicketOpeningInteraction
from bot.interactions.errors import NoReplyException
from bot.management import LoggingCog, StrikesCog, WelcomeCog


class AdeptClient(commands.Bot):
    """Main class of the bot."""

    def __init__(self, prefix: str, intents: discord.Intents):
        super().__init__(prefix, intents=intents, case_insensitive=True)

    async def on_ready(self):
        """Called when the bot is ready."""
        util.logger.info(
            "\nLogged in with account @%s ID:%s \n------------------------------------\n", self.user.name, self.user.id
        )

        await self.change_presence(activity=discord.Activity(name="for bad boys!", type=discord.ActivityType.watching))
        tasks.load_tasks()

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
        util.load(self)

    async def on_message(self, message: discord.Message, /):
        if message.author.bot:
            return

        if message.content.startswith(f"<@!{self.user.id}>") or message.content.startswith(f"<@{self.user.id}>"):
            message.content = message.content.replace(f"<@!{self.user.id}>", configs.PREFIX, 1)
            message.content = message.content.replace(f"<@{self.user.id}>", configs.PREFIX, 1)

        if message.content.startswith(configs.PREFIX):
            await self.process_commands(message)

    async def say(self, channel: discord.abc.Messageable | str, *args, **kwargs):
        """
        Send a message to a channel.

        Parameters
        ----------
        - channel: The channel to send the message to.
        - *args: The arguments to pass to the send method.
        - **kwargs: The keyword arguments to pass to the send
        method.

        Returns
        -------
        The message sent.
        """
        if isinstance(channel, str):
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
            await self.on_command_error(ctx, error)  # Sketchy but works flawlessly (:
            return

        util.logger.error(error)

    async def on_command_error(self, ctx: commands.Context, exception: commands.errors.CommandError, /) -> None:
        if isinstance(exception, CommandInvokeError):
            exception = exception.original

        if isinstance(ctx, CommandNotFound):
            # We don't care
            pass

        elif isinstance(exception, NoPrivateMessage):
            await ctx.send("Cette commande ne peut pas être utilisée en message privé.")

        elif isinstance(exception, UserNotFound):
            await ctx.send("Utilisateur introuvable.")

        elif isinstance(exception, MissingAnyRole):
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")

        elif isinstance(exception, MissingRequiredArgument):
            await ctx.send(f"Argument manquant: {exception.param.name}")

        elif isinstance(exception, BadArgument):
            await ctx.send(f"Argument invalide: {exception.param.name}")

        elif isinstance(exception, NoReplyException):
            await exception.channel.send(exception.message)

        elif isinstance(exception, discord.Forbidden):
            # Check if the error is about not being able to send a DM
            if exception.code == 50007:
                await ctx.reply(configs.WELCOME_CANT_DM)

        elif isinstance(exception, util.AdeptBotException):
            await ctx.send(exception.message)

        else:
            # Log any uncatched error in the logging channel
            await self.say(configs.LOGS_CHANNEL, f"```py\n{traceback.format_exc()[-1500:]}```")
            await super().on_command_error(ctx, exception)


if __name__ == "__main__":
    util.logger.info("Starting the bot!")

    all_intents = discord.Intents.all()
    client = AdeptClient(configs.PREFIX, all_intents)

    client.run(configs.TOKEN)

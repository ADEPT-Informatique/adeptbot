import configs
import discord
from bot.util import AdeptBotException


class NoReplyException(AdeptBotException):
    def __init__(self, channel: discord.abc.Messageable) -> None:
        self.channel = channel
        super().__init__(f"Nous n'avons pas reçu de réponse! Utilisez `{configs.PREFIX}setup` dans <#{configs.SETUP_CHANNEL}> pour recommencer.")


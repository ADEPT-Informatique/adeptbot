"""Errors used for interactions."""

import discord

import configs
from bot.util import AdeptBotException


class NoReplyException(AdeptBotException):
    """
    Raised when the user doesn't reply to the interaction in time.

    Attributes
    ----------
    `channel` : discord.abc.Messageable
        The channel the interaction was sent in.
    """

    def __init__(self, channel: discord.abc.Messageable) -> None:
        self.channel = channel
        super().__init__(
            "Nous n'avons pas reçu de réponse! "
            + f"Utilisez `{configs.PREFIX}setup` dans <#{configs.SETUP_CHANNEL}> pour recommencer."
        )

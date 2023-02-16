"""Module containing the Strike enum"""

from enum import Enum

from discord.ext.commands.errors import BadArgument


class Strike(Enum):
    """Enum representing the different types of strikes"""

    def __int__(self):
        match (self):
            case Strike.MUTE:
                return 0
            case Strike.UNMUTE:
                return 1
            case Strike.KICK:
                return 2
            case Strike.BAN:
                return 3
            case Strike.UNBAN:
                return 4
            case _:
                raise BadArgument("Invalid Strike value")

    def __str__(self):
        return self.value

    WARN = "Warn"
    MUTE = "Mute"
    UNMUTE = "Unmute"
    KICK = "Kick"
    BAN = "Ban"
    UNBAN = "Unban"

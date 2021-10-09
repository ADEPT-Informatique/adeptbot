from enum import Enum

from discord.errors import InvalidArgument

class Strike(Enum):
    def __str__(self):
        return self.value
    
    def __int__(self):
        match(self):
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
                raise InvalidArgument("Invalid Strike value")

    WARN = "Warn"
    MUTE = "Mute"
    UNMUTE = "Unmute"
    KICK = "Kick"
    BAN = "Ban"
    UNBAN = "Unban"

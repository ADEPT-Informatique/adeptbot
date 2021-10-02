from enum import Enum

class Strike(Enum):
    # TODO: Make the default Strike.<value> return its value without needing str() around it
    def __str__(self):
        return self.value

    WARN = "warn"
    MUTE = "mute"
    UNMUTE = "unmute"
    KICK = "kick"
    BAN = "ban"
    UNBAN = "unban"
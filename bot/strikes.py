from enum import Enum

class Strike(Enum):
    def __str__(self):
        return self.value
    
    def __int__(self):
        if self == self.MUTE:
            return 0
        elif self == self.UNMUTE:
            return 1
        elif self == self.KICK:
            return 2
        elif self == self.BAN:
            return 3
        elif self == self.UNBAN:
            return 4

    WARN = "Warn"
    MUTE = "Mute"
    UNMUTE = "Unmute"
    KICK = "Kick"
    BAN = "Ban"
    UNBAN = "Unban"
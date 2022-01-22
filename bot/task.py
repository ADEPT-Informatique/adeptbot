import datetime
import disnake
from jsonpickle.pickler import Pickler

from bot.strikes import Strike


class Task(Pickler):
    def __init__(self, member, end_date: datetime.datetime, type:Strike):
        self.member = member
        self.end_date = end_date
        self.type = type

    def __getstate__(self):
        return {'member': self.member.id, 'guild': self.member.guild.id, 'end_date': str(self.end_date), 'type': str(self.type)}

    member: disnake.Member
    end_date: str
    type:Strike

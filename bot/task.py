"""This file contains the Task class, which is used to store tasks in the database."""

import datetime

import discord
from jsonpickle.pickler import Pickler

from bot.strikes import Strike


class Task(Pickler):
    """
    This class represents a task to be executed at a later time.

    Attributes
    ----------
    `member` : discord.Member
        The member the task is related to.
    `end_date` : datetime.datetime
        The date and time the task will be executed.
    `strike_type` : Strike
        The type of strike to be executed.
    """

    def __init__(self, member: discord.Member, end_date: datetime.datetime, strike_type: Strike):
        self.member = member
        self.end_date = end_date
        self.type = strike_type

        super().__init__()

    def __getstate__(self):
        return {'member': self.member.id, 'guild': self.member.guild.id,
                'end_date': str(self.end_date), 'type': str(self.type)}

    member: discord.Member
    end_date: str
    type: Strike

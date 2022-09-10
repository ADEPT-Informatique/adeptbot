import discord
from typing import List


class User:
    def __init__(self, member: discord.Member, last_message: int = 0, strikes: int = 0) -> None:
        self.id = member.id
        self.last_message_timestamp = last_message
        self.strikes = strikes


users: List[User] = []


async def create_user(member: discord.Member, last_message_timestamp: int = 0):
    new_user = User(member, last_message_timestamp)
    users.append(new_user)

    return new_user


async def get_user(member: discord.Member) -> User | None:
    for user in users:
        if user.id == member.id:
            return user

    return None

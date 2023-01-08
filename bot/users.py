"""This file contains the User class and functions to interact with it."""

from typing import List

import discord


class User:
    """This class represents a user."""

    def __init__(self, member: discord.Member, last_message: int = 0, strikes: int = 0) -> None:
        self.discord_id = member.id
        self.last_message_timestamp = last_message
        self.strikes = strikes


users: List[User] = []


async def create_user(member: discord.Member, last_message_timestamp: int = 0):
    """Creates a new user and adds it to the list."""
    new_user = User(member, last_message_timestamp)
    users.append(new_user)

    return new_user


async def get_user(member: discord.Member) -> User | None:
    """Returns the user for the given member."""
    for user in users:
        if user.discord_id == member.id:
            return user

    return None

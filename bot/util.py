import discord
import logging
from typing import Union

import configs
from run import AdeptClient

client: AdeptClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ADEPT-INFO')


def get_member(guild_id: int, member_id: int):
    return client.get_guild(guild_id).get_member(member_id)


def get_guild(guild_id: int):
    return client.get_guild(guild_id)


def get_case_number():
    raise NotImplementedError()


async def strike(id: int, t: str, reason: str):
    raise NotImplementedError()


async def react_to(message: discord.Message, reaction: Union[discord.Emoji, discord.Reaction, discord.PartialEmoji, str]):
    await message.add_reaction(reaction)


async def say(*args, **kwargs):
    await client.say(*args, **kwargs)


async def exception(channel: discord.abc.Messageable, message: discord.Message, **kwargs):
    await say(channel, ":bangbang: **%s**" %message, **kwargs)


async def mute(member: discord.Member):
    guild = member.guild
    mute_role = guild.get_role(configs.MUTED_ROLE)

    await member.add_roles(mute_role)


async def unmute(member: discord.Member, reason: str):
    guild = member.guild
    mute_role = guild.get_role(configs.MUTED_ROLE)

    await member.remove_roles(mute_role, reason=reason)


async def has_role(member: discord.Member, role: discord.Role):
    return role in member.roles


def get_welcome_instruction(instruction: str):
    return configs.WELCOME_MESSAGE.format(content=instruction)


def get_plural(value: int, word: str):
    if word.endswith("s"):
        return word
    
    if value > 1:
        return word + "s"
    
    return word


def _load(c):
    global client
    client = c

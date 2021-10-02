import logging
import discord
from discord.ext import tasks

from . import dbconn, strikes
import configs

client = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ADEPT-INFO')


def get_member(guild, member):
    return client.get_guild(guild).get_member(member)


def get_case_number():
    return dbconn.get("Strikes").find().count() + 1


async def strike(id, t:str, reason):
    dbconn.strike(id, str(t), reason)


async def react_to(message, reaction):
    await message.add_reaction(reaction)


async def say(*args, **kwargs):
    await client.say(*args, **kwargs)


async def exception(channel, message, **kwargs):
    await say(channel, ":bangbang: **%s**" %message, **kwargs)


async def mute(member):
    guild = member.guild
    mute_role = guild.get_role(configs.muted_role)
    
    await member.add_roles(mute_role)


async def unmute(member, reason):
    guild = member.guild
    mute_role = guild.get_role(configs.muted_role)
    
    await member.remove_roles(mute_role, reason=reason)


async def has_role(member, role):
    return role in member.roles


def _load(c):
    global client
    client = c
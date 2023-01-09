"""Utility functions for the bot."""

import asyncio
import logging
from typing import Optional

import discord

import configs
from bot.interactions.ticket import TicketCloseInteraction
from bot.strikes import Strike

CLIENT: discord.Client = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('ADEPT-BOT')


class AdeptBotException(Exception):
    """
    Generic exception for the bot.

    Parameters
    ----------
    `message` : str
        The message to send.
    """

    def __init__(self, message: str) -> None:
        self.message = f":bangbang: **{message}**"


def get_member(guild_id: int, member_id: int):
    """
    Get a member from a guild.

    Parameters
    ----------
    `guild_id` : int
        The id of the guild.
    `member_id` : int
        The id of the member.
    """
    return CLIENT.get_guild(guild_id).get_member(member_id)


def get_guild(guild_id: int):
    """
    Get a guild.

    Parameters
    ----------
    `guild_id` : int
        The id of the guild.
    """
    return CLIENT.get_guild(guild_id)


def get_case_number():
    """Get the next case number."""
    raise NotImplementedError()


async def strike(discord_id: int, strike_type: Strike, reason: str):
    """
    Strike a member.

    Parameters
    ----------
    `discord_id` : int
        The id of the member to strike.
    `strike_type` : Strike
        The type of the strike.
    `reason` : str
        The reason of the strike.
    """
    raise NotImplementedError()


async def wait_for_message(author: discord.User, timeout: int = None) -> Optional[discord.Message]:
    """
    Wait for a message from a user.

    Parameters
    ----------
    `author` : discord.User
        The user to wait for.
    `timeout` : int
        The timeout in seconds.
    """
    def check(message: discord.Message):
        return message.author.id == author.id and isinstance(message.channel, discord.DMChannel)

    try:
        return await CLIENT.wait_for("message", timeout=timeout, check=check)
    except asyncio.exceptions.TimeoutError:
        return None


async def say(*args, **kwargs):
    """Sends a message."""
    await CLIENT.say(*args, **kwargs)


async def exception(channel: discord.abc.Messageable, message: discord.Message, **kwargs):
    """
    Sends an exception message.

    Parameters
    ----------
    `channel` : discord.abc.Messageable
        The channel to send the message to.
    `message` : str
        The message to send.
    `kwargs` : dict
        The kwargs to pass to the send method.
    """
    await channel.send(f":bangbang: **{message}**", **kwargs)


async def mute(member: discord.Member, reason: str):
    """
    Mute a member.

    Parameters
    ----------
    `member` : discord.Member
        The member to mute.
    `reason` : str
        The reason of the mute.
    """
    guild = member.guild
    mute_role = guild.get_role(configs.MUTED_ROLE)

    await member.add_roles(mute_role, reason=reason)


async def unmute(member: discord.Member, reason: str):
    """
    Unmute a member.

    Parameters
    ----------
    `member` : discord.Member
        The member to unmute.
    `reason` : str
        The reason of the unmute.
    """
    guild = member.guild
    mute_role = guild.get_role(configs.MUTED_ROLE)

    await member.remove_roles(mute_role, reason=reason)


async def has_role(member: discord.Member, role: discord.Role):
    """
    Check if a member has a role.

    Parameters
    ----------
    `member` : discord.Member
        The member to check.
    `role` : discord.Role
        The role to check.
    """
    return role in member.roles


async def create_ticket(member: discord.Member, ticket: TicketType):
    """
    Creates a ticket for a member.

    Parameters
    ----------
    `member` : discord.Member
        The member to create the ticket for.
    `ticket` : TicketType
        The type of the ticket.
    """
    guild = member.guild
    category: discord.CategoryChannel = guild.get_channel(configs.TICKET_CATEGORY)
    overwrites = discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True,
                                             read_message_history=True)
    channel = await category.create_text_channel(f"{member.display_name}")
    await channel.set_permissions(member, overwrite=overwrites)

    admin = guild.get_role(configs.ADMIN_ROLE)
    close_button = TicketCloseInteraction()
    await channel.send(configs.TICKET_MESSAGE.format(plaintive=member.mention, admins=admin.mention,
                                                     ticket_type=ticket, prefix=configs.PREFIX),
                       view=close_button)

    return channel


async def archive_ticket(member: discord.Member, channel: discord.TextChannel):
    """
    Sends an active ticket to the tickets archive category and removes the permissions to write in it.

    Parameters
    ----------
    `member` : discord.Member
        The member who closed the ticket.
    `channel` : discord.TextChannel
        The channel to archive.
    """
    guild = channel.guild
    category = guild.get_channel(configs.TICKET_ARCHIVE_CATEGORY)

    overwrites = discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False,
                                             read_message_history=True)

    await channel.set_permissions(member, overwrite=overwrites)
    await channel.send(f'Ticket fermé par {member.mention}.')
    await channel.edit(category=category)


def get_welcome_instruction(instruction: str):
    """
    Get the instruction embed for the welcome setup

    Parameters
    ----------
    `instruction` : str
        The instruction to display.
    """
    welcome_embed = discord.Embed(title=configs.WELCOME_TITLE,
                                  description=configs.WELCOME_MESSAGE.format(content=instruction),
                                  color=0x1de203)
    welcome_embed.set_thumbnail(url="https://www.adeptinfo.ca/img/badge.png")
    welcome_embed.set_footer(text=configs.WELCOME_FOOTER)

    return welcome_embed


def get_plural(value: int, word: str):
    """
    Get the plural of a word.

    Parameters
    ----------
    `value` : int
        The amount of the word.
    `word` : str
        The word to pluralize.
    """
    if word.endswith("s"):
        return word

    if value > 1:
        return word + "s"

    return word


# Simple time formatter based on "Mr. B" - https://stackoverflow.com/a/24542445
INTERVALS = (
    ('semaines', 604800),  # 60 * 60 * 24 * 7
    ('jours', 86400),  # 60 * 60 * 24
    ('heures', 3600),  # 60 * 60
    ('minutes', 60),
    ('secondes', 1),
)


def display_time(seconds: int, granularity: int = 2):
    """
    Display time in a human readable format.

    Parameters
    ----------
    `seconds` : int
        The amount of seconds to display.
    `granularity` : int
        The amount of time units to display. Default to 2.
    """
    result = []

    for name, count in INTERVALS:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append(f"{int(value)} {name}")
    return ', '.join(result[:granularity])


def load(loaded_client):
    """
    Inject the client in the module.

    This is a hack that allows us to use the client
    in modules that does not have access to it.

    NOTE: This is a hack and should NEVER be replicated :kekw:
    """
    global CLIENT
    CLIENT = loaded_client

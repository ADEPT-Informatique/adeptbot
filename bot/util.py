"""Utility functions for the bot."""

import logging

import discord

import configs
from bot.interactions.ticket import TicketCloseInteraction
from bot.tickets import TicketType

from bot.strikes import Strike

client: discord.Client = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('ADEPT-BOT')


class AdeptBotException(Exception):
    """Generic exception for the bot."""

    def __init__(self, message) -> None:
        self.message = f":bangbang: **{message}**"


def get_member(guild_id: int, member_id: int):
    """Get a member from a guild."""
    return client.get_guild(guild_id).get_member(member_id)


def get_guild(guild_id: int):
    """Get a guild."""
    return client.get_guild(guild_id)


def get_case_number():
    """Get the next case number."""
    raise NotImplementedError()


async def strike(discord_id: int, strike_type: Strike, reason: str):
    """Strike a member."""
    raise NotImplementedError()


async def react_to(message: discord.Message, reaction: discord.Emoji | discord.Reaction | discord.PartialEmoji | str):
    """React to a message."""
    await message.add_reaction(reaction)


async def say(*args, **kwargs):
    """Sends a message."""
    await client.say(*args, **kwargs)


async def exception(channel: discord.abc.Messageable, message: discord.Message, **kwargs):
    """Sends an exception message."""
    await channel.send(f":bangbang: **{message}**", **kwargs)


async def mute(member: discord.Member, reason: str):
    """Mute a member."""
    guild = member.guild
    mute_role = guild.get_role(configs.MUTED_ROLE)

    await member.add_roles(mute_role, reason=reason)


async def unmute(member: discord.Member, reason: str):
    """Unmute a member."""
    guild = member.guild
    mute_role = guild.get_role(configs.MUTED_ROLE)

    await member.remove_roles(mute_role, reason=reason)


async def has_role(member: discord.Member, role: discord.Role):
    """Check if a member has a role."""
    return role in member.roles


async def create_ticket(member: discord.Member, ticket: TicketType):
    """Creates a ticket for a member."""
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
    """Sends an active ticket to the tickets archive category and removes the permissions to write in it."""
    guild = channel.guild
    category = guild.get_channel(configs.TICKET_ARCHIVE_CATEGORY)

    overwrites = discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False,
                                             read_message_history=True)

    await channel.set_permissions(member, overwrite=overwrites)
    await channel.send(f'Ticket fermé par {member.mention}.')
    await channel.edit(category=category)


def get_welcome_instruction(instruction: str):
    """Get the welcome embed."""
    welcome_embed = discord.Embed(title=configs.WELCOME_TITLE,
                                  description=configs.WELCOME_MESSAGE.format(content=instruction),
                                  color=0x1de203)
    welcome_embed.set_thumbnail(url="https://www.adeptinfo.ca/img/badge.png")
    welcome_embed.set_footer(text=configs.WELCOME_FOOTER)

    return welcome_embed


def get_plural(value: int, word: str):
    """Get the plural of a word."""
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


def display_time(seconds, granularity=2):
    """Display time in a human readable format."""
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
    global client
    client = loaded_client

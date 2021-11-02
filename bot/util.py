import discord
import logging

import configs
from bot.interactions.ticket import TicketCloseInteraction
from bot.tickets import TicketType

client = None

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


async def react_to(message: discord.Message, reaction: discord.Emoji | discord.Reaction | discord.PartialEmoji | str):
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


async def create_ticket(member: discord.Member, ticket: TicketType):
    guild = member.guild
    category: discord.CategoryChannel = guild.get_channel(configs.TICKET_CATEGORY)
    overwrites = discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, read_message_history=True)
    channel = await category.create_text_channel(f"{member.display_name}")
    await channel.set_permissions(member, overwrite=overwrites)

    admin = guild.get_role(configs.ADMIN_ROLE)
    close_button = TicketCloseInteraction()
    await channel.send(configs.TICKET_MESSAGE.format(plaintive=member.mention, admins=admin.mention, 
                                                    ticket_type=ticket, prefix=configs.PREFIX), 
                                                    view=close_button)

    return channel


async def archive_ticket(member: discord.Member, channel: discord.TextChannel):
    guild = channel.guild
    category = guild.get_channel(configs.TICKET_ARCHIVE_CATEGORY)

    overwrites = discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False, read_message_history=True)

    await channel.set_permissions(member, overwrite=overwrites)
    await channel.send(f'Ticket fermé par {member.mention}.')
    await channel.edit(category=category)


def get_welcome_instruction(instruction: str):
    welcome_embed = discord.Embed(title = configs.WELCOME_TITLE,
                                description=configs.WELCOME_MESSAGE.format(content=instruction),
                                color=0x1de203)
    welcome_embed.set_thumbnail(url="https://www.adeptinfo.ca/img/badge.png")
    welcome_embed.set_footer(text=configs.WELCOME_FOOTER)

    return welcome_embed


def get_plural(value: int, word: str):
    if word.endswith("s"):
        return word
    
    if value > 1:
        return word + "s"
    
    return word


def _load(c):
    global client
    client = c

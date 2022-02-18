import disnake
import logging

import configs
from bot.interactions.ticket import TicketCloseInteraction
from bot.tickets import TicketType

client = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ADEPT-INFO')


class AdeptBotError(Exception):
    def __init__(self, channel: disnake.abc.Messageable, message) -> None:
        self.channel = channel
        self.message = message


def get_member(guild_id: int, member_id: int):
    return client.get_guild(guild_id).get_member(member_id)


def get_guild(guild_id: int):
    return client.get_guild(guild_id)


def get_case_number():
    raise NotImplementedError()


async def strike(id: int, t: str, reason: str):
    raise NotImplementedError()


async def react_to(message: disnake.Message, reaction: disnake.Emoji | disnake.Reaction | disnake.PartialEmoji | str):
    await message.add_reaction(reaction)


async def say(*args, **kwargs):
    await client.say(*args, **kwargs)


async def exception(channel: disnake.abc.Messageable, message: disnake.Message, **kwargs):
    await say(channel, f":bangbang: **{message}**", **kwargs)


async def mute(member: disnake.Member):
    guild = member.guild
    mute_role = guild.get_role(configs.MUTED_ROLE)

    await member.add_roles(mute_role)


async def unmute(member: disnake.Member, reason: str):
    guild = member.guild
    mute_role = guild.get_role(configs.MUTED_ROLE)

    await member.remove_roles(mute_role, reason=reason)


async def has_role(member: disnake.Member, role: disnake.Role):
    return role in member.roles


async def create_ticket(member: disnake.Member, ticket: TicketType):
    guild = member.guild
    category: disnake.CategoryChannel = guild.get_channel(configs.TICKET_CATEGORY)
    overwrites = disnake.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True,
                                             read_message_history=True)
    channel = await category.create_text_channel(f"{member.display_name}")
    await channel.set_permissions(member, overwrite=overwrites)

    admin = guild.get_role(configs.ADMIN_ROLE)
    close_button = TicketCloseInteraction()
    await channel.send(configs.TICKET_MESSAGE.format(plaintive=member.mention, admins=admin.mention,
                                                     ticket_type=ticket, prefix=configs.PREFIX),
                       view=close_button)

    return channel


async def archive_ticket(member: disnake.Member, channel: disnake.TextChannel):
    guild = channel.guild
    category = guild.get_channel(configs.TICKET_ARCHIVE_CATEGORY)

    overwrites = disnake.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False,
                                             read_message_history=True)

    await channel.set_permissions(member, overwrite=overwrites)
    await channel.send(f'Ticket fermé par {member.mention}.')
    await channel.edit(category=category)


def get_welcome_instruction(instruction: str):
    welcome_embed = disnake.Embed(title=configs.WELCOME_TITLE,
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

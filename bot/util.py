import discord
import logging

import configs
from bot.http.models.user import WelcomeUser

client = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ADEPT-INFO')


def get_member(guild, member):
    return client.get_guild(guild).get_member(member)


def get_case_number():
    raise NotImplementedError()


async def strike(id, t: str, reason: str):
    raise NotImplementedError()


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


def get_welcome_instruction(instruction: str):
    return configs.WELCOME_MESSAGE.format(content=instruction)


async def process_welcome_result(member: discord.Member, result):
    if isinstance(result, WelcomeUser):
        guild = member.guild
        name = result.name
        student_id = result.student_id

        role = None
        if result.is_student:
            if result.program == "Programmation":
                role = guild.get_role(configs.PROG_ROLE)
            elif result.program == "Réseautique":
                role = guild.get_role(configs.NETWORK_ROLE)
            elif result.program == "DEC-BAC":
                role = guild.get_role(configs.DECBAC_ROLE)
        else:
            role = guild.get_role(configs.TEACHER_ROLE)

        await member.edit(nick=name, roles=[role], reason="Inital setup")

        # TODO: Post to API the new partial student setup
    else:
        logger.warning(f"Failed to complete setup for {member.name} ({member.id})")


def _load(c):
    global client
    client = c
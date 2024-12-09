"""This module contains the moderation commands."""

import re
import typing

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import configs
from bot import permissions, tasks, util
from bot.botcommands.utils.validators import has_at_least_role
from bot.strikes import Strike
from bot.util import AdeptBotException

NO_REASON = "Pas de raison spécifié"


class ParsedTime:
    """
    This class represents a parsed time.

    Attributes
    ----------
    `label` : str
        The label of the time.
    `seconds` : int
        The total time in seconds.
    """

    def __init__(self, label: str, seconds: int) -> None:
        self.label = label
        self.seconds = seconds


def __parse_values(value: str):
    pattern = r"(\d+)([A-Za-z]+)"
    matches = re.match(pattern, value)

    return matches.groups(None)


def __parse_secs(value: int):
    label = f"{value} {util.get_plural(value, 'seconde')}"

    return ParsedTime(label, value)


def __parse_mins(value: int):
    label = f"{value} {util.get_plural(value, 'minute')}"
    total_time = value * 60

    return ParsedTime(label, total_time)


def __parse_hours(value: int):
    label = f"{value} {util.get_plural(value, 'heure')}"
    total_time = value * 60 * 60

    return ParsedTime(label, total_time)


def __parse_days(value: int):
    label = f"{value} {util.get_plural(value, 'jour')}"
    total_time = value * 60 * 60 * 24

    return ParsedTime(label, total_time)


def __parse_week(value: int):
    label = f"{value} {util.get_plural(value, 'semaine')}"
    total_time = value * 60 * 60 * 24 * 7

    return ParsedTime(label, total_time)


class CustomTime(commands.Converter):
    """This class represents a custom time converter."""

    async def convert(self, _, value: str) -> ParsedTime:
        matches = __parse_values(value)

        if matches is None:
            raise commands.BadArgument(f"{value} n'est pas une unité de temps valide.")

        int_value = matches[0]
        time_parse = matches[1]

        parsed_time = {
            "s": __parse_secs(int_value),
            "m": __parse_mins(int_value),
            "h": __parse_hours(int_value),
            "d": __parse_days(int_value),
            "w": __parse_week(int_value),
        }.get(time_parse, None)

        return parsed_time


class ModerationEmbedRequest:
    """
    This class is used to create a moderation embed.

    Attributes
    ----------
    `strike` : Strike
        The strike type.
    `target` : discord.User | discord.Member
        The target of the strike.
    `author` : discord.Member
        The author of the strike.
    `reason` : str
        The reason of the strike.
    `parsed_time` : ParsedTime
        The time information of the strike.
    """

    def __init__(
        self,
        strike: Strike,
        target: discord.User | discord.Member,
        author: discord.Member,
        reason: str,
        parsed_time: ParsedTime = None,
    ):
        self.strike = strike
        self.target = target
        self.author = author
        self.reason = reason
        self.parsed_time = parsed_time

    @property
    def moderation_embed(self) -> discord.Embed:
        """Creates an embed with the moderation information."""
        color = None
        if self.strike in (Strike.WARN, Strike.MUTE, Strike.UNMUTE):
            color = 15066368
        elif self.strike == Strike.KICK:
            color = 16758079
        elif self.strike in (Strike.BAN, Strike.UNBAN):
            color = 993326

        moderation_embed = discord.Embed(title=f"Nouveau cas | {self.strike} | {self.target.name}", color=color)
        moderation_embed.add_field(name="Utilisateur", value=self.target.mention, inline=False)
        moderation_embed.add_field(name="Moderateur", value=self.author.mention, inline=False)
        moderation_embed.add_field(name="Raison", value=self.reason, inline=False)

        if self.parsed_time:
            moderation_embed.add_field(name="Durée", value=self.parsed_time.seconds)

        return moderation_embed


class ModerationCog(commands.Cog):
    """This class represents the moderation cog."""

    @commands.command()
    @has_at_least_role(configs.TRUST_ROLE)
    async def warn(self, ctx: Context, member: discord.Member, *, reason: str = NO_REASON):
        """
        Avertit un utilisateur.

        Utilisation:
        !warn @DeveloperAnonymous Is a noob
        """
        try:
            await member.send(f"Vous avez été averti(e) {ctx.guild.name}.\n\nRaison: {reason}")
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warning("Failed to notify warn")

        warn_embed = ModerationEmbedRequest(Strike.WARN, member, ctx.author, reason).moderation_embed
        await util.say(configs.LOGS_CHANNEL, embed=warn_embed)
        await ctx.message.add_reaction("\u2705")

        # TODO: Do DB Calls in the background

    @commands.command()
    @has_at_least_role(configs.TRUST_ROLE)
    async def mute(
        self,
        ctx: Context,
        member: discord.Member,
        length: typing.Optional[CustomTime] = None,
        *,
        reason: str = NO_REASON,
    ):
        """
        Rend muet un utilisateur.

        Utilisation:
        !mute @DeveloperAnonymous Is a noob
        !mute @DeveloperAnonymous 15 Is a noob
        !mute @DeveloperAnonymous 15s Is a noob
        !mute @DeveloperAnonymous 15m Is a noob
        !mute @DeveloperAnonymous 15h Is a noob
        !mute @DeveloperAnonymous 15d Is a noob
        !mute @DeveloperAnonymous 15w Is a noob

        NOTE:
        s = second(s)
        m = minute(s)
        h = hour(s)
        d = day(s)
        w = week(s)
        """
        target_perm = permissions.determine_permission(member)
        if not permissions.has_permission(ctx.author, target_perm):
            raise permissions.InsufficientPermissionsError(
                ctx.channel,
                f"Vous ne pouvez pas rendre muet {member.mention} puisqu'il dispose de permissions plus élevées!",
            )

        if await util.has_role(member, ctx.guild.get_role(configs.MUTED_ROLE)):
            raise AdeptBotException("Ce membre est déjà muet!")

        try:
            await member.send(f"Vous êtes désormais muet sur {ctx.guild.name}.\n\nRaison: {reason}")
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warning("Failed to notify mute")

        mute_embed = await ModerationEmbedRequest(Strike.MUTE, member, ctx.author, reason, length).moderation_embed
        await util.mute(member, reason)
        await util.say(configs.LOGS_CHANNEL, embed=mute_embed)
        await ctx.message.add_reaction("\u2705")

        if length is not None:
            await tasks.create_mute_task(member, length.seconds)

        # TODO: Create the task
        # TODO: Do DB Calls in the background

    @commands.command()
    @has_at_least_role(configs.TRUST_ROLE)
    async def unmute(self, ctx: Context, member: discord.Member, *, reason: str = NO_REASON):
        """
        Enlève le statut de muet d'un utilisateur.

        Utilisation:
        !unmute @DeveloperAnonymous
        !unmute @DeveloperAnonymous Is not a noob anymore
        """
        if not await util.has_role(member, ctx.guild.get_role(configs.MUTED_ROLE)):
            raise AdeptBotException("Ce membre n'est pas muet!")

        mute_embed = await ModerationEmbedRequest(Strike.UNMUTE, member, ctx.author, reason).moderation_embed
        await util.unmute(member, reason)
        await util.say(configs.LOGS_CHANNEL, embed=mute_embed)
        await ctx.message.add_reaction("\u2705")

        # TODO: Remove the task, if any
        # TODO: Do DB Calls in the background

    @commands.command()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def kick(self, ctx: Context, member: discord.Member, *, reason: str = NO_REASON):
        """
        Expulse un utilisateur du serveur.

        Utilisation:
        !kick @DeveloperAnonymous
        !kick @DeveloperAnonymous Is a noob
        """
        target_perm = permissions.determine_permission(member)
        if not permissions.has_permission(ctx.author, target_perm):
            raise permissions.InsufficientPermissionsError(
                ctx.channel,
                f"Vous ne pouvez pas retiré {member.mention} du serveur puisqu'il dispose de permissions plus élevées!",
            )

        try:
            await member.send(f"Vous avez été retiré de {ctx.guild.name}.\n\nRaison: {reason}")
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warning("Failed to notify kick")

        kick_embed = await ModerationEmbedRequest(Strike.KICK, member, ctx.author, reason).moderation_embed
        await member.kick(reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=kick_embed)
        await ctx.message.add_reaction("\u2705")

        # TODO: Do DB Calls in the background

    @commands.command()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def ban(self, ctx: Context, user: discord.User, *, reason: str = NO_REASON):
        """
        Banni un utilisateur du serveur.

        Utilisation:
        !ban @DeveloperAnonymous
        !ban @DeveloperAnonymous Is a noob
        """
        guild: discord.Guild = ctx.guild
        member = guild.get_member(user.id)
        if member is None:
            raise AdeptBotException("Ce membre n'existe pas!")

        target_perm = permissions.determine_permission(member)
        if not permissions.has_permission(ctx.author, target_perm):
            raise permissions.InsufficientPermissionsError(
                ctx.channel,
                f"Vous ne pouvez pas bannir {member.mention} puisqu'il dispose de permissions plus élevées!",
            )

        if user in [entry.user for entry in await guild.bans()]:
            raise AdeptBotException("Ce membre est déjà banni!")

        try:
            await user.send(f"Vous avez été banni de {ctx.guild.name}.\n\nRaison: {reason}")
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warning("Failed to notify ban")

        ban_embed = await ModerationEmbedRequest(Strike.BAN, user, ctx.author, reason).moderation_embed
        await guild.ban(user, reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=ban_embed)
        await ctx.message.add_reaction("\u2705")

        # TODO: Create the task
        # TODO: Do DB Calls in the background

    @commands.command()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def unban(self, ctx: Context, user: discord.User, *, reason: str = NO_REASON):
        """
        Enlève le statut de banni d'un utilisateur.

        Utilisation:
        !unban @DeveloperAnonymous
        !unban @DeveloperAnonymous Is not a noob anymore
        """
        guild: discord.Guild = ctx.guild

        if user not in [entry.user for entry in await guild.bans()]:
            raise AdeptBotException("Ce membre n'est pas banni!")

        unban_embed = await ModerationEmbedRequest(Strike.UNBAN, user, ctx.author, reason).moderation_embed
        await guild.unban(user, reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=unban_embed)
        await ctx.message.add_reaction("\u2705")

        # TODO: Remove the task, if any
        # TODO: Do DB Calls in the background

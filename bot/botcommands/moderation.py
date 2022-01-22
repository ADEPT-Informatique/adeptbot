import disnake
import re
import traceback
import typing
from disnake.ext import commands
from disnake.ext.commands.context import Context
from disnake.ext.commands.errors import CommandInvokeError
from bot.management import StrikesCog

import configs
from .. import tasks, util, permissions
from ..http.services import BanService, MuteService
from ..strikes import Strike

NO_REASON = "Pas de raison spécifié"


class ParsedTime:
    def __init__(self, label, seconds) -> None:
        self.label = label
        self.seconds = seconds


def parse_values(value: str):
    pattern = r"(\d+)([A-Za-z]+)"
    matches = re.match(pattern, value)

    return matches.groups(None)


def parse_secs(value: int):
    label = f"{value} {util.get_plural(value, 'seconde')}"
    
    return ParsedTime(label, value)


def parse_mins(value: int):
    label = f"{value} {util.get_plural(value, 'minute')}"
    total_time = value * 60

    return ParsedTime(label, total_time)


def parse_hours(value: int):
    label = f"{value} {util.get_plural(value, 'heure')}"
    total_time = value * 60 * 60

    return ParsedTime(label, total_time)


def parse_days(value: int):
    label = f"{value} {util.get_plural(value, 'jour')}"
    total_time = value * 60 * 60 * 24

    return ParsedTime(label, total_time)


def parse_week(value: int):
    label = f"{value} {util.get_plural(value, 'semaine')}"
    total_time = value * 60 * 60 * 24 * 7

    return ParsedTime(label, total_time)


class CustomTime(commands.Converter):
    async def convert(self, _, value: str) -> ParsedTime:
        matches = parse_values(value)

        if matches is None:
            raise commands.BadArgument(f"{value} n'est pas une unité de temps valide.")

        int_value = matches[0]
        time_parse = matches[1]

        parsed_time = {
            's': parse_secs(int_value),
            'm': parse_mins(int_value),
            'h': parse_hours(int_value),
            'd': parse_days(int_value),
            'w': parse_week(int_value)
        }.get(time_parse, None)
        
        return parsed_time


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.mute_service = MuteService(bot.loop)
        self.ban_service = BanService(bot.loop)

        bot.add_cog(StrikesCog(bot))

    async def __create_moderation_embed(self, strike: Strike, target: disnake.User| disnake.Member, author: disnake.Member, reason: str, parsed_time: ParsedTime = None):
        color = None
        if strike in (Strike.WARN, Strike.MUTE, Strike.UNMUTE):
            color = 15066368
        elif strike == Strike.KICK:
            color = 16758079
        elif strike in (Strike.BAN, Strike.UNBAN):
            color = 993326

        moderation_embed = disnake.Embed(title=f"Nouveau cas | {strike} | {target.name}", color=color)
        moderation_embed.add_field(name="Utilisateur", value=target.mention, inline=False)
        moderation_embed.add_field(name="Moderateur", value=author.mention, inline=False)
        moderation_embed.add_field(name="Raison", value=reason, inline=False)

        if parsed_time:
            moderation_embed.add_field(name="Durée", value=parsed_time.seconds)

        return moderation_embed

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE, configs.TRUST_ROLE)
    async def warn(self, ctx: Context, member: disnake.Member, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !warn @DeveloperAnonymous Is a noob
        """
        try:
            await member.send("Vous avez été averti(e) %s.\n\nRaison: %s" % (ctx.guild.name, reason))
        except(disnake.errors.HTTPException, disnake.errors.Forbidden):
            util.logger.warn("Failed to notify warn")

        warn_embed = self.__create_moderation_embed(Strike.WARN, member, ctx.author, reason)
        await util.say(configs.LOGS_CHANNEL, embed=warn_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Do API Calls in the background

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE, configs.TRUST_ROLE)
    async def mute(self, ctx: Context, member: disnake.Member, length: typing.Optional[CustomTime] = None, *, reason: str = NO_REASON):
        """
        USAGE EXAMPLES:
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
            raise permissions.InsufficientPermissionsError(ctx.channel, f"Vous ne pouvez pas rendre muet {member.mention} puisqu'il dispose de permissions plus élevées!")
        
        if await util.has_role(member, ctx.guild.get_role(configs.MUTED_ROLE)):
            return await util.exception(ctx.channel, "Ce membre est déjà muet!")

        try:
            await member.send("Vous êtes désormais muet sur %s.\n\nRaison: %s" % (ctx.guild.name, reason))
        except (disnake.errors.HTTPException, disnake.errors.Forbidden):
            util.logger.warn("Failed to notify mute")

        mute_embed = await self.__create_moderation_embed(Strike.MUTE, member, ctx.author, reason, length)
        await util.mute(member)
        await util.say(configs.LOGS_CHANNEL, embed=mute_embed)
        await util.react_to(ctx.message, u"\u2705")

        if length is not None:
            await tasks.create_mute_task(member, length.seconds)

        # TODO: Create the task
        # TODO: Do API Calls in the background

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE, configs.TRUST_ROLE)
    async def unmute(self, ctx: Context, member: disnake.Member, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !unmute @DeveloperAnonymous
        !unmute @DeveloperAnonymous Is not a noob anymore
        """
        if not await util.has_role(member, ctx.guild.get_role(configs.MUTED_ROLE)):
            return await util.exception(ctx.channel, "Ce membre n'est pas muet!")

        mute_embed = await self.__create_moderation_embed(Strike.UNMUTE, member, ctx.author, reason)
        await util.unmute(member)
        await util.say(configs.LOGS_CHANNEL, embed=mute_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Remove the task, if any
        # TODO: Do API Calls in the background

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE)
    async def kick(self, ctx: Context, member: disnake.Member, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !kick @DeveloperAnonymous
        !kick @DeveloperAnonymous Is a noob
        """
        target_perm = permissions.determine_permission(member)
        if not permissions.has_permission(ctx.author, target_perm):
            raise permissions.InsufficientPermissionsError(ctx.channel, f"Vous ne pouvez pas retiré {member.mention} du serveur puisqu'il dispose de permissions plus élevées!")
        
        try:
            await member.send("Vous avez été retiré de %s.\n\nRaison: %s" % (ctx.guild.name, reason))
        except (disnake.errors.HTTPException, disnake.errors.Forbidden):
            util.logger.warn("Failed to notify kick")

        kick_embed = await self.__create_moderation_embed(Strike.KICK, member, ctx.author, reason)
        await member.kick(reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=kick_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Do API Calls in the background

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE)
    async def ban(self, ctx: Context, user: disnake.User, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !ban @DeveloperAnonymous
        !ban @DeveloperAnonymous Is a noob
        """
        guild: disnake.Guild = ctx.guild
        member = guild.get_member(user.id)
        if member is None:
            return await util.exception(ctx.channel, "Ce membre n'existe pas!")

        target_perm = permissions.determine_permission(member)
        if not permissions.has_permission(ctx.author, target_perm):
            raise permissions.InsufficientPermissionsError(ctx.channel, f"Vous ne pouvez pas bannir {member.mention} puisqu'il dispose de permissions plus élevées!")
        
        if user in [entry.user for entry in await guild.bans()]:
            return await util.exception(ctx.channel, "Ce membre est déjà banni!")

        try:
            await user.send("Vous avez été banni dans %s.\n\nRaison: %s" % (guild.name, reason))
        except (disnake.errors.HTTPException, disnake.errors.Forbidden):
            util.logger.warn("Failed to notify ban")

        ban_embed = await self.__create_moderation_embed(Strike.BAN, user, ctx.author, reason)
        await guild.ban(user, reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=ban_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Create the task
        # TODO: Do API Calls in the background

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE)
    async def unban(self, ctx: Context, user: disnake.User, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !unban @DeveloperAnonymous
        !unban @DeveloperAnonymous Is not a noob anymore
        """
        guild: disnake.Guild = ctx.guild

        if user not in [entry.user for entry in await guild.bans()]:
            return await util.exception(ctx.channel, "Ce membre n'est pas banni!")

        unban_embed = await self.__create_moderation_embed(Strike.UNBAN, user, ctx.author, reason)
        await guild.unban(user, reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=unban_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Remove the task, if any
        # TODO: Do API Calls in the background

    async def cog_command_error(self, ctx: Context, error):
        if isinstance(error, CommandInvokeError):
            error = error.original
        
        if isinstance(error, permissions.InsufficientPermissionsError):
            await util.exception(error.channel, error.message)
            return # We don't want to print the traceback
        
        if ctx is not None:
            await util.exception(ctx.channel, error)
            return

        traceback.print_exc()

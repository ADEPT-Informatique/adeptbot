import discord
import typing
from discord.ext import commands
from discord.ext.commands.context import Context

import configs
from .. import tasks, util
from ..http.services import BanService, MuteService
from ..strikes import Strike

NO_REASON = "Pas de raison spécifié"

class ParsedTime:
    def __init__(self, label, seconds) -> None:
        self.label = label
        self.seconds = seconds


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
    async def convert(self, _, value) -> ParsedTime:
        time_parse = value[-1].lower()
        
        try:
            int_value = int(value)
        except ValueError:
            int_value = int(value[:-1])

        return {
            's': parse_secs(int_value),
            'm': parse_mins(int_value),
            'h': parse_hours(int_value),
            'd': parse_days(int_value),
            'w': parse_week(int_value)
        }.get(time_parse, parse_secs(int_value))


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.mute_service = MuteService(bot.loop)
        self.ban_service = BanService(bot.loop)

    async def __create_moderation_embed(self, strike: Strike, target: discord.User| discord.Member, author: discord.Member, reason: str, parsed_time: ParsedTime = None):
        color = None
        if strike in (Strike.WARN, Strike.MUTE, Strike.UNMUTE):
            color = 15066368
        elif strike == Strike.KICK:
            color = 16758079
        elif strike in (Strike.BAN, Strike.UNBAN):
            color = 993326

        moderation_embed = discord.Embed(title=f"Nouveau cas | {strike} | {target.name}", color=color)
        moderation_embed.add_field(name="Utilisateur", value=target.mention, inline=False)
        moderation_embed.add_field(name="Moderateur", value=author.mention, inline=False)
        moderation_embed.add_field(name="Raison", value=reason, inline=False)

        if parsed_time:
            moderation_embed.add_field(name="Durée", value=parsed_time.seconds)

        return moderation_embed

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE, configs.TRUST_ROLE)
    async def warn(self, ctx: Context, member: discord.Member, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !warn @DeveloperAnonymous Is a noob
        """

        try:
            await member.send("Vous avez été averti(e) %s.\n\nRaison: %s" % (ctx.guild.name, reason))
        except(discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warn("Failed to notify warn")

        warn_embed = self.__create_moderation_embed(Strike.WARN, member, ctx.author, reason)
        await util.say(configs.LOGS_CHANNEL, embed=warn_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Do API Calls in the background

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE, configs.TRUST_ROLE)
    async def mute(self, ctx: Context, member: discord.Member, length: typing.Optional[CustomTime] = None, *, reason: str = NO_REASON):
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
        if await util.has_role(member, ctx.guild.get_role(configs.MUTED_ROLE)):
            return await util.exception(ctx.channel, "Ce membre est déjà muet!")

        try:
            await member.send("Vous êtes désormais muet sur %s.\n\nRaison: %s" % (ctx.guild.name, reason))
        except (discord.errors.HTTPException, discord.errors.Forbidden):
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
    async def unmute(self, ctx: Context, member: discord.Member, *, reason: str=NO_REASON):
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
    async def kick(self, ctx: Context, member: discord.Member, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !kick @DeveloperAnonymous
        !kick @DeveloperAnonymous Is a noob
        """
        
        try:
            await member.send("Vous avez été retiré de %s.\n\nRaison: %s" % (ctx.guild.name, reason))
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warn("Failed to notify kick")

        kick_embed = await self.__create_moderation_embed(Strike.KICK, member, ctx.author, reason)
        await member.kick(reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=kick_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Do API Calls in the background

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE)
    async def ban(self, ctx: Context, user: discord.User, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !ban @DeveloperAnonymous
        !ban @DeveloperAnonymous Is a noob
        """

        guild: discord.Guild = ctx.guild
        if user in [entry.user for entry in await guild.bans()]:
            return await util.exception(ctx.channel, "Ce membre est déjà banni!")


        try:
            await user.send("Vous avez été banni dans %s.\n\nRaison: %s" % (guild.name, reason))
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warn("Failed to notify ban")

        ban_embed = await self.__create_moderation_embed(Strike.BAN, user, ctx.author, reason)
        await guild.ban(user, reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=ban_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Create the task
        # TODO: Do API Calls in the background

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE)
    async def unban(self, ctx: Context, user: discord.User, *, reason: str=NO_REASON):
        """
        USAGE EXAMPLES:
        !unban @DeveloperAnonymous
        !unban @DeveloperAnonymous Is not a noob anymore
        """
        guild:discord.Guild = ctx.guild

        if user not in [entry.user for entry in await guild.bans()]:
            return await util.exception(ctx.channel, "Ce membre n'est pas banni!")

        unban_embed = await self.__create_moderation_embed(Strike.UNBAN, user, ctx.author, reason)
        await guild.unban(user, reason=reason)
        await util.say(configs.LOGS_CHANNEL, embed=unban_embed)
        await util.react_to(ctx.message, u"\u2705")

        # TODO: Remove the task, if any
        # TODO: Do API Calls in the background

    async def cog_command_error(self, ctx: Context, error):
        await util.say(ctx.channel, error)

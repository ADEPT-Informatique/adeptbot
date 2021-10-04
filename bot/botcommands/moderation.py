import discord
from discord.ext import commands
import typing

from discord.ext.commands import cog
from discord.ext.commands.context import Context
from ..http.services import MuteService, BanService

import configs

from .. import util, tasks
from ..strikes import Strike

NO_REASON = "No reason specified"


def parse_secs(value:int):
    return (value, "seconds" if value > 1 else "second", value)


def parse_mins(value:int):
    total_time = value * 60
    return (value, "minutes" if value > 1 else "minute", total_time)


def parse_hours(value:int):
    total_time = value * 60 * 60
    return (value, "hours" if value > 1 else "hour", total_time)


def parse_days(value:int):
    total_time = value * 60 * 60 * 24
    return (value, "days" if value > 1 else "day", total_time)


def parse_week(value:int):
    total_time = value * 60 * 60 * 24 * 7
    return (value, "weeks" if value > 1 else "week", total_time)


class CustomTime(commands.Converter):
    async def convert(self, _, value):
        time_parse = value[-1].lower()
        try:
            int_value = int(value)
        except TypeError:
            int_value = int(value[:-1])
        return {
            's': parse_secs(int_value),
            'm': parse_mins(int_value),
            'h': parse_hours(int_value),
            'd': parse_days(int_value),
            'w': parse_week(int_value)
        }.get(time_parse, parse_secs(int_value))


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.mute_service = MuteService(bot.loop)
        self.ban_service = BanService(bot.loop)
    
    async def cog_check(self, ctx: Context) -> bool:
        return any([role in (configs.ADMIN_ROLE, configs.TRUST_ROLE) for role in ctx.author.roles])

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE, configs.TRUST_ROLE)
    async def warn(self, ctx: Context, member: discord.Member, *, reason:str=NO_REASON):
        """
        USAGE EXAMPLES:
        !warn @DeveloperAnonymous Is a noob
        """

        warn_embed = discord.Embed(title=f"New case | Warning | {member}", color=15066368)
        warn_embed.add_field(name="User", value=member.mention)
        warn_embed.add_field(name="Moderator", value=ctx.author.mention)
        warn_embed.add_field(name="Reason", value=reason, inline=False)

        try:
            await member.send("You have been warned in %s: %s" % (ctx.guild.name, reason))
        except(discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warn("Failed to notify warn")

        await util.strike(member.id, str(Strike.WARN), reason)
        await util.say(configs.LOGS, embed=warn_embed)
        await util.react_to(ctx.message, u"\u2705")
    
    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE, configs.TRUST_ROLE)
    async def mute(self, ctx: Context, member: discord.Member, length:typing.Optional[CustomTime]=-1, *, reason:str=NO_REASON):
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
            return await util.exception(ctx.channel, "This user is already muted!")

        mute_embed = discord.Embed(title=f"New case | Mute | {member}", color=15066368)
        mute_embed.add_field(name="User", value=member.mention)
        mute_embed.add_field(name="Moderator", value=ctx.author.mention)
        if type(length) == tuple:
            mute_embed.add_field(name="Length", value=f"{length[0]} {length[1]}")
        mute_embed.add_field(name="Reason", value=reason, inline=False)

        try:
            await member.send("You have been muted in %s: %s" % (ctx.guild.name, reason))
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warn("Failed to notify mute")

        seconds = length[2] if type(length) == tuple else None
        await tasks.create_mute_task(member, seconds)
        await util.strike(member.id, Strike.MUTE, reason)
        await self.mute_service.mute(member, reason, seconds)
        await util.say(configs.LOGS, embed=mute_embed)
        await util.react_to(ctx.message, u"\u2705")

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def unmute(self, ctx: Context, member: discord.Member, *, reason:str=NO_REASON):
        """
        USAGE EXAMPLES:
        !unmute @DeveloperAnonymous
        !unmute @DeveloperAnonymous Is not a noob anymore
        """
        if not await util.has_role(member, ctx.guild.get_role(configs.MUTED_ROLE)):
            return await util.exception(ctx.channel, "This user is not muted!")
            
        mute_embed = discord.Embed(title=f"New case | Unmute | {member}", color=15066368)
        mute_embed.add_field(name="User", value=member.mention)
        mute_embed.add_field(name="Reason", value=reason, inline=False)
        
        await util.unmute(member)
        await tasks.delete_task(member, Strike.MUTE, reason)
        await util.strike(member.id, Strike.UNMUTE, reason)
        await util.say(configs.LOGS, embed=mute_embed)
        await util.react_to(ctx.message, u"\u2705")
    
    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: discord.Member, *, reason:str=NO_REASON):
        """
        USAGE EXAMPLES:
        !kick @DeveloperAnonymous
        !kick @DeveloperAnonymous Is a noob
        """
        kick_embed = discord.Embed(title=f"New case | Kick | {member}", color=16758079)
        kick_embed.add_field(name="User", value=member.mention)
        kick_embed.add_field(name="Reason", value=reason, inline=False)

        try:
            await member.send("You have been kicked in %s: %s" % (ctx.guild.name, reason))
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warn("Failed to notify kick")

        await member.kick(reason=reason)
        await util.strike(member.id, Strike.KICK, reason)
        await util.say(configs.LOGS, embed=kick_embed)
        await util.react_to(ctx.message, u"\u2705")
    
    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx: Context, user: discord.User, *, reason:str=NO_REASON):
        """
        USAGE EXAMPLES:
        !ban @DeveloperAnonymous
        !ban @DeveloperAnonymous Is a noob
        """
        guild:discord.Guild = ctx.guild
        
        if user in [entry.user for entry in await guild.bans()]:
            return await util.exception(ctx.channel, "This user is already banned!")

        ban_embed = discord.Embed(title=f"New case | Ban | {user}", color=993326)
        ban_embed.add_field(name="User", value=user.mention)
        ban_embed.add_field(name="Reason", value=reason, inline=False)

        try:
            await user.send("You have been banned in %s: %s" % (ctx.guild.name, reason))
        except (discord.errors.HTTPException, discord.errors.Forbidden):
            util.logger.warn("Failed to notify ban")
        
        await ctx.guild.ban(user, reason=reason)
        await util.strike(user.id, Strike.BAN, reason)
        await util.say(configs.LOGS, embed=ban_embed)
        await util.react_to(ctx.message, u"\u2705")
    
    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx: Context, user: discord.User, *, reason:str=NO_REASON):
        """
        USAGE EXAMPLES:
        !unban @DeveloperAnonymous
        !unban @DeveloperAnonymous Is not a noob anymore
        """
        guild:discord.Guild = ctx.guild
        
        if user not in [entry.user for entry in await guild.bans()]:
            return await util.exception(ctx.channel, "This user is not banned!")

        unban_embed = discord.Embed(title=f"New case | Unban | {user}", color=993326)
        unban_embed.add_field(name="User", value=user.mention)
        unban_embed.add_field(name="Reason", value=reason, inline=False)
        
        await guild.unban(user, reason=reason)
        await util.strike(user.id, Strike.UNBAN, reason)
        await util.say(configs.LOGS, embed=unban_embed)
        await util.react_to(ctx.message, u"\u2705")

    async def cog_command_error(self, ctx: Context, error):
        await util.say(ctx.channel, error)

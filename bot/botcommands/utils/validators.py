import discord
from discord.ext import commands


def has_at_least_role(role_id: int | str):
    def predicate(ctx: commands.Context):
        if ctx.guild is None or isinstance(ctx.author, discord.User):
            raise commands.NoPrivateMessage()

        highest_role = ctx.author.roles[-1]
        required_role = ctx.guild.get_role(role_id)
        if highest_role.position >= required_role.position:
            return True

        raise commands.MissingRole(role_id)

    return commands.check(predicate)

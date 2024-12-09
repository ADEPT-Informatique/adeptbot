"""This module contains the commands related to the members of the server."""

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import configs
from bot.botcommands.utils.validators import has_at_least_role
from bot.db.services.reaction_role_service import ReactionRoleService
from bot.util import AdeptBotException


class ReactionRoleCog(commands.Cog):
    """This class contains the commands related to the members of the server."""

    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
        self.reaction_role_service = ReactionRoleService()

    @commands.command()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def addreactionrole(self, ctx: Context, message_id: int, emoji: str, role: discord.Role):
        """
        Cette commande permet d'ajouter une réaction à un message et de la lier à un rôle.

        Utilisation:
        !addreactionrole <message_id> <emoji> <role_id>
        """
        message = await ctx.fetch_message(message_id)

        if not message or not role:
            raise AdeptBotException("Message ou rôle invalide!")

        await message.add_reaction(emoji)
        await self.reaction_role_service.add_reaction_role(message_id, emoji, role.id)
        await ctx.send(f"Réaction {emoji} ajoutée au message {message.jump_url} et liée au rôle {role.name}.")

    @commands.command()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def removereactionrole(self, ctx: Context, message_id: int, emoji: str):
        """
        Cette commande permet de retirer une réaction d'un message et de supprimer le lien avec un rôle.

        Utilisation:
        !removereactionrole <message_id> <emoji>
        """
        message = await ctx.fetch_message(message_id)

        if not message:
            raise AdeptBotException("Message invalide!")

        await message.clear_reaction(emoji)
        await self.reaction_role_service.remove_reaction_role(message_id, emoji)
        await ctx.send(f"Réaction {emoji} retirée du message {message.jump_url}.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """This event is called when a reaction is added to a message."""
        if payload.member.bot:
            return

        reaction_role = await self.reaction_role_service.get_reaction_role(payload.message_id, str(payload.emoji))
        if reaction_role:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(reaction_role.role_id)
            await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """This event is called when a reaction is removed from a message."""
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot:
            return

        reaction_role = await self.reaction_role_service.get_reaction_role(payload.message_id, str(payload.emoji))
        if reaction_role:
            role = guild.get_role(reaction_role.role_id)
            await member.remove_roles(role)

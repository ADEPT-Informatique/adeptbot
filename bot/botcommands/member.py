"""This module contains the commands related to the members of the server."""

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import configs
from bot import tickets, util, welcome
from bot.botcommands.utils.validators import has_at_least_role
from bot.db.models.user import AdeptMember
from bot.db.services import ReactionRoleService, UserService
from bot.interactions import TicketOpeningInteraction
from bot.interactions import ticket as ticket_interactions
from bot.util import AdeptBotException


class MemberCog(commands.Cog):
    """This class contains the commands related to the members of the server."""

    def __init__(self) -> None:
        self.user_service = UserService()
        self.reaction_role_service = ReactionRoleService()

    @commands.command()
    async def ticket(self, ctx: Context, ticket: tickets.TicketConverter):
        """
        Cette commande permet de créer un ticket de support.

        Utilisation:
        !ticket moron
        !ticket plainte
        """
        category = ctx.channel.category
        if category is not None and category.id == configs.TICKET_CATEGORY:
            return await ctx.message.add_reaction(configs.CROSS_REACT)

        await ticket_interactions.create_ticket(ctx.author, ticket)
        await ctx.message.add_reaction(configs.CHECK_REACT)

    @commands.command()
    async def close(self, ctx: Context):
        """
        Cettte commande permet de fermer le ticket dans lequel l'utilisateur se trouve.
        """
        category = ctx.channel.category
        if category is None or category.id != configs.TICKET_CATEGORY:
            return await ctx.message.add_reaction(configs.CROSS_REACT)

        await util.archive_ticket(ctx.author, ctx.channel)

    @commands.command()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def create_ticket(self, ctx: Context):
        """
        Cette commande permet de créer une interaction pour créer un ticket de support.
        """
        await ctx.channel.send(configs.TICKET_VIEW_MESSAGE, view=TicketOpeningInteraction())

    @commands.command(aliases=["stalk"])
    @has_at_least_role(configs.ADMIN_ROLE)
    async def search(self, ctx: Context, user: discord.User):
        """
        Cette commande permet de rechercher un membre dans la base de données.

        Utilisation:
        !search @DeveloperAnonymous
        !search 115269304705875969
        """
        result = self.user_service.find_by_id(user.id)

        if result is None:
            raise AdeptBotException("Aucune donnée n'a été trouvé pour le membre!")

        adept_member = AdeptMember(
            result["_id"],
            result["name"],
            result["email"],
            result["is_student"],
            is_teacher=result["is_teacher"],
            is_it_student=result["is_it_student"],
            student_id=result["student_id"],
            program=result["program"],
        )

        embed = await welcome.create_welcome_embed(user, adept_member)
        embed.title = f"Résultat de recherche pour {user}"

        await ctx.send(embed=embed)

    @has_at_least_role(configs.ADMIN_ROLE)
    @commands.command(name="count", aliases=["compte", "c", "total", "t"])
    async def count_students_in_computer_science(self, ctx: Context):
        """Cette commande permet de compter le nombre d'étudiants dans le programme de Technique Informatique."""
        guild = ctx.guild
        former_student_role = guild.get_role(configs.FORMER_STUDENT_ROLE)
        prog_role = guild.get_role(configs.PROG_ROLE)
        network_role = guild.get_role(configs.NETWORK_ROLE)
        decbac_role = guild.get_role(configs.DECBAC_ROLE)

        former_student_count = 0
        prog_students_count = 0
        network_students_count = 0
        decbac_students_count = 0

        members = guild.members
        for member in members:
            if former_student_role in member.roles:
                former_student_count += 1
            elif prog_role in member.roles:
                prog_students_count += 1
            elif network_role in member.roles:
                network_students_count += 1
            elif decbac_role in member.roles:
                decbac_students_count += 1

        comp_sci_students_number = sum((prog_students_count, network_students_count, decbac_students_count))

        await ctx.send(
            f"Présentement, ``{comp_sci_students_number}`` étudiants sont dans le programme.\n"
            + "Plus précisément:\n"
            + f"  - ``{prog_students_count}`` en **Programmation**\n"
            + f"  - ``{network_students_count}`` en **Réseau**\n"
            + f"  - ``{decbac_students_count}`` en **DEC-BAC**\n\n"
            + f"  - ``{former_student_count}`` anciens étudiants"
        )

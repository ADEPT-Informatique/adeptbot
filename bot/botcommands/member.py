import configs
import discord
from bot import util, welcome
from bot.botcommands.utils.validators import has_at_least_role
from bot.db.models.user import AdeptMember
from bot.db.services.user_service import UserService
from bot.interactions import TicketOpeningInteraction
from bot.tickets import TicketConverter
from bot.util import AdeptBotException
from discord.ext import commands
from discord.ext.commands.context import Context


class MemberCog(commands.Cog):
    def __init__(self) -> None:
        self.user_service = UserService()

    @commands.command()
    async def ticket(self, ctx: Context, ticket: TicketConverter):
        """
        USAGE EXAMPLES:
        !ticket moron
        !ticket plainte
        """
        category = ctx.channel.category
        if category != None and category.id == configs.TICKET_CATEGORY:
            return await ctx.message.add_reaction(configs.CROSS_REACT)

        await util.create_ticket(ctx.author, ticket)
        await ctx.message.add_reaction(configs.CHECK_REACT)

    @commands.command()
    async def close(self, ctx: Context):
        category = ctx.channel.category
        if category is None or category.id != configs.TICKET_CATEGORY:
            return await ctx.message.add_reaction(configs.CROSS_REACT)

        await util.archive_ticket(ctx.author, ctx.channel)

    @commands.command()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def create_ticket(self, ctx: Context):
        await ctx.channel.send(configs.TICKET_VIEW_MESSAGE, view=TicketOpeningInteraction())

    @commands.command()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def search(self, ctx: Context, user: discord.User):
        result = self.user_service.find_by_id(user.id)

        if result is None:
            raise AdeptBotException(
                "Aucune donnée n'a été trouvé pour le membre!")

        adept_member = AdeptMember(
            result["_id"],
            result["name"],
            result["email"],
            result["is_student"],
            is_teacher=result["is_teacher"],
            is_it_student=result["is_it_student"],
            student_id=result["student_id"],
            program=result["program"]
        )

        embed = await welcome.create_welcome_embed(user, adept_member)
        embed.title = f"Résultat de recherche pour {user}"

        await ctx.send(embed=embed)

    @commands.command()
    async def count_students_in_comp_sci(self, ctx: Context):
        # Non student
        former_student_count = 0
        # Students
        prog_students_count = 0
        network_students_count = 0
        decbac_students_count = 0

        # Get the guild object for the server you want to get the members from
        guild = ctx.guild

        # Get a list of all members in the server
        members = guild.members

        # Iterate through the list of members
        for member in members:
            # -Get the roles by searching for them by their id's
            # Not student role
            former_student_role = discord.utils.get(
                configs.FORMER_STUDENT_ROLE)
            # Student roles
            prog_role = discord.utils.get(configs.PROG_ROLE)
            network_role = discord.utils.get(configs.NETWORK_ROLE)
            decbac_role = discord.utils.get(configs.DECBAC_ROLE)

            if former_student_role in member.roles:
                former_student_count += 1
            elif prog_role in member.roles:
                prog_students_count += 1
            elif network_role in member.roles:
                network_students_count += 1
            elif decbac_role in member.roles:
                decbac_students_count += 1

        # Count the number of True (valid students) values in the results list
        comp_sci_students_number = prog_students_count + \
            network_students_count + decbac_students_count

        await ctx.send(f"Présentement, dans le serveur de l'ADEPT, ``{comp_sci_students_number}`` étudiants sont dans le programme de Technique Informatique.\n" +
                       "Plus précisément:\n" +
                       f"  - ``{prog_students_count}`` en **Programmation**\n" +
                       f"  - ``{network_students_count}`` en **Réseau**\n" +
                       f"  - ``{decbac_students_count}`` en **DEC-BAC**\n\n" +
                       f"Et ``{former_student_count}`` anciens étudiants")

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
            raise AdeptBotException("Aucune donnée n'a été trouvé pour le membre!")

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

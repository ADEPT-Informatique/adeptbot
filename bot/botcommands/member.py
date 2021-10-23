import traceback
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandInvokeError

import configs
from bot import welcome, util
from bot.interactions import TicketOpeningInteraction
from bot.tickets import TicketConverter


class MemberCog(commands.Cog):
    @commands.command()
    async def setup(self, ctx: Context):
        await ctx.reply("Nous vous avons envoyé un message en privé avec les instructions!")
        result = await welcome.walk_through_welcome(ctx.author)
        await welcome.process_welcome_result(ctx.author, result)

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
        
        await ctx.channel.delete()

    @commands.command()
    @commands.has_any_role(configs.ADMIN_ROLE)
    async def create_ticket(self, ctx: Context):
        await ctx.channel.send(configs.TICKET_VIEW_MESSAGE, view=TicketOpeningInteraction())

    async def cog_command_error(self, ctx: Context, error):
        if isinstance(error, CommandInvokeError):
            error = error.original
        
        if isinstance(error, welcome.NoReplyException):
            await util.exception(error.channel, error.message)
            return # We don't want to print the traceback
        
        if ctx is not None:
            await util.exception(ctx.channel, error)
            return
        
        traceback.print_exc()

import discord
from discord import ui, ButtonStyle

import configs
from bot import util
from bot.tickets import TicketType


class TicketOpeningInteraction(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='Plainte', style=ButtonStyle.blurple, custom_id=configs.TICKET_COMPLAINT_ID)
    async def green(self, button: ui.Button, interaction: discord.Interaction):
        await util.create_ticket(interaction.user, TicketType.COMPLAINT)

    @ui.button(label='Appel de moron', style=ButtonStyle.blurple, custom_id=configs.TICKET_MORON_ID)
    async def red(self, button: ui.Button, interaction: discord.Interaction):
        await util.create_ticket(interaction.user, TicketType.MORON)
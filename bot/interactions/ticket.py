"""Ticket interactions."""

import discord
from discord import ButtonStyle, ui

import configs
from bot import util
from bot.tickets import TicketType


class TicketOpeningInteraction(ui.View):
    """View for opening a ticket."""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='Plainte', style=ButtonStyle.blurple, custom_id=configs.TICKET_COMPLAINT_ID)
    async def btn_plainte(self, interaction: discord.Interaction, _: ui.Button):
        """Open a complaint ticket."""
        await interaction.response.send_message("Êtes-vous sûre de vouloir ouvrir un ticket de plainte?",
                                                view=TicketConfirmationInteraction(TicketType.COMPLAINT),
                                                ephemeral=True)

    @ui.button(label='Appel de moron', style=ButtonStyle.blurple, custom_id=configs.TICKET_MORON_ID)
    async def btn_moron(self, interaction: discord.Interaction, _: ui.Button):
        """Open a moron ticket."""
        await interaction.response.send_message("Êtes-vous sûre de vouloir ouvrir un ticket d'appel de moron?",
                                                view=TicketConfirmationInteraction(TicketType.MORON),
                                                ephemeral=True)


class TicketConfirmationInteraction(ui.View):
    """
    View for confirming the opening of a ticket.

    Attributes
    ----------
    `ticket_type` : TicketType
        The type of ticket to open.
    """

    def __init__(self, ticket_type: TicketType):
        super().__init__(timeout=30)
        self.ticket_type = ticket_type

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)

        return await super().interaction_check(interaction)

    @ui.button(label='Oui', style=ButtonStyle.green)
    async def btn_confirm(self, interaction: discord.Interaction, _: ui.Button):
        """Create the ticket."""
        await util.create_ticket(interaction.user, self.ticket_type)

    @ui.button(label='Non', style=ButtonStyle.red)
    async def btn_decline(self, interaction: discord.Interaction, _: ui.Button):
        """Cancel the ticket creation."""
        await interaction.edit_original_response(content='Vous avez annulé la création du ticket.')


class TicketCloseInteraction(ui.View):
    """View for closing a ticket."""

    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)

        return await super().interaction_check(interaction)

    @ui.button(label='Fermer', style=ButtonStyle.red, custom_id=configs.TICKET_CLOSE_ID)
    async def btn_close(self, interaction: discord.Interaction, _: ui.Button):
        """Close the ticket."""
        await util.archive_ticket(interaction.user, interaction.channel)

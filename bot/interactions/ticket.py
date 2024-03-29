"""Ticket interactions."""

import discord
from discord import ButtonStyle, ui

import configs
from bot import tickets, util


class TicketOpeningInteraction(ui.View):
    """View for opening a ticket."""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Plainte", style=ButtonStyle.blurple, custom_id=configs.TICKET_COMPLAINT_ID)
    async def btn_plainte(self, interaction: discord.Interaction, _: ui.Button):
        """Open a complaint ticket."""
        await interaction.response.send_message(
            "Êtes-vous sûre de vouloir ouvrir un ticket de plainte?",
            view=TicketConfirmationInteraction(tickets.TicketType.COMPLAINT),
            ephemeral=True,
        )

    @ui.button(label="Appel de moron", style=ButtonStyle.blurple, custom_id=configs.TICKET_MORON_ID)
    async def btn_moron(self, interaction: discord.Interaction, _: ui.Button):
        """Open a moron ticket."""
        await interaction.response.send_message(
            "Êtes-vous sûre de vouloir ouvrir un ticket d'appel de moron?",
            view=TicketConfirmationInteraction(tickets.TicketType.MORON),
            ephemeral=True,
        )


class TicketConfirmationInteraction(ui.View):
    """
    View for confirming the opening of a ticket.

    Attributes
    ----------
    `ticket_type` : TicketType
        The type of ticket to open.
    """

    def __init__(self, ticket_type: tickets.TicketType):
        super().__init__(timeout=30)
        self.ticket_type = ticket_type

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)

        return await super().interaction_check(interaction)

    @ui.button(label="Oui", style=ButtonStyle.green)
    async def btn_confirm(self, interaction: discord.Interaction, _: ui.Button):
        """Create the ticket."""
        await create_ticket(interaction.user, self.ticket_type)

    @ui.button(label="Non", style=ButtonStyle.red)
    async def btn_decline(self, interaction: discord.Interaction, _: ui.Button):
        """Cancel the ticket creation."""
        await interaction.edit_original_response(content="Vous avez annulé la création du ticket.")


class TicketCloseInteraction(ui.View):
    """View for closing a ticket."""

    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)

        return await super().interaction_check(interaction)

    @ui.button(label="Fermer", style=ButtonStyle.red, custom_id=configs.TICKET_CLOSE_ID)
    async def btn_close(self, interaction: discord.Interaction, _: ui.Button):
        """Close the ticket."""
        await util.archive_ticket(interaction.user, interaction.channel)


async def create_ticket(member: discord.Member, ticket: tickets.TicketType):
    """
    Creates a ticket for a member.

    Parameters
    ----------
    `member` : discord.Member
        The member to create the ticket for.
    `ticket` : TicketType
        The type of the ticket.
    """
    guild = member.guild
    category: discord.CategoryChannel = guild.get_channel(configs.TICKET_CATEGORY)
    overwrites = discord.PermissionOverwrite(
        view_channel=True, read_messages=True, send_messages=True, read_message_history=True
    )
    channel = await category.create_text_channel(f"{member.display_name}")
    await channel.set_permissions(member, overwrite=overwrites)

    admin = guild.get_role(configs.ADMIN_ROLE)
    close_button = TicketCloseInteraction()
    await channel.send(
        configs.TICKET_MESSAGE.format(
            plaintive=member.mention, admins=admin.mention, ticket_type=ticket, prefix=configs.PREFIX
        ),
        view=close_button,
    )

    return channel

import disnake
from disnake import ui, ButtonStyle

import configs
from bot import util
from bot.tickets import TicketType


class TicketOpeningInteraction(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='Plainte', style=ButtonStyle.blurple, custom_id=configs.TICKET_COMPLAINT_ID)
    async def plainte(self, button: ui.Button, interaction: disnake.Interaction):
        await interaction.send("Êtes-vous sûre de vouloir ouvrir un ticket de plainte?",
                                                view=TicketConfirmationInteraction(TicketType.COMPLAINT),
                                                ephemeral=True)

    @ui.button(label='Appel de moron', style=ButtonStyle.blurple, custom_id=configs.TICKET_MORON_ID)
    async def moron(self, button: ui.Button, interaction: disnake.Interaction):
        await interaction.send("Êtes-vous sûre de vouloir ouvrir un ticket d'appel de moron?",
                                                view=TicketConfirmationInteraction(TicketType.MORON),
                                                ephemeral=True)


class TicketConfirmationInteraction(ui.View):
    def __init__(self, ticket_type: TicketType):
        super().__init__(timeout=30)
        self.ticket_type = ticket_type

    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)

        return await super().interaction_check(interaction)

    @ui.button(label='Oui', style=ButtonStyle.green)
    async def confirm(self, button: ui.Button, interaction: disnake.Interaction):
        await interaction.response.defer()
        await util.create_ticket(interaction.user, self.ticket_type)

    @ui.button(label='Non', style=ButtonStyle.red)
    async def decline(self, button: ui.Button, interaction: disnake.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_message(content='Vous avez annulé la création du ticket.')


class TicketCloseInteraction(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: disnake.Interaction) -> bool:
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)

        return await super().interaction_check(interaction)

    @ui.button(label='Fermer', style=ButtonStyle.red, custom_id=configs.TICKET_CLOSE_ID)
    async def close(self, button: ui.Button, interaction: disnake.Interaction):
        await interaction.response.defer()
        await util.archive_ticket(interaction.user, interaction.channel)

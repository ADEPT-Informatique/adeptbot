"""Welcome interaction."""

import discord
from discord import ButtonStyle, ui

from bot.programs import Programs


class StudentInteraction(ui.View):
    """View for selecting a program."""

    def __init__(self, timeout: int = 60):
        self.program = None
        super().__init__(timeout=timeout)

    async def start(self):
        """Start the view and wait for a response."""
        await self.wait()

        return self.program

    @ui.button(label="Programmation", style=ButtonStyle.primary)
    async def btn_prog(self, interaction: discord.Interaction, _: ui.Button):
        """Set the program to programming."""
        await interaction.response.defer()
        self.program = Programs.PROGRAMMING.value
        self.stop()

    @ui.button(label="Réseautique", style=ButtonStyle.primary)
    async def btn_network(self, interaction: discord.Interaction, _: ui.Button):
        """Set the program to networking."""
        await interaction.response.defer()
        self.program = Programs.NETWORKING.value
        self.stop()

    @ui.button(label="DEC-BAC", style=ButtonStyle.primary)
    async def btn_decbac(self, interaction: discord.Interaction, _: ui.Button):
        """Set the program to DEC-BAC."""
        await interaction.response.defer()
        self.program = Programs.DECBAC.value
        self.stop()

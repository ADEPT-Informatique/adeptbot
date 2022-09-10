import discord
from discord import ButtonStyle, ui

from bot.programs import Programs


class StudentInteraction(ui.View):
    def __init__(self, timeout: int = 60):
        self.program = None
        super().__init__(timeout=timeout)

    async def start(self):
        await self.wait()

        return self.program

    @ui.button(label="Programmation", style=ButtonStyle.primary)
    async def prog(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        self.program = Programs.PROGRAMMING
        self.stop()

    @ui.button(label="Réseautique", style=ButtonStyle.primary)
    async def network(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        self.program = Programs.NETWORKING
        self.stop()

    @ui.button(label="DEC-BAC", style=ButtonStyle.primary)
    async def decbac(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        self.program = Programs.DECBAC
        self.stop()

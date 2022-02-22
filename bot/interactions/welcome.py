from disnake import ui
from disnake.enums import ButtonStyle
from disnake.interactions import Interaction


class StudentInteraction(ui.View):
    def __init__(self, timeout: int = 60):
        self.program = None
        super().__init__(timeout=timeout)

    async def start(self):
        await self.wait()

        return self.program

    @ui.button(label="Programmation", style=ButtonStyle.primary)
    async def prog(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.program = "prog"
        self.stop()

    @ui.button(label="Réseautique", style=ButtonStyle.primary)
    async def network(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.program = "network"
        self.stop()

    @ui.button(label="DEC-BAC", style=ButtonStyle.primary)
    async def decbac(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.program = "decbac"
        self.stop()

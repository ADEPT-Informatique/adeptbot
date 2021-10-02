from discord import ui
from discord.interactions import Interaction

class WelcomeInteraction(ui.View):

    @ui.button(label="Programmation")
    async def prog(self, button: ui.Button, interaction: Interaction):
        pass
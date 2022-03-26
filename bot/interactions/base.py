from types import NoneType
from disnake import ButtonStyle, Interaction, ui

class YesNoInteraction(ui.View):
    """
    Basic yes/no interaction

    Parameters
    ------------
    timeout: Optional[:class:`int`]
        Timeout in seconds, defaults to 300
    """

    def __init__(self, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.value: bool | NoneType = None

    async def start(self):
        """
        Start the interaction and wait for a response from the user or timeout

        return: The value of the interaction if the user responded, `None` if the user timed out
        """
        await self.wait()

        return self.value


    @ui.button(label="Oui", style=ButtonStyle.green)
    async def yes(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.value = True
        self.stop()

    @ui.button(label="Non", style=ButtonStyle.red)
    async def no(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.value = False
        self.stop()

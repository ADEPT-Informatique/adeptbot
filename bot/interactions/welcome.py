from discord import ui
from discord.enums import ButtonStyle
from discord.interactions import Interaction

class WelcomeInteraction(ui.View):
    async def start(self):
        timed_out = await self.wait()
        if timed_out:
            return None
        return self.is_student

    @ui.button(label="Oui", style=ButtonStyle.green)
    async def yes_student(self, button: ui.Button, interaction: Interaction):
        self.is_student = True
        self.stop()

    @ui.button(label="Non", style=ButtonStyle.red)
    async def no_student(self, button: ui.Button, interaction: Interaction):
        self.is_student = False
        self.stop()


class StudentInteraction(ui.View):
    async def start(self):
        timed_out = await self.wait()
        if timed_out:
            return None
        return self.program

    @ui.button(label="Programmation", style=ButtonStyle.primary)
    async def prog(self, button: ui.Button, interaction: Interaction):
        self.program = "prog"
        self.stop()

    @ui.button(label="Réseautique", style=ButtonStyle.primary)
    async def network(self, button: ui.Button, interaction: Interaction):
        self.program = "network"
        self.stop()

    @ui.button(label="DEC-BAC", style=ButtonStyle.primary)
    async def decbac(self, button: ui.Button, interaction: Interaction):
        self.program = "decbac"
        self.stop()


class TeacherInteraction(ui.View):
    async def start(self):
        timed_out = await self.wait()
        if timed_out:
            return None
        return self.is_teacher
    
    @ui.button(label="Oui", style=ButtonStyle.green)
    async def yes_teacher(self, button: ui.Button, interaction: Interaction):
        self.is_teacher = True
        self.stop()

    @ui.button(label="Non", style=ButtonStyle.red)
    async def no_teacher(self, button: ui.Button, interaction: Interaction):
        self.is_teacher = False
        self.stop()


class ConfirmationInteraction(ui.View):
    async def start(self):
        timed_out = await self.wait()
        if timed_out:
            return None
        return self.confirmed

    @ui.button(label="Oui", style=ButtonStyle.green)
    async def yes(self, button: ui.Button, interaction: Interaction):
        self.confirmed = True
        self.stop()

    @ui.button(label="Non", style=ButtonStyle.red)
    async def no(self, button: ui.Button, interaction: Interaction):
        self.confirmed = False
        self.stop()
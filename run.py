import traceback
import discord
from discord.ext import commands
from discord.ext.commands.errors import NoEntryPointError
from bot.http.models.user import WelcomeUser
from bot.interactions import WelcomeInteraction
import sys
import asyncio
import re
from bot.interactions.welcome import ConfirmationInteraction, StudentInteraction, TeacherInteraction

import configs
from bot import util, tasks
from bot.botcommands import moderation

bot_prefix = "!"

class AdeptClient(commands.Bot):
    def __init__(self, prefix):
        intents = discord.Intents.default()
        intents.members = True
        loop = asyncio.get_event_loop()
        super().__init__(prefix, loop=loop, intents=intents)
        self.loop = loop
        
        self.add_cog(moderation.Moderation(self))

    async def on_message(self, message):
        if isinstance(message.channel, discord.abc.PrivateChannel):
            return

        mentions_self_regex = f"<@.?{self.user.id}>"
        if re.match("^"+mentions_self_regex, message.content):
            message.content = re.sub(mentions_self_regex + "\s*", bot_prefix, message.content)
        
        if message.content.startswith(bot_prefix):
            await self.process_commands(message)

    async def on_ready(self):
        util._load(self)
        util.logger.info("\nLogged in with account @%s ID:%s \n-------",
                        self.user.name, self.user.id)

        await self.change_presence(activity=discord.Activity(name="for bad boys!", type=discord.ActivityType.watching))
        tasks._load_tasks(self)

    async def walk_through_welcome(self, member: discord.Member):
        welcome_view = WelcomeInteraction()
        original_message: discord.Message = await member.send(content=util.get_welcome_instruction("Êtes-vous un étudiant en informatique?"), view=welcome_view)
        is_student = await welcome_view.start()

        if is_student is None:
            return await member.send("Nous avons pas reçu de réponse! Utilisez `!setup` pour recommencer.")

        await original_message.edit(content=util.get_welcome_instruction("Quel est votre nom?"), view=None)
        student_name_msg = await self.wait_for("message", check=lambda message:message.author.id == member.id and isinstance(message.channel, discord.DMChannel))
        
        # TODO: Make a None check
        student_name = student_name_msg.content
        confirmation_embed = discord.Embed(title="Est-ce que ces informations sont tous exactes?")
        confirmation_embed.add_field(name="Nom:", value=student_name, inline=False)

        if is_student:
            student_view = StudentInteraction()
            await original_message.edit(content=util.get_welcome_instruction("Quel est votre programme?"), view=student_view)
            program = await student_view.start()

            if program == "prog":
                program = "Programmation"
            elif program == "network":
                program == "Réseautique"
            elif program == "decbac":
                program = "DEC-BAC"

            await original_message.edit(content=util.get_welcome_instruction("Quel est votre numéro étudiant?"), view=None)
            student_number_msg = await self.wait_for("message", check=lambda message:message.author.id == member.id and isinstance(message.channel, discord.DMChannel))

            # TODO: Make a None check
            student_number = student_number_msg.content
            confirmation_embed.add_field(name="Numéro étudiant:", value=student_number, inline=False)
            confirmation_embed.add_field(name="Programme:", value=program, inline=False)
        else:
            teacher_view = TeacherInteraction()
            await original_message.edit(content=util.get_welcome_instruction("Êtes-vous un professeur?"), view=teacher_view)
            is_teacher = await teacher_view.start()

            if not is_teacher:
                await member.send("Entrée invalide, veuillez recommencer!")
                return await self.walk_through_welcome(member)
            
            confirmation_embed.add_field(name="Professeur:", value="Oui" if is_teacher else "Non", inline=False)

        confirmation_view = ConfirmationInteraction()
        confirmation_message = await member.send(embed=confirmation_embed, view=confirmation_view)
        confirmed = await confirmation_view.start()

        if confirmed:
            await member.send("Parfait, tout est beau!")
            await confirmation_message.edit(view=None)
        else:
            await member.send("D'accord, recommencons!")
            return await self.walk_through_welcome(member)

        return WelcomeUser(student_name, is_student, student_number, program)


    async def on_member_join(self, member: discord.Member):
        await self.say(configs.WELCOME_CHANNEL, configs.WELCOME_SERVER.format(name=member.mention))
        result = await self.walk_through_welcome(member)

        if isinstance(result, WelcomeUser):
            guild = member.guild
            name = result.name
            student_id = result.student_id

            role = None
            if result.is_student:
                if result.program == "Programmation":
                    role = guild.get_role(configs.PROG_ROLE)
                elif result.program == "Réseautique":
                    role = guild.get_role(configs.NETWORK_ROLE)
                elif result.program == "DEC-BAC":
                    role = guild.get_role(configs.DECBAC_ROLE)
            else:
                role = guild.get_role(configs.TEACHER_ROLE)

            await member.edit(nick=name, roles=[role], reason="Inital setup")

            # TODO: Post to API the new partial student setup
        else:
            util.logger.warning(f"Failed to complete setup for {member.name} ({member.id})")
            

    async def on_error(self, event, *args,  **kwargs):
        traceback.print_exc()

    async def say(self, channel, *args, **kwargs):
        if type(channel) is str:
            # channel_id/server_id
            channel_id, server_id = channel.split("/")
            channel = self.get_guild(int(server_id)).get_channel(int(channel_id))
        try:
            return await channel.send(*args, **kwargs)
        except discord.Forbidden as send_error:
            util.logger.warning(send_error)


if __name__ == "__main__":
    util.logger.info("Starting the bot!")
    client = AdeptClient(prefix=configs.PREFIX)
    client.run(configs.TOKEN)
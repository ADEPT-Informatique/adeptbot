import disnake

import configs
from bot import util
from bot.http.models.user import WelcomeUser
from bot.interactions.welcome import (ConfirmationInteraction,
                                      StudentInteraction, TeacherInteraction,
                                      WelcomeInteraction)

NO_REPLY = "Nous avons pas reçu de réponse! Utilisez `!setup` pour recommencer."


class NoReplyException(TimeoutError):
    def __init__(self, channel: disnake.abc.Messageable, message: str = NO_REPLY) -> None:
        self.channel = channel
        self.message = message


async def walk_through_welcome(member: disnake.Member):
    current_view = WelcomeInteraction()
    original_message: disnake.Message = await member.send(embed=util.get_welcome_instruction("Êtes-vous un étudiant en informatique?"), view=current_view)
    is_student = await current_view.start()

    if is_student is None:
        raise NoReplyException(member)

    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre nom?"), view=current_view)
    student_name_msg = await util.client.wait_for("message", check=lambda message: message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if student_name_msg is None:
        raise NoReplyException(member)

    student_name = student_name_msg.content
    confirmation_embed = disnake.Embed(title="Est-ce que ces informations sont tous exactes?")
    confirmation_embed.add_field(name="Nom:", value=student_name, inline=False)

    if is_student:
        student_number, program = await __process_student(member, original_message)

        confirmation_embed.add_field(name="Numéro étudiant:", value=student_number, inline=False)
        confirmation_embed.add_field(name="Programme:", value=program, inline=False)
    else:
        is_teacher = await __process_teacher(member, original_message)

        confirmation_embed.add_field(name="Professeur:", value="Oui" if is_teacher else "Non", inline=False)

    confirmed = await __process_confirmation(member, confirmation_embed)
    
    if confirmed is None:
        return WelcomeUser(student_name, is_student, student_number, program)
    elif confirmed:
        return await walk_through_welcome(member)
    else:
        return await member.send("Parfait, on ne recommence pas!")


async def __process_confirmation(member: disnake.Member, embed: disnake.Embed):
    current_view = ConfirmationInteraction()
    confirmation_message = await member.send(embed=embed, view=current_view)
    confirmed = await current_view.start()

    if confirmed is None:
        raise NoReplyException(member)

    await confirmation_message.edit(view=current_view)
    if confirmed:
        await member.send("Parfait, tout est beau!")
    else:
        current_view = ConfirmationInteraction()
        restart_message = await member.send("D'accord, voulez-vous recommencer?", view=current_view)
        restart = await current_view.start()

        await restart_message.edit(view=current_view)
        if restart is None:
            raise NoReplyException(member)

        return restart


async def __process_teacher(member: disnake.Member, original_message: disnake.Message):
    current_view = TeacherInteraction()
    await original_message.edit(embed=util.get_welcome_instruction("Êtes-vous un professeur?"), view=current_view)
    is_teacher = await current_view.start()

    if is_teacher is None:
        raise NoReplyException(member)
    
    await original_message.edit(view=current_view)

    return is_teacher


async def __process_student(member: disnake.Member, original_message: disnake.Message):
    current_view = StudentInteraction()
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre programme?"), view=current_view)
    program = await current_view.start()

    if program is None:
        await original_message.edit(view=current_view)
        raise NoReplyException(member)
    
    if program == "prog":
        program = "Programmation"
    elif program == "network":
        program = "Réseautique"
    elif program == "decbac":
        program = "DEC-BAC"

    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre numéro étudiant?"), view=current_view)
    student_number_msg = await util.client.wait_for("message", check=lambda message:message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if student_number_msg is None:
        await original_message.edit(view=current_view)
        raise NoReplyException(member)

    student_number = student_number_msg.content

    return student_number, program


async def process_welcome_result(member: disnake.Member, result):
    if isinstance(result, WelcomeUser):
        guild = member.guild
        name = result.name

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

        embed = disnake.Embed(title="Nouveau membre dans ADEPT-Informatique", timestamp=disnake.utils.utcnow())
        embed.add_field(name="Nom:", value=name, inline=False)
        embed.add_field(name="Numéro étudiant:", value=result.student_id, inline=False)
        embed.add_field(name="Professeur:", value="Oui" if result.is_teacher else "Non", inline=False)
        embed.add_field(name="Programme:", value=result.program, inline=False)
        embed.add_field(name="id", value=member.id, inline=False)

        await util.say(configs.LOGS_CHANNEL, embed=embed)
        # TODO: Post to API the new partial student setup
    else:
        util.logger.warning(f"Failed to complete setup for {member.name} ({member.id})")

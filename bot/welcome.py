import disnake

import configs
from bot import util
from bot.db.models import WelcomeUser
from bot.interactions.welcome import (ConfirmationInteraction,
                                      StudentInteraction, TeacherInteraction,
                                      WelcomeInteraction)

NO_REPLY = "Nous avons pas reçu de réponse! Utilisez `!setup` pour recommencer."


class NoReplyException(TimeoutError):
    def __init__(self, channel: disnake.abc.Messageable, message: str = NO_REPLY) -> None:
        self.channel = channel
        self.message = message


async def walk_through_welcome(member: disnake.Member):
    welcome_view = WelcomeInteraction()
    original_message: disnake.Message = await member.send(embed=util.get_welcome_instruction("Êtes-vous un étudiant en informatique?"), view=welcome_view)
    is_student = await welcome_view.start()

    if is_student is None:
        raise NoReplyException(member)

    full_name = await __process_name(member, original_message)

    email = await __process_email(member, util.get_welcome_instruction("Quel est votre adresse email?"))

    confirmation_embed = disnake.Embed(title="Est-ce que ces informations sont tous exactes?", color=0xF9E18B)
    confirmation_embed.add_field(name="Nom:", value=full_name, inline=False)
    confirmation_embed.add_field(name="Email:", value=email, inline=False)

    if is_student:
        student_number, program = await __process_student(member, original_message)

        confirmation_embed.add_field(name="Numéro étudiant:", value=student_number, inline=False)
        confirmation_embed.add_field(name="Programme:", value=program, inline=False)
    else:
        is_teacher = await __process_teacher(member, original_message)

        confirmation_embed.add_field(name="Professeur:", value="Oui" if is_teacher else "Non", inline=False)

    confirmed = await __process_confirmation(member, confirmation_embed)
    
    if confirmed is None:
        welcome_user = WelcomeUser(member.id, full_name, email, is_student, student_number, program)
        welcome_user.save()

        return welcome_user
    elif confirmed:
        return await walk_through_welcome(member)
    else:
        return await member.send("Parfait, on ne recommence pas!")


async def __process_confirmation(member: disnake.Member, embed: disnake.Embed):
    confirmation_view = ConfirmationInteraction()
    confirmation_message = await member.send(embed=embed, view=confirmation_view)
    confirmed = await confirmation_view.start()

    if confirmed is None:
        raise NoReplyException(member)

    await confirmation_message.edit(view=None)
    if confirmed:
        await member.send("Parfait, tout est beau!")
    else:
        confirmation_view = ConfirmationInteraction()
        restart_message = await member.send("D'accord, voulez-vous recommencer?", view=confirmation_view)
        restart = await confirmation_view.start()

        await restart_message.edit(view=confirmation_view)
        if restart is None:
            raise NoReplyException(member)

        return restart


async def __process_name(member: disnake.Member, original_message: disnake.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre prénom?"), view=None)
    first_name_msg = await util.client.wait_for("message", check=lambda message: message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if first_name_msg is None:
        raise NoReplyException(member)
    first_name = first_name_msg.content

    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre nom de famille?"))
    last_name_msg = await util.client.wait_for("message", check=lambda message: message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if last_name_msg is None:
        raise NoReplyException(member)
    last_name = last_name_msg.content

    full_name = f"{first_name} {last_name}"
    return full_name


async def __process_email(member: disnake.Member, original_message: disnake.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre adresse email?"), view=None)
    email_msg = await util.client.wait_for("message", check=lambda message: message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if email_msg is None:
        raise NoReplyException(member)
    email = email_msg.content

    return email


async def __process_teacher(member: disnake.Member, original_message: disnake.Message):
    current_view = TeacherInteraction()
    await original_message.edit(embed=util.get_welcome_instruction("Êtes-vous un professeur?"), view=current_view)
    is_teacher = await current_view.start()

    if is_teacher is None:
        raise NoReplyException(member)
    
    await original_message.edit(view=current_view)

    return is_teacher


async def __process_student(member: disnake.Member, original_message: disnake.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre numéro étudiant?"), view=None)
    student_number_msg = await util.client.wait_for("message", check=lambda message:message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if student_number_msg is None:
        raise NoReplyException(member)

    student_number = student_number_msg.content

    student_view = StudentInteraction()
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre programme?"), view=student_view)
    program = await student_view.start()

    if program is None:
        await original_message.edit(view=None)
        raise NoReplyException(member)
    
    if program == "prog":
        program = "Programmation"
    elif program == "network":
        program = "Réseautique"
    elif program == "decbac":
        program = "DEC-BAC"

    return int(student_number), program


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

        roles = [role for role in member.roles if role.id not in (configs.PROG_ROLE, configs.NETWORK_ROLE, configs.DECBAC_ROLE, configs.TEACHER_ROLE)]
        roles.append(role)
        try:
            await member.edit(nick=name, roles=roles, reason="Inital setup")
        except disnake.Forbidden:
            await member.send("Vous avez des permissions plus élevées que moi. Veuillez contacter un administrateur.\n\n" +
                                "Si vous êtes un administrateur, veuillez changer vos informations.")

        embed = disnake.Embed(title="Nouveau membre dans ADEPT-Informatique", timestamp=disnake.utils.utcnow())
        embed.add_field(name="Nom:", value=name, inline=False)
        embed.add_field(name="Email:", value=result.email, inline=False)
        embed.add_field(name="Numéro étudiant:", value=result.student_id, inline=False)
        embed.add_field(name="Professeur:", value="Non" if result.is_student else "Oui", inline=False)
        embed.add_field(name="Programme:", value=result.program, inline=False)
        embed.add_field(name="ID:", value=member.id, inline=False)

        await util.say(configs.LOGS_CHANNEL, embed=embed)
    else:
        util.logger.warning(f"Failed to complete setup for {member.name} ({member.id})")

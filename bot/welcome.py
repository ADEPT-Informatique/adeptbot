import disnake

import configs
from bot import util
from bot.db.models import WelcomeUser
from bot.interactions import StudentInteraction, YesNoInteraction
from bot.util import AdeptBotError


class NoReplyException(AdeptBotError):
    def __init__(self, channel: disnake.abc.Messageable) -> None:
        super().__init__(channel, f"Nous n'avons pas reçu de réponse! Utilisez `{configs.PREFIX}setup` dans <#{configs.SETUP_CHANNEL}> pour recommencer.")


class InvalidInputException(AdeptBotError):
    def __init__(self, channel: disnake.abc.Messageable, message: str) -> None:
        super().__init__(channel, message)


class StudentProcessOutput:
    is_it_student: bool
    student_number: int
    program: str

    def __init__(self) -> None:
        self.is_it_student = None
        self.student_number = None
        self.program = None


async def __handle_on_timeout(member: disnake.Member, message: disnake.Message) -> NoReplyException:
    """
    Clean up the message from any interactions and raises a NoReplyException
    """
    await message.edit(view=None)
    raise NoReplyException(member)


async def walk_through_welcome(member: disnake.Member):
    is_student_view = YesNoInteraction()
    original_message: disnake.Message = await member.send(embed=util.get_welcome_instruction("Êtes-vous un étudiant?"), view=is_student_view)
    is_student = await is_student_view.start()

    if is_student is None:
        await __handle_on_timeout(member, original_message)

    full_name = await __process_name(member, original_message)

    email = await __process_email(member, original_message)

    welcome_user = WelcomeUser(member.id, full_name, email, is_student)

    confirmation_embed = disnake.Embed(title="Est-ce que ces informations sont tous exactes?", color=0xF9E18B)
    confirmation_embed.add_field(name="Nom:", value=full_name, inline=False)
    confirmation_embed.add_field(name="Email:", value=email, inline=False)
    confirmation_embed.add_field(name="Étudiant:", value="Oui" if is_student else "Non", inline=False)

    if is_student:
        process_student_result = await __process_student(member, original_message)

        welcome_user.student_id = process_student_result.student_number
        welcome_user.program = process_student_result.program
        welcome_user.is_it_student = process_student_result.is_it_student

        confirmation_embed.add_field(name="Numéro étudiant:", value=process_student_result.student_number, inline=False)
        if process_student_result.program is not None:
            confirmation_embed.add_field(name="Programme:", value=process_student_result.program, inline=False)
    else:
        is_teacher = await __process_teacher(member, original_message)
        welcome_user.is_teacher = is_teacher

        confirmation_embed.add_field(name="Professeur:", value="Oui" if is_teacher else "Non", inline=False)

    confirmed = await __process_confirmation(member, confirmation_embed)
    
    if confirmed is None:
        welcome_user.save()

        return welcome_user
    elif confirmed:
        return await walk_through_welcome(member)
    else:
        return await member.send("Parfait, on ne recommence pas!")


async def __process_confirmation(member: disnake.Member, embed: disnake.Embed):
    confirmation_view = YesNoInteraction()
    confirmation_message: disnake.Message = await member.send(embed=embed, view=confirmation_view)
    confirmed = await confirmation_view.start()

    if confirmed is None:
        await __handle_on_timeout(member, confirmation_message)

    await confirmation_message.edit(view=None)
    if confirmed:
        await member.send("Parfait, tout est beau!")
    else:
        confirmation_view = YesNoInteraction()
        restart_message = await member.send("D'accord, voulez-vous recommencer?", view=confirmation_view)
        restart = await confirmation_view.start()

        await restart_message.edit(view=confirmation_view)
        if restart is None:
            await __handle_on_timeout(member, restart_message)

        return restart


async def __process_name(member: disnake.Member, original_message: disnake.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre prénom?"), view=None)
    first_name_msg: disnake.Message = await util.client.wait_for("message", check=lambda message: message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if first_name_msg is None:
        await __handle_on_timeout(member, original_message)
    first_name = first_name_msg.content

    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre nom de famille?"))
    last_name_msg: disnake.Message = await util.client.wait_for("message", check=lambda message: message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if last_name_msg is None:
        await __handle_on_timeout(member, original_message)
    last_name = last_name_msg.content

    full_name = f"{first_name} {last_name}"
    return full_name


async def __process_email(member: disnake.Member, original_message: disnake.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre adresse email?"), view=None)
    email_msg: disnake.Message = await util.client.wait_for("message", check=lambda message: message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if email_msg is None:
        await __handle_on_timeout(member, original_message)
    email = email_msg.content

    return email


async def __process_teacher(member: disnake.Member, original_message: disnake.Message):
    current_view = YesNoInteraction()
    await original_message.edit(embed=util.get_welcome_instruction("Êtes-vous un professeur?"), view=current_view)
    is_teacher = await current_view.start()

    if is_teacher is None:
        await __handle_on_timeout(member, original_message)
    
    await original_message.edit(view=current_view)

    return is_teacher


async def __process_student(member: disnake.Member, original_message: disnake.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre matricule?"), view=None)
    student_number_msg: disnake.Message = await util.client.wait_for("message", check=lambda message:message.author.id == member.id and isinstance(message.channel, disnake.DMChannel))

    if student_number_msg is None:
        await __handle_on_timeout(member, original_message)

    student_number = student_number_msg.content
    if not student_number.isdigit():
        await util.exception(member, "Le numéro étudiant doit être un nombre entier.")
        return await __process_student(member, original_message)
        
    result = StudentProcessOutput()
    result.student_number = int(student_number)

    is_info_view = YesNoInteraction()
    await original_message.edit(embed=util.get_welcome_instruction("Êtes-vous un étudiant en informatique?"), view=is_info_view)
    is_it_student = await is_info_view.start()
    
    if is_it_student is None:
        await __handle_on_timeout(member, original_message)
    
    result.is_it_student = is_it_student

    if is_it_student:
        student_view = StudentInteraction()
        await original_message.edit(embed=util.get_welcome_instruction("Quel est votre programme?"), view=student_view)
        program = await student_view.start()

        await original_message.edit(view=None)
        if program is None:
            await __handle_on_timeout(member, original_message)
        
        if program == "prog":
            program = "Programmation"
        elif program == "network":
            program = "Réseautique"
        elif program == "decbac":
            program = "DEC-BAC"

        result.program = program

    return result


async def process_welcome_result(member: disnake.Member, result: WelcomeUser):
    guild = member.guild
    name = result.name

    role = None
    if result.is_it_student:
        if result.program == "Programmation":
            role = guild.get_role(configs.PROG_ROLE)
        elif result.program == "Réseautique":
            role = guild.get_role(configs.NETWORK_ROLE)
        elif result.program == "DEC-BAC":
            role = guild.get_role(configs.DECBAC_ROLE)
    elif result.is_student:
        role = guild.get_role(configs.REGULARS_ROLE)
    elif result.is_teacher:
        role = guild.get_role(configs.TEACHER_ROLE)

    roles = [role for role in member.roles if role.id not in (configs.PROG_ROLE, configs.NETWORK_ROLE, configs.DECBAC_ROLE, configs.TEACHER_ROLE)]
    if role is not None:
        roles.append(role)
    try:
        await member.edit(nick=name, roles=roles, reason="Inital setup")
    except disnake.Forbidden:
        await member.send("Vous avez des permissions plus élevées que moi. Veuillez contacter un administrateur.\n\n" +
                            "Si vous êtes un administrateur, veuillez changer vos informations.")

    embed = disnake.Embed(title="Nouveau membre dans ADEPT-Informatique", color=0xF9E18B, timestamp=disnake.utils.utcnow())
    embed.add_field(name="Nom:", value=name, inline=False)
    embed.add_field(name="Email:", value=result.email, inline=False)
    embed.add_field(name="Numéro étudiant:", value=result.student_id, inline=False)
    embed.add_field(name="Étudiant:", value="Non" if result.is_student else "Oui", inline=False)
    embed.add_field(name="Professeur:", value="Non" if result.is_teacher else "Oui", inline=False)
    embed.add_field(name="Programme:", value=result.program if result.is_it_student else "N'est pas en informatique" , inline=False)
    embed.set_footer(text=f"ID: {member.id}")

    content = None
    if not result.is_it_student or result.is_teacher:
        content = f"<@&{configs.ADMIN_ROLE}> Veuillez valider la requête de {member.mention}."

    await util.say(configs.LOGS_CHANNEL, content, embed=embed)

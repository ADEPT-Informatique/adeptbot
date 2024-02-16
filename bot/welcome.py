"""This module contains the code for the welcome process of the bot"""

import discord

import configs
from bot import util
from bot.db.models import AdeptMember
from bot.interactions import StudentInteraction, YesNoInteraction
from bot.interactions.errors import NoReplyException


class StudentProcessOutput:
    """This class represents the output of the student process"""

    __is_it_student: bool
    __student_number: int
    __program: str

    def __init__(self) -> None:
        self.__is_it_student = None
        self.__student_number = None
        self.__program = None

    @property
    def is_it_student(self) -> bool:
        """Returns whether the user is a student or not"""
        return self.__is_it_student

    @is_it_student.setter
    def is_it_student(self, value: bool) -> None:
        self.__is_it_student = value

    @property
    def student_number(self) -> int:
        """Returns the student number of the user"""
        return self.__student_number

    @student_number.setter
    def student_number(self, value: int) -> None:
        self.__student_number = value

    @property
    def program(self) -> str:
        """Returns the program of the user"""
        return self.__program

    @program.setter
    def program(self, value: str) -> None:
        self.__program = value


async def __handle_on_timeout(member: discord.Member, message: discord.Message) -> NoReplyException:
    """
    Clean up the message from any interactions and raises a NoReplyException
    """
    await message.edit(view=None)
    raise NoReplyException(member)


async def walk_through_welcome(member: discord.Member):
    """
    Walks through the welcome process with the given member

    Parameters
    ----------
    `member` : discord.Member
        The member to walk through the welcome process with
    """
    is_student_view = YesNoInteraction()
    original_message: discord.Message = await member.send(
        embed=util.get_welcome_instruction("Êtes-vous un étudiant?"),
        view=is_student_view,
    )
    is_student = await is_student_view.start()

    if is_student is None:
        await __handle_on_timeout(member, original_message)

    full_name = await __process_name(member, original_message)

    email = await __process_email(member, original_message)

    welcome_user = AdeptMember(member.id, full_name, email, is_student)

    confirmation_embed = discord.Embed(title="Est-ce que ces informations sont tous exactes?", color=0xF9E18B)
    confirmation_embed.add_field(name="Nom:", value=full_name, inline=False)
    confirmation_embed.add_field(name="Email:", value=email, inline=False)
    confirmation_embed.add_field(name="Étudiant:", value="Oui" if is_student else "Non", inline=False)

    if is_student:
        process_student_result = await __process_student(member, original_message)

        welcome_user.student_id = process_student_result.student_number
        welcome_user.program = process_student_result.program
        welcome_user.is_it_student = process_student_result.is_it_student

        confirmation_embed.add_field(
            name="Numéro étudiant:",
            value=process_student_result.student_number,
            inline=False,
        )
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

    if confirmed:
        return await walk_through_welcome(member)

    return await member.send("Parfait, on ne recommence pas!")


async def __process_confirmation(member: discord.Member, embed: discord.Embed):
    confirmation_view = YesNoInteraction()
    confirmation_message: discord.Message = await member.send(embed=embed, view=confirmation_view)
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


async def __process_name(member: discord.Member, original_message: discord.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre prénom?"), view=None)
    first_name_msg: discord.Message = await util.wait_for_message(member)

    if first_name_msg is None:
        await __handle_on_timeout(member, original_message)
    first_name = first_name_msg.content

    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre nom de famille?"))
    last_name_msg: discord.Message = await util.wait_for_message(member)

    if last_name_msg is None:
        await __handle_on_timeout(member, original_message)
    last_name = last_name_msg.content

    full_name = f"{first_name} {last_name}"
    return full_name


async def __process_email(member: discord.Member, original_message: discord.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre adresse email?"), view=None)
    email_msg: discord.Message = await util.wait_for_message(member)

    if email_msg is None:
        await __handle_on_timeout(member, original_message)
    email = email_msg.content

    return email


async def __process_teacher(member: discord.Member, original_message: discord.Message):
    current_view = YesNoInteraction()
    await original_message.edit(
        embed=util.get_welcome_instruction("Êtes-vous un professeur?"),
        view=current_view,
    )
    is_teacher = await current_view.start()

    if is_teacher is None:
        await __handle_on_timeout(member, original_message)

    await original_message.edit(view=current_view)

    return is_teacher


async def __process_student(member: discord.Member, original_message: discord.Message):
    await original_message.edit(embed=util.get_welcome_instruction("Quel est votre matricule?"), view=None)
    student_number_msg: discord.Message = await util.wait_for_message(member)

    if student_number_msg is None:
        await __handle_on_timeout(member, original_message)

    student_number = student_number_msg.content
    if not student_number.isdigit():
        await util.exception(member, "Le numéro étudiant doit être un nombre entier.")
        return await __process_student(member, original_message)

    result = StudentProcessOutput()
    result.student_number = int(student_number)

    is_info_view = YesNoInteraction()
    await original_message.edit(
        embed=util.get_welcome_instruction("Êtes-vous un étudiant en informatique?"),
        view=is_info_view,
    )
    is_it_student = await is_info_view.start()

    if is_it_student is None:
        await __handle_on_timeout(member, original_message)

    result.is_it_student = is_it_student

    if is_it_student:
        student_view = StudentInteraction()
        await original_message.edit(
            embed=util.get_welcome_instruction("Quel est votre programme?"),
            view=student_view,
        )
        program = await student_view.start()

        await original_message.edit(view=None)
        if program is None:
            await __handle_on_timeout(member, original_message)

        result.program = program

    return result


async def create_welcome_embed(member: discord.User, adept_member: AdeptMember):
    """
    Creates the welcome embed for the new member.

    Parameters
    ----------
    `member`: discord.User
        The new member.
    `adept_member`: AdeptMember
        The new member's information.
    """
    embed = discord.Embed(
        title="Nouveau membre dans ADEPT-Informatique",
        color=0xF9E18B,
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="Nom:", value=adept_member.name, inline=False)
    embed.add_field(name="Email:", value=adept_member.email, inline=False)
    embed.add_field(name="Numéro étudiant:", value=adept_member.student_id, inline=False)
    embed.add_field(
        name="Étudiant:",
        value="Oui" if adept_member.is_student else "Non",
        inline=False,
    )
    embed.add_field(
        name="Professeur:",
        value="Oui" if adept_member.is_teacher else "Non",
        inline=False,
    )
    embed.add_field(
        name="Programme:",
        value=(adept_member.program if adept_member.is_it_student else "N'est pas en informatique"),
        inline=False,
    )
    embed.set_footer(text=f"ID: {member.id}")

    return embed


async def process_welcome_result(member: discord.Member, result: AdeptMember):
    """
    Processes the welcome result.

    Parameters
    ----------
    `member`: discord.Member
        The new member.
    `result`: AdeptMember
        The new member's information.
    """
    guild = member.guild

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

    roles = [
        role
        for role in member.roles
        if role.id
        not in (
            configs.PROG_ROLE,
            configs.NETWORK_ROLE,
            configs.DECBAC_ROLE,
            configs.TEACHER_ROLE,
        )
    ]
    if role is not None:
        roles.append(role)

    try:
        await member.edit(nick=result.name, roles=roles, reason="Inital setup")
    except discord.Forbidden:
        await member.send(
            "Vous avez des permissions plus élevées que moi. Veuillez contacter un administrateur.\n\n"
            + "Si vous êtes un administrateur, veuillez changer vos informations."
        )

    embed = await create_welcome_embed(member, result)

    content = None
    if not result.is_it_student or result.is_teacher:
        content = f"<@&{configs.ADMIN_ROLE}> Veuillez valider la requête de {member.mention}."

    await util.say(configs.LOGS_CHANNEL, content, embed=embed)

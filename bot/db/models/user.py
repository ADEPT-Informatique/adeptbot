"""ADEPT User model."""

from bot.db.models.entity import Entity


class AdeptMember(Entity):
    """
    ADEPT Member Model.

    Attributes
    ----------
    `name` : str
        The name of the member.
    `email` : str
        The email of the member.
    `is_student` : bool
        Whether or not the member is a student.
    `is_teacher` : bool
        Whether or not the member is a teacher.
    `is_it_student` : bool
        Whether or not the member is an IT student.
    `student_id` : int
        The student id of the member.
    `program` : str
        The program of the member.
    """

    __slots__ = (
        "name",
        "email",
        "is_student",
        "is_teacher",
        "is_it_student",
        "student_id",
        "program",
    )

    def __init__(
        self,
        discord_id: int,
        name: str,
        email: str,
        is_student: bool,
        *,
        is_teacher: bool = False,
        is_it_student: bool = False,
        student_id: int = None,
        program: str = None,
        **kwargs,
    ) -> None:
        self.name = name
        self.email = email
        self.is_student = is_student

        self.is_teacher = is_teacher
        self.is_it_student = is_it_student
        self.student_id = student_id
        self.program = program

        super().__init__(discord_id, **kwargs)

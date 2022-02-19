from . import Entity
from ..services import BaseService, UserService


class WelcomeUser(Entity):
    name: str
    email: str
    is_student: bool
    is_teacher: bool
    is_it_student: bool
    student_id: int
    program: str

    def __init__(self, discord_id: int, name: str, email: str, is_student: bool, **kwargs) -> None:
        self.name = name
        self.email = email
        self.is_student = is_student

        self.is_teacher = False
        self.is_it_student = False
        self.student_id = None
        self.program = None

        super().__init__(discord_id, **kwargs)

    @property
    def service(self) -> BaseService:
        return UserService()

from . import Entity
from ..services import BaseService, UserService


class WelcomeUser(Entity):
    def __init__(self, discord_id: int, name: str, email: str, is_student: bool, student_id: int = None, program: str = None, **kwargs) -> None:
        self.name = name
        self.email = email
        self.is_student = is_student
        self.student_id = student_id
        self.program = program

        super().__init__(discord_id, **kwargs)

    @property
    def service(self) -> BaseService:
        return UserService()

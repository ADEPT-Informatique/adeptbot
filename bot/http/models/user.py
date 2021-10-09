class WelcomeUser:
    def __init__(self, name:str, is_student: bool, student_id: int = None, program: str = None) -> None:
        self.name = name
        self.is_student = is_student
        self.student_id = student_id
        self.program = program

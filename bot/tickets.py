from discord.ext import commands
from discord.ext.commands.errors import ArgumentParsingError
from enum import Enum


class TicketType(Enum):
    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, str):
            return False

        return self.value.lower() == other.lower()

    COMPLAINT = "Plainte"
    MORON = "Moron"


class TicketConverter(commands.Converter):
    async def convert(self, _, value) -> TicketType:
        match value:
            case TicketType.COMPLAINT:
                return TicketType.COMPLAINT
            case TicketType.MORON:
                return TicketType.MORON
            case _:
                raise ArgumentParsingError("Type de ticket invalid!")

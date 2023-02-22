"""Module for ticket related commands."""

from enum import Enum

from discord.ext import commands
from discord.ext.commands.errors import ArgumentParsingError


class TicketType(Enum):
    """Enum for ticket types."""

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, str):
            return False

        return self.value.lower() == other.lower()

    COMPLAINT = "Plainte"
    MORON = "Moron"


class TicketConverter(commands.Converter):
    """Converter for ticket types."""

    async def convert(self, _, value) -> TicketType:
        match value:
            case TicketType.COMPLAINT:
                return TicketType.COMPLAINT
            case TicketType.MORON:
                return TicketType.MORON
            case _:
                raise ArgumentParsingError("Type de ticket invalid!")

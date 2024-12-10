"""ReactionRole model for linking reactions to roles."""

from bot.db.models.entity import Entity


class ReactionRole(Entity):
    """
    ReactionRole model for linking reactions to roles.

    Attributes
    ----------
    `message_id` : int
        The ID of the message.
    `emoji` : str
        The emoji used for the reaction.
    `role_id` : int
        The ID of the role to assign.
    """

    __slots__ = ("message_id", "emoji", "role_id")

    def __init__(self, _id: int, message_id: int, emoji: str, role_id: int):
        super().__init__(_id)
        self.message_id = message_id
        self.emoji = emoji
        self.role_id = role_id

    def __getstate__(self):
        state = super().__getstate__()
        state.update(
            {
                "message_id": self.message_id,
                "emoji": self.emoji,
                "role_id": self.role_id,
            }
        )
        return state

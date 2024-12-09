"""Service class for ReactionRole model."""

from bot.db.models.reaction_role import ReactionRole
from bot.db.services.base_service import BaseService


class ReactionRoleService(BaseService):
    """
    Service class for ReactionRole model.

    Methods
    -------
    `add_reaction_role` : None
        Add a reaction role to the database.
    `remove_reaction_role` : None
        Remove a reaction role from the database.
    `get_reaction_role` : ReactionRole
        Get a reaction role from the database.
    """

    @property
    def collection_name(self):
        return "reaction_roles"

    async def add_reaction_role(self, message_id: int, emoji: str, role_id: int):
        """
        Add a reaction role to the database.

        Parameters
        ----------
        `message_id` : int
            The ID of the message.
        `emoji` : str
            The emoji used for the reaction.
        `role_id` : int
            The ID of the role to assign.
        """
        reaction_role = ReactionRole(None, message_id, emoji, role_id)
        self.insert_one(reaction_role.__getstate__())

    async def remove_reaction_role(self, message_id: int, emoji: str):
        """
        Remove a reaction role from the database.

        Parameters
        ----------
        `message_id` : int
            The ID of the message.
        `emoji` : str
            The emoji used for the reaction.
        """
        self.delete_one({"message_id": message_id, "emoji": emoji})

    async def get_reaction_role(self, message_id: int, emoji: str) -> ReactionRole | None:
        """
        Get a reaction role from the database.

        Parameters
        ----------
        `message_id` : int
            The ID of the message.
        `emoji` : str
            The emoji used for the reaction.

        Returns
        -------
        ReactionRole
            The reaction role.
        """
        result = self.find_one({"message_id": message_id, "emoji": emoji})
        if result:
            return ReactionRole(result["_id"], result["message_id"], result["emoji"], result["role_id"])
        return None

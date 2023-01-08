"""User service."""

from . import BaseService


class UserService(BaseService):
    """User service."""
    __COLLECTION_NAME = "users"

    def find_by_id(self, discord_id: int):
        """
        Find a user by their discord id.

        Parameters
        ----------
        - `discord_id` The discord id of the user.

        Returns
        -------
        The cursor of the user.
        """
        return self.find_one({"_id": discord_id})

    @property
    def collection_name(self):
        return self.__COLLECTION_NAME

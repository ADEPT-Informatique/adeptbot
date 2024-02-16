"""Base entity class for all models"""

from abc import abstractmethod
from datetime import datetime

from bot.db.services import BaseService


class Entity:
    """
    Base entity class for all models.

    Attributes
    ----------
    `_id` : int
        The id of the entity.
    `created_at` : datetime
        The time the entity was created.
    `updated_at` : datetime
        The time the entity was last updated.
    """

    __slots__ = ("_id", "created_at", "updated_at")

    def __init__(self, _id: int, created_at: datetime = None, updated_at: datetime = None):
        self._id = _id
        self.created_at = created_at
        self.updated_at = updated_at

        if self._id is not None:
            self._load()

    def save(self, upsert=True):
        """
        Save the entity to the database.

        Parameters
        ----------
        `upsert` : bool
            Whether to insert the entity if it doesn't exist. Defaults to True.
        """
        if self.created_at is None:
            self.created_at = datetime.utcnow()
            self.updated_at = self.created_at
        else:
            self.updated_at = datetime.utcnow()

        return self.service.update_one({"_id": self._id}, self.__getstate__(), upsert=upsert)

    def delete(self):
        """Delete the entity from the database."""
        return self.service.delete_one({"_id": self._id})

    def _load(self):
        """Load the entity from the database."""
        entity: dict = self.service.find_one({"_id": self._id})

        if entity is not None:
            self.created_at = entity.get("created_at")
            self.updated_at = entity.get("updated_at")

    def __getstate__(self):
        state = {}
        for cls in self.__class__.__mro__:
            if hasattr(cls, "__slots__"):
                for slot in cls.__slots__:
                    if hasattr(self, slot):
                        state[slot] = getattr(self, slot)
        return state

    @property
    @abstractmethod
    def service(self) -> BaseService:
        """The service for the entity."""

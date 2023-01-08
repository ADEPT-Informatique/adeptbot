"""Base entity class for all models"""

from abc import abstractmethod
from datetime import datetime

from bot.db.services import BaseService


class Entity:
    """Base entity class for all models."""

    def __init__(self, _id: int, created_at: datetime = None, updated_at: datetime = None):
        self._id = _id
        self.created_at = created_at
        self.updated_at = updated_at

        if self._id is not None:
            self._load()

    def save(self, upsert=True):
        """
        Save the entity to the database.

        :param upsert: Whether to insert the entity if it doesn't exist.
        :return: The result of the save operation.
        """
        if self.created_at is None:
            self.created_at = datetime.utcnow()
            self.updated_at = self.created_at
        else:
            self.updated_at = datetime.utcnow()

        return self.service.update_one({"_id": self._id}, {"$set": self.__dict__}, upsert=upsert)

    def delete(self):
        """Delete the entity from the database."""
        return self.service.delete_one({"_id": self._id})

    def _load(self):
        """Load the entity from the database."""
        entity: dict = self.service.find_one({"_id": self._id})

        if entity is not None:
            self.created_at = entity.get("created_at")
            self.updated_at = entity.get("updated_at")

    @property
    @abstractmethod
    def service(self) -> BaseService:
        """Return the service for the entity."""

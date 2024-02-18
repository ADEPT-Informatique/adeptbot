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

    def __init__(self, _id: int, created_at: datetime = datetime.utcnow(), updated_at: datetime = datetime.utcnow()):
        self._id = _id
        self.created_at = created_at
        self.updated_at = updated_at

    def __getstate__(self):
        state = {}
        for cls in self.__class__.__mro__:
            if hasattr(cls, "__slots__"):
                for slot in cls.__slots__:
                    if hasattr(self, slot):
                        state[slot] = getattr(self, slot)
        return state
